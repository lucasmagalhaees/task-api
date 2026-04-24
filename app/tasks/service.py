from sqlalchemy.orm import Session

from app.cache import cache
from . import models, schemas


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
