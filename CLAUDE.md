# task-manager-api

Task management API built with FastAPI, SQLAlchemy, and SQLite.

## Stack

- Python 3.12+, FastAPI, SQLAlchemy, SQLite, uv

## Project Structure

```
task-manager-api/
├── app/
│   ├── main.py              # App factory, registers routers
│   ├── database.py          # SQLAlchemy engine, session, Base
│   └── tasks/               # Feature module
│       ├── router.py        # Controller — HTTP routes
│       ├── models.py        # Model — SQLAlchemy ORM
│       ├── schemas.py       # DTO — Pydantic schemas
│       └── service.py       # Business logic
├── specs/
│   └── tasks.yaml           # OpenAPI spec (source of truth)
├── tests/
│   └── tasks/               # Tests mirror the feature structure
│       ├── test_unit.py
│       ├── test_integration.py
│       ├── test_contract.py
│       └── test_e2e.py
├── Dockerfile
└── docker-compose.yml
```

## Development Workflow: Spec-Driven + TDD

Every new feature or change must follow this order. **Never skip steps.**

### Step 1 — Spec

Create or update the contract in `specs/<feature>.yaml` before writing any code.
The spec is the source of truth: it defines endpoints, payloads, status codes, and response schemas.

### Step 2 — Feature Structure

Create the module at `app/<feature>/` with exactly these four files:

| File | Responsibility |
|---|---|
| `models.py` | Database tables (SQLAlchemy ORM) |
| `schemas.py` | Input/output contracts (Pydantic) |
| `service.py` | Business logic and database access |
| `router.py` | HTTP routes — orchestrates only, no logic |

Register the router in `app/main.py`:
```python
from app.<feature>.router import router as <feature>_router
app.include_router(<feature>_router)
```

Create `tests/<feature>/` mirroring the module, with `__init__.py` and four test files:

| File | What it tests |
|---|---|
| `test_unit.py` | Pydantic schemas and pure functions, no DB or HTTP |
| `test_integration.py` | Endpoints via TestClient with in-memory database |
| `test_contract.py` | Responses validated against the YAML spec |
| `test_e2e.py` | Full flow via real HTTP against Docker |

### Step 3 — Tests First (TDD)

Write the tests based on the spec. They **must fail** at this point.

### Step 4 — Implement

Write the minimum code in `models.py` → `schemas.py` → `service.py` → `router.py` until all tests pass with 100% coverage.

## Commands

```bash
# Run tests (unit + integration + contract)
uv run pytest tests/ -m "not e2e" -v

# Run tests with coverage (requires 100%)
uv run pytest tests/ -m "not e2e" --cov=. --cov-report=term-missing

# Run E2E tests (requires Docker running)
uv run e2e

# Run locally
uv run uvicorn app.main:app --reload

# Start Docker (port 8001)
uv run up
```

## Conventions

- Error responses return `{"detail": "message"}`
- Separate schemas for input (`Create`) and output (`Response`)
- `specs/` must always reflect the current state of the API
- Tests use an isolated in-memory SQLite database per fixture
- Minimum coverage: 100% of the `app/` package
