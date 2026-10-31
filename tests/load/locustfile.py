"""
Load tests: simulação de carga real contra o container Docker.
Requer a aplicação rodando em localhost:8001 (`uv run up`).

Foco: GET /tasks/{id} — leitura por ID que passa pelo cache Redis.
Cada usuário fica N segundos batendo no mesmo ID (cache hit) e então
rotaciona para o próximo (cache miss → DB → popula cache).

Execução:
    uv run load                          # headless, 20 usuários, 30s
    uv run load --users 50 --time 60s    # customizado
"""
import time

from locust import HttpUser, between, task

CYCLE_SECONDS = 10


class TaskUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://localhost:8001"

    def on_start(self):
        self._task_ids: list[int] = []
        self._current_idx = 0
        self._rotated_at = time.monotonic()

        for i in range(5):
            resp = self.client.post("/tasks", json={"title": f"Tarefa de carga {i}"})
            if resp.status_code == 200:
                self._task_ids.append(resp.json()["id"])

    def _current_id(self) -> int | None:
        if not self._task_ids:
            return None
        if time.monotonic() - self._rotated_at >= CYCLE_SECONDS:
            self._current_idx = (self._current_idx + 1) % len(self._task_ids)
            self._rotated_at = time.monotonic()
        return self._task_ids[self._current_idx]

    @task
    def get_task_by_id(self):
        task_id = self._current_id()
        if task_id:
            self.client.get(f"/tasks/{task_id}", name="/tasks/[id]")
