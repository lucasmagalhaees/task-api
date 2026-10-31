"""
Contract tests: validate that API responses conform to the schema
defined in specs/tasks.yaml.
"""
from pathlib import Path

import pytest
import yaml

SPEC_PATH = Path(__file__).parent.parent.parent / "specs" / "tasks.yaml"


@pytest.fixture(scope="module")
def spec():
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


def assert_task_response(data: dict, spec: dict):
    schema = spec["components"]["schemas"]["TaskResponse"]["properties"]
    assert set(schema.keys()) == set(data.keys()), \
        f"Fields diverge from contract: {set(data.keys()) ^ set(schema.keys())}"
    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert isinstance(data["done"], bool)


def test_contract_post_tasks(client, spec):
    response = client.post("/tasks", json={"title": "Contract"})
    assert response.status_code == 200
    assert_task_response(response.json(), spec)


def test_contract_get_tasks(client, spec):
    client.post("/tasks", json={"title": "T1"})
    client.post("/tasks", json={"title": "T2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for item in response.json():
        assert_task_response(item, spec)


def test_contract_get_task_by_id(client, spec):
    created = client.post("/tasks", json={"title": "Get"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert_task_response(response.json(), spec)


def test_contract_404_returns_detail(client, spec):
    for endpoint in ["/tasks/999", "/tasks/999/toggle"]:
        if "toggle" not in endpoint:
            response = client.get(endpoint)
        else:
            response = client.put(endpoint)
        assert response.status_code == 404
        msg = f"{endpoint} did not return 'detail' on error"
        assert "detail" in response.json(), msg


def test_contract_put_task(client, spec):
    created = client.post("/tasks", json={"title": "Old"}).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"title": "New", "done": True}
    )
    assert response.status_code == 200
    assert_task_response(response.json(), spec)


def test_contract_toggle_status(client, spec):
    created = client.post("/tasks", json={"title": "Toggle"}).json()
    response = client.put(f"/tasks/{created['id']}/toggle")
    assert response.status_code == 200
    assert_task_response(response.json(), spec)


def test_contract_delete_task(client, spec):
    created = client.post("/tasks", json={"title": "Delete"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert "message" in response.json()
