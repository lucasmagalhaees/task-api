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
    assert data["done"] == False
    assert "id" in data


def test_create_task_with_description(client):
    response = client.post("/tasks", json={"title": "With desc", "description": "Detail"})
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
    response = client.put(f"/tasks/{created['id']}", json={"title": "New", "done": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["done"] == True


def test_update_task_not_found(client):
    assert client.put("/tasks/999", json={"title": "X", "done": False}).status_code == 404


# --- PUT /tasks/{id}/toggle ---

def test_toggle_status_to_true(client):
    created = client.post("/tasks", json={"title": "Toggle"}).json()
    assert created["done"] == False
    assert client.put(f"/tasks/{created['id']}/toggle").json()["done"] == True


def test_toggle_status_to_false(client):
    created = client.post("/tasks", json={"title": "Toggle", "done": True}).json()
    assert client.put(f"/tasks/{created['id']}/toggle").json()["done"] == False


def test_toggle_status_not_found(client):
    assert client.put("/tasks/999/toggle").status_code == 404


# --- DELETE /tasks/{id} ---

def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    assert client.delete(f"/tasks/{created['id']}").status_code == 200
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    assert client.delete("/tasks/999").status_code == 404
