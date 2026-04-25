from unittest.mock import MagicMock, patch


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# --- POST /tasks ---

def test_create_task(client):
    response = client.post("/tasks", json={"title": "Study TDD"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Study TDD"
    assert not data["done"]
    assert "id" in data


def test_create_task_with_description(client):
    response = client.post(
        "/tasks", json={"title": "With desc", "description": "Detail"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Detail"


def test_create_task_without_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


# --- GET /tasks ---

def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


# --- GET /tasks/{id} ---

def test_get_task(client):
    created = client.post("/tasks", json={"title": "Get me"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_not_found(client):
    assert client.get("/tasks/999").status_code == 404


# --- PUT /tasks/{id} ---

def test_update_task(client):
    created = client.post("/tasks", json={"title": "Old"}).json()
    response = client.put(
        f"/tasks/{created['id']}", json={"title": "New", "done": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["done"]


def test_update_task_not_found(client):
    result = client.put("/tasks/999", json={"title": "X", "done": False})
    assert result.status_code == 404


# --- PUT /tasks/{id}/toggle ---

def test_toggle_status_to_true(client):
    created = client.post("/tasks", json={"title": "Toggle"}).json()
    assert not created["done"]
    assert client.put(f"/tasks/{created['id']}/toggle").json()["done"]


def test_toggle_status_to_false(client):
    created = client.post("/tasks", json={"title": "Toggle", "done": True}).json()
    assert not client.put(f"/tasks/{created['id']}/toggle").json()["done"]


def test_toggle_status_not_found(client):
    assert client.put("/tasks/999/toggle").status_code == 404


# --- DELETE /tasks/{id} ---

def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    assert client.delete(f"/tasks/{created['id']}").status_code == 200
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    assert client.delete("/tasks/999").status_code == 404


# --- GET /tasks/{id}/consulting ---

def test_consulting_not_found(client):
    assert client.get("/tasks/999/consulting").status_code == 404


def test_consulting_no_description_returns_422(client):
    created = client.post("/tasks", json={"title": "No desc"}).json()
    assert client.get(f"/tasks/{created['id']}/consulting").status_code == 422


def test_consulting_returns_action_plan(client):
    created = client.post(
        "/tasks", json={"title": "Setup CI", "description": "Configure pipeline"}
    ).json()
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "1. Step one\n2. Step two"
    with patch("app.tasks.service._get_openai") as mock_fn:
        mock_fn.return_value.chat.completions.create.return_value = mock_resp
        response = client.get(f"/tasks/{created['id']}/consulting")
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == created["id"]
    assert data["title"] == "Setup CI"
    assert data["action_plan"] == "1. Step one\n2. Step two"


def test_consulting_cached(client):
    created = client.post(
        "/tasks", json={"title": "Cached", "description": "Some work"}
    ).json()
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "Cached plan"
    with patch("app.tasks.service._get_openai") as mock_fn:
        mock_fn.return_value.chat.completions.create.return_value = mock_resp
        client.get(f"/tasks/{created['id']}/consulting")
        response = client.get(f"/tasks/{created['id']}/consulting")
    assert response.status_code == 200
    assert mock_fn.return_value.chat.completions.create.call_count == 1
