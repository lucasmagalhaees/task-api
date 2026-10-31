import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

import app.tasks.service as svc
from app.database import get_db
from app.tasks.schemas import TaskCreate, TaskResponse


def test_task_create_title_required():
    with pytest.raises(ValidationError):
        TaskCreate()


def test_task_create_empty_title_invalid():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_task_create_defaults():
    t = TaskCreate(title="Do something")
    assert not t.done
    assert t.description is None


def test_task_create_full():
    t = TaskCreate(title="Do something", description="Details", done=True)
    assert t.title == "Do something"
    assert t.description == "Details"
    assert t.done


def test_task_response_fields():
    t = TaskResponse(id=1, title="Task", description=None, done=False)
    assert t.id == 1
    assert not t.done


def test_task_response_serializes_to_dict():
    t = TaskResponse(id=1, title="Task", description="Desc", done=True)
    expected = {"id": 1, "title": "Task", "description": "Desc", "done": True}
    assert t.model_dump() == expected


def test_get_db_yields_and_closes_session():
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    try:
        next(gen)
    except StopIteration:
        pass


def test_get_openai_lazy_init(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    svc._openai = None
    client1 = svc._get_openai()
    client2 = svc._get_openai()
    assert client1 is client2
    svc._openai = None
