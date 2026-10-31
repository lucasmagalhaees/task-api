# task-manager-api

A RESTful task management API built with **FastAPI**, **SQLAlchemy**, **SQLite**, and **Redis** for caching.

## Tech Stack

- **Python** 3.12+
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — database
- **Redis** — response cache (TTL-based, per task ID)
- **uv** — package manager

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for containerized runs and E2E/load tests)

### Run Locally

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000/docs`

> Without Docker the cache falls back to an in-memory implementation.

### Run with Docker (API + Redis)

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
| `GET` | `/tasks/{id}` | Get task by ID (cached) |
| `PUT` | `/tasks/{id}` | Update a task |
| `PUT` | `/tasks/{id}/toggle` | Toggle done status |
| `DELETE` | `/tasks/{id}` | Delete a task |

`GET /tasks/{id}` reads from Redis first; on a miss it hits the database and populates the cache. Writes (update, toggle, delete) invalidate the cache entry automatically.

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
# Unit + integration + contract + BDD (with coverage)
uv run pytest tests/ -m "not e2e" --cov=. --cov-report=term-missing

# E2E tests (requires Docker running)
uv run e2e

# Load test (requires Docker running, 20 users, 30s by default)
uv run load

# Load test with custom parameters
uv run load --users 50 --time 60s
```

Coverage is enforced at **100%** on the `app/` package.

## Project Structure

```
task-manager-api/
├── app/
│   ├── main.py          # App factory, registers routers
│   ├── database.py      # SQLAlchemy engine, session, Base
│   ├── cache.py         # Cache abstraction (MemoryCache / RedisCache)
│   └── tasks/
│       ├── router.py    # HTTP routes — orchestrates only, no logic
│       ├── models.py    # SQLAlchemy ORM model
│       ├── schemas.py   # Pydantic input/output schemas
│       └── service.py   # Business logic and DB/cache access
├── specs/
│   └── tasks.yaml       # OpenAPI spec (source of truth)
├── tests/
│   ├── conftest.py      # Shared fixtures (TestClient, in-memory DB)
│   ├── test_cache.py    # Cache unit tests (Memory + Redis)
│   ├── load/
│   │   └── locustfile.py  # Locust load test (GET /tasks/{id} cache cycle)
│   └── tasks/
│       ├── features/
│       │   └── tasks.feature  # Gherkin BDD scenarios (pt)
│       ├── test_unit.py
│       ├── test_integration.py
│       ├── test_contract.py
│       ├── test_bdd.py
│       └── test_e2e.py
├── entrypoint.sh        # Docker startup (seed + uvicorn)
├── seed.py              # Populates DB with sample tasks
├── Dockerfile           # Multi-stage: test → runtime
└── docker-compose.yml   # API + Redis services
```

## Development Workflow

This project follows **Spec-Driven Development + TDD**:

1. **Spec first** — update `specs/<feature>.yaml` before any code
2. **Tests first** — write failing tests based on the spec
3. **Implement** — write the minimum code until all tests pass

See [CLAUDE.md](CLAUDE.md) for the full step-by-step workflow guide.
