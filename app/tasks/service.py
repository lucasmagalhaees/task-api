from sqlalchemy.orm import Session
from . import models, schemas


def list_tasks(db: Session):
    return db.query(models.Task).all()


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


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
    return task


def toggle_status(db: Session, task: models.Task):
    task.done = not task.done
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task):
    db.delete(task)
    db.commit()
