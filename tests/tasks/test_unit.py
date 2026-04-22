import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.tasks.schemas import TaskCreate, TaskResponse
from app.database import get_db


def test_task_create_title_required():
    with pytest.raises(ValidationError):
        TaskCreate()


def test_task_create_empty_title_invalid():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_create_defaults():
    t = TaskCreate(title="Do something")
    assert t.done == False
    assert t.description is None


def test_task_create_full():
    t = TaskCreate(title="Do something", description="Details", done=True)
    assert t.title == "Do something"
    assert t.description == "Details"
    assert t.done == True


def test_task_response_fields():
    t = TaskResponse(id=1, title="Task", description=None, done=False)
    assert t.id == 1
    assert t.done == False


def test_task_response_serializes_to_dict():
    t = TaskResponse(id=1, title="Task", description="Desc", done=True)
    assert t.model_dump() == {"id": 1, "title": "Task", "description": "Desc", "done": True}


def test_get_db_yields_and_closes_session():
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    try:
        next(gen)
    except StopIteration:
        pass
