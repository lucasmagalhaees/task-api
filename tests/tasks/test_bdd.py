import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("features/tasks.feature")


@pytest.fixture
def ctx():
    return {}


# --- Dado ---

@given("que não existe nenhuma tarefa")
def no_tasks():
    pass


@given(parsers.parse('que existe uma tarefa com título "{title}"'))
def task_exists(client, ctx, title):
    task = client.post("/tasks", json={"title": title}).json()
    ctx["task_id"] = task["id"]


@given(parsers.parse('que existe uma tarefa concluída com título "{title}"'))
def completed_task_exists(client, ctx, title):
    task = client.post("/tasks", json={"title": title, "done": True}).json()
    ctx["task_id"] = task["id"]


# --- Quando ---

@when(parsers.parse('eu criar uma tarefa com título "{title}"'))
def create_task(client, ctx, title):
    ctx["response"] = client.post("/tasks", json={"title": title})


@when("eu tentar criar uma tarefa sem título")
def create_task_without_title(client, ctx):
    ctx["response"] = client.post("/tasks", json={})


@when("eu listar todas as tarefas")
def list_tasks(client, ctx):
    ctx["response"] = client.get("/tasks")


@when("eu buscar a tarefa pelo seu ID")
def get_task_by_id(client, ctx):
    ctx["response"] = client.get(f"/tasks/{ctx['task_id']}")


@when("eu buscar a tarefa pelo seu ID novamente")
def get_task_by_id_again(client, ctx):
    ctx["second_response"] = client.get(f"/tasks/{ctx['task_id']}")


@when(parsers.parse("eu buscar a tarefa com ID {task_id:d}"))
def get_task_by_fixed_id(client, ctx, task_id):
    ctx["response"] = client.get(f"/tasks/{task_id}")


@when("eu alternar o status da tarefa")
def toggle_task(client, ctx):
    ctx["response"] = client.put(f"/tasks/{ctx['task_id']}/toggle")


@when("eu excluir a tarefa")
def delete_task(client, ctx):
    client.delete(f"/tasks/{ctx['task_id']}")
    ctx["deleted_task_id"] = ctx["task_id"]


# --- Então ---

@then("a tarefa deve ser criada com sucesso")
def task_created(ctx):
    assert ctx["response"].status_code == 200
    ctx["task_id"] = ctx["response"].json()["id"]


@then(parsers.parse('o título da tarefa deve ser "{title}"'))
def check_title(ctx, title):
    assert ctx["response"].json()["title"] == title


@then("a tarefa deve estar pendente")
def task_is_pending(ctx):
    assert ctx["response"].json()["done"] is False


@then("a tarefa deve estar concluída")
def task_is_done(ctx):
    assert ctx["response"].json()["done"] is True


@then("devo receber um erro de validação")
def validation_error(ctx):
    assert ctx["response"].status_code == 422


@then("devo receber um erro de não encontrado")
def not_found_error(ctx):
    assert ctx["response"].status_code == 404


@then("a lista deve estar vazia")
def list_is_empty(ctx):
    assert ctx["response"].json() == []


@then(parsers.parse("a lista deve conter {count:d} tarefas"))
def list_count(ctx, count):
    assert len(ctx["response"].json()) == count


@then("a tarefa deve ser encontrada")
def task_found(ctx):
    assert ctx["response"].status_code == 200


@then("a tarefa não deve mais existir")
def task_deleted(client, ctx):
    assert client.get(f"/tasks/{ctx['deleted_task_id']}").status_code == 404


@then("ambas as respostas devem retornar a mesma tarefa")
def both_responses_same_task(ctx):
    assert ctx["response"].status_code == 200
    assert ctx["second_response"].status_code == 200
    assert ctx["response"].json()["id"] == ctx["second_response"].json()["id"]
