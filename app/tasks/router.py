from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from . import schemas, service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=schemas.TaskResponse)
def create_task(data: schemas.TaskCreate, db: Session = Depends(get_db)):
    return service.create_task(db, data)


@router.get("", response_model=List[schemas.TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return service.list_tasks(db)


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = service.get_task_cached(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, data: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return service.update_task(db, task, data)


@router.put("/{task_id}/toggle", response_model=schemas.TaskResponse)
def toggle_status(task_id: int, db: Session = Depends(get_db)):
    task = service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return service.toggle_status(db, task)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    service.delete_task(db, task)
    return {"message": "Task deleted"}
