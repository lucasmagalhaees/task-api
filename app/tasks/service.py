import os

from openai import OpenAI
from sqlalchemy.orm import Session

from app.cache import cache

from . import models, schemas

_openai: OpenAI | None = None


def _get_openai() -> OpenAI:
    global _openai
    if _openai is None:
        _openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _openai


def list_tasks(db: Session):
    return db.query(models.Task).all()


def get_task(db: Session, task_id: int) -> models.Task | None:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_task_cached(db: Session, task_id: int):
    cached = cache.get(task_id)
    if cached is not None:
        return cached
    task = get_task(db, task_id)
    if task is not None:
        cache.set(task_id, schemas.TaskResponse.model_validate(task).model_dump())
    return task


def create_task(db: Session, data: schemas.TaskCreate):
    task = models.Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: models.Task, data: schemas.TaskCreate):
    task.title = data.title
    task.description = data.description
    task.done = data.done
    db.commit()
    db.refresh(task)
    cache.delete(task.id)
    return task


def toggle_status(db: Session, task: models.Task):
    task.done = not task.done
    db.commit()
    db.refresh(task)
    cache.delete(task.id)
    return task


def delete_task(db: Session, task: models.Task):
    cache.delete(task.id)
    db.delete(task)
    db.commit()


def get_task_consulting(task: models.Task) -> schemas.ConsultingResponse:
    cache_key = f"consulting:{task.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return schemas.ConsultingResponse(**cached)

    context = f"Title: {task.title}"
    if task.description:
        context += f"\nDescription: {task.description}"

    response = _get_openai().chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a productivity assistant. "
                    "Given a task, return a concise, numbered "
                    "action plan (maximum 5 steps) "
                    "to complete it. Respond only with the action plan, no preamble."
                ),
            },
            {"role": "user", "content": context},
        ],
    )

    action_plan = response.choices[0].message.content or ""

    result = schemas.ConsultingResponse(
        task_id=task.id,
        title=task.title,
        action_plan=action_plan,
    )
    cache.set(cache_key, result.model_dump())
    return result
