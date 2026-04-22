# task-manager-api

A RESTful task management API built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

## Tech Stack

- **Python** 3.12+
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **uv** — package manager

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for containerized runs)

### Run Locally

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000/docs`

### Run with Docker

```bash
uv run up
```

API available at `http://localhost:8001/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/tasks` | List all tasks |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{id}` | Get a task by ID |
| `PUT` | `/tasks/{id}` | Update a task |
| `PUT` | `/tasks/{id}/toggle` | Toggle done status |
| `DELETE` | `/tasks/{id}` | Delete a task |

### Example

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'

# Toggle done status
curl -X PUT http://localhost:8000/tasks/1/toggle
```

## Running Tests

```bash
# Unit + integration + contract tests (with coverage)
uv run pytest tests/ -m "not e2e" --cov=. --cov-report=term-missing

# E2E tests (requires Docker running)
uv run e2e
```

Coverage is enforced at **100%** on the `app/` package.

## Project Structure

```
task-manager-api/
├── app/
│   ├── main.py          # App factory
│   ├── database.py      # DB engine and session
│   └── tasks/
│       ├── router.py    # HTTP routes
│       ├── models.py    # ORM models
│       ├── schemas.py   # Pydantic schemas
│       └── service.py   # Business logic
├── specs/
│   └── tasks.yaml       # OpenAPI spec (source of truth)
├── tests/
│   └── tasks/
│       ├── test_unit.py
│       ├── test_integration.py
│       ├── test_contract.py
│       └── test_e2e.py
├── Dockerfile
└── docker-compose.yml
```

## Development Workflow

This project follows **Spec-Driven Development + TDD**:

1. **Spec first** — update `specs/<feature>.yaml` before any code
2. **Tests first** — write failing tests based on the spec
3. **Implement** — write the minimum code until all tests pass

See [CLAUDE.md](CLAUDE.md) for the full workflow guide.
