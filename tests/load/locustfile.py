"""
Load tests: simulação de carga real contra o container Docker.
Requer a aplicação rodando em localhost:8001 (`uv run up`).

Execução:
    uv run load                          # headless, 20 usuários, 30s
    uv run load --users 50 --time 60s    # customizado
"""
import random

from locust import HttpUser, between, task


class TaskUser(HttpUser):
    """Simula um usuário realizando operações típicas na API de tarefas."""

    wait_time = between(0.5, 2)
    host = "http://localhost:8001"

    def on_start(self):
        self._task_ids: list[int] = []
        for i in range(3):
            resp = self.client.post("/tasks", json={"title": f"Tarefa inicial {i}"})
            if resp.status_code == 200:
                self._task_ids.append(resp.json()["id"])

    @task(10)
    def get_task_by_id(self):
        """Leitura por ID — exercita o cache."""
        if self._task_ids:
            task_id = random.choice(self._task_ids)
            self.client.get(f"/tasks/{task_id}", name="/tasks/[id]")

    @task(5)
    def list_tasks(self):
        self.client.get("/tasks")

    @task(3)
    def create_task(self):
        resp = self.client.post("/tasks", json={"title": "Tarefa de carga"})
        if resp.status_code == 200:
            self._task_ids.append(resp.json()["id"])

    @task(2)
    def toggle_task(self):
        if self._task_ids:
            task_id = random.choice(self._task_ids)
            self.client.put(f"/tasks/{task_id}/toggle", name="/tasks/[id]/toggle")

    @task(1)
    def delete_task(self):
        if self._task_ids:
            task_id = self._task_ids.pop(random.randrange(len(self._task_ids)))
            self.client.delete(f"/tasks/{task_id}", name="/tasks/[id]")
