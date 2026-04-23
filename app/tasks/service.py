import time
from sqlalchemy.orm import Session
from . import models, schemas

_CACHE_TTL = 60
_task_cache: dict[int, tuple[models.Task, float]] = {}


def list_tasks(db: Session):
    return db.query(models.Task).all()


def get_task(db: Session, task_id: int):
    entry = _task_cache.get(task_id)
    if entry and time.monotonic() - entry[1] < _CACHE_TTL:
        return entry[0]
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is not None:
        _task_cache[task_id] = (task, time.monotonic())
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
    _task_cache.pop(task.id, None)
    return task


def toggle_status(db: Session, task: models.Task):
    task.done = not task.done
    db.commit()
    db.refresh(task)
    _task_cache.pop(task.id, None)
    return task


def delete_task(db: Session, task: models.Task):
    _task_cache.pop(task.id, None)
    db.delete(task)
    db.commit()
