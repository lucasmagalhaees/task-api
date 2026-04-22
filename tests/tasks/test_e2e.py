"""
E2E tests: real HTTP requests against the Docker container.
Requires the container running at localhost:8001 (`uv run up`).
Automatically skipped if the server is not reachable.
"""
import pytest
import httpx

BASE_URL = "http://localhost:8001"


@pytest.fixture(scope="module", autouse=True)
def check_server():
    try:
        httpx.get(BASE_URL, timeout=2)
    except (httpx.ConnectError, httpx.ConnectTimeout):
        pytest.skip("Docker is not running at localhost:8001")


@pytest.mark.e2e
def test_e2e_home():
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.e2e
def test_e2e_full_flow():
    response = httpx.post(f"{BASE_URL}/tasks", json={"title": "E2E Task"})
    assert response.status_code == 200
    task_id = response.json()["id"]
    assert response.json()["done"] == False

    try:
        response = httpx.get(f"{BASE_URL}/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "E2E Task"

        response = httpx.put(f"{BASE_URL}/tasks/{task_id}/toggle")
        assert response.status_code == 200
        assert response.json()["done"] == True

        response = httpx.put(f"{BASE_URL}/tasks/{task_id}/toggle")
        assert response.status_code == 200
        assert response.json()["done"] == False

        response = httpx.put(
            f"{BASE_URL}/tasks/{task_id}",
            json={"title": "E2E Updated", "done": True},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "E2E Updated"

    finally:
        httpx.delete(f"{BASE_URL}/tasks/{task_id}")

    assert httpx.get(f"{BASE_URL}/tasks/{task_id}").status_code == 404


@pytest.mark.e2e
def test_e2e_task_not_found():
    assert httpx.get(f"{BASE_URL}/tasks/999999").status_code == 404
    assert httpx.put(f"{BASE_URL}/tasks/999999/toggle").status_code == 404
    assert httpx.delete(f"{BASE_URL}/tasks/999999").status_code == 404
