# task-manager-api

Task management API built with FastAPI, SQLAlchemy, SQLite, and Redis.

## Stack

- Python 3.12+, FastAPI, SQLAlchemy, SQLite, Redis, uv

## Project Structure

```
task-manager-api/
├── app/
│   ├── main.py              # App factory, registers routers
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── cache.py             # Cache abstraction: MemoryCache / RedisCache
│   └── tasks/               # Feature module
│       ├── router.py        # Controller — HTTP routes
│       ├── models.py        # Model — SQLAlchemy ORM
│       ├── schemas.py       # DTO — Pydantic schemas
│       └── service.py       # Business logic and DB/cache access
├── specs/
│   └── tasks.yaml           # OpenAPI spec (source of truth)
├── tests/
│   ├── conftest.py          # Shared fixtures (TestClient, in-memory DB, cache reset)
│   ├── test_cache.py        # Cache unit tests (MemoryCache + RedisCache + build_cache)
│   ├── load/
│   │   └── locustfile.py    # Locust load test — GET /tasks/{id} with cache cycling
│   └── tasks/               # Tests mirror the feature structure
│       ├── features/
│       │   └── tasks.feature  # Gherkin BDD scenarios (language: pt)
│       ├── test_unit.py
│       ├── test_integration.py
│       ├── test_contract.py
│       ├── test_bdd.py
│       └── test_e2e.py
├── entrypoint.sh            # Docker startup: seed.py → uvicorn
├── seed.py                  # Populates DB with realistic sample tasks
├── Dockerfile               # Multi-stage: tester stage (runs tests) → runtime stage
└── docker-compose.yml       # Services: api (port 8001) + redis (port 6379)
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
| `service.py` | Business logic, database access, cache interaction |
| `router.py` | HTTP routes — orchestrates only, no logic |

Register the router in `app/main.py`:
```python
from app.<feature>.router import router as <feature>_router
app.include_router(<feature>_router)
```

Create `tests/<feature>/` mirroring the module, with `__init__.py` and these test files:

| File | What it tests |
|---|---|
| `test_unit.py` | Pydantic schemas and pure functions, no DB or HTTP |
| `test_integration.py` | Endpoints via TestClient with in-memory database |
| `test_contract.py` | Responses validated against the YAML spec |
| `test_bdd.py` | BDD step implementations for `features/<feature>.feature` |
| `test_e2e.py` | Full flow via real HTTP against Docker |

Also create `tests/<feature>/features/<feature>.feature` with Gherkin scenarios (language: pt).

### Step 3 — Tests First (TDD)

Write the tests based on the spec. They **must fail** at this point.

### Step 4 — Implement

Write the minimum code in `models.py` → `schemas.py` → `service.py` → `router.py` until all tests pass with 100% coverage.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_PROFILE` | _(unset)_ | Set to `dev` to use RedisCache; otherwise MemoryCache is used |
| `REDIS_URL` | _(required if dev)_ | Redis connection URL, e.g. `redis://redis:6379` |
| `CACHE_TTL` | `60` | Cache TTL in seconds |

Docker Compose sets all three automatically. For local runs without Docker, leave `APP_PROFILE` unset — the app falls back to MemoryCache with no Redis dependency.

## Commands

```bash
# Run tests (unit + integration + contract + BDD)
uv run pytest tests/ -m "not e2e" -v

# Run tests with coverage (requires 100%)
uv run pytest tests/ -m "not e2e" --cov=. --cov-report=term-missing

# Run E2E tests (requires Docker running)
uv run e2e

# Run load test (requires Docker running — 20 users, 30s by default)
uv run load

# Run load test with custom parameters
uv run load --users 50 --spawn-rate 10 --time 60s

# Run locally
uv run uvicorn app.main:app --reload

# Start Docker (API on port 8001, Redis on 6379)
uv run up
```

## Ports

| Context | Port |
|---|---|
| Local (`uvicorn --reload`) | `8000` |
| Docker (`uv run up`) | `8001` |

## Build Behaviour

`uv run up` runs `docker compose build --no-cache` before starting the containers. The Dockerfile has a `tester` stage that executes the full test suite (excluding E2E) during the image build — if any test fails or coverage drops below 100%, the build fails and the container never starts.

`seed.py` runs at container startup (via `entrypoint.sh`) and populates the SQLite database with sample tasks. The test suite never calls `seed.py` — tests always start with an empty in-memory database.

## Conventions

- Error responses return `{"detail": "message"}`
- Separate schemas for input (`Create`) and output (`Response`)
- `specs/` must always reflect the current state of the API
- Tests use an isolated in-memory SQLite database per fixture
- Cache is cleared before and after each test via the `client` fixture in `conftest.py`
- `app/cache.py` selects RedisCache when `APP_PROFILE=dev`, MemoryCache otherwise
- Cache keys follow the format `task:{id}`; writes (update, toggle, delete) always invalidate the entry
- Minimum coverage: 100% of the `app/` package
- BDD scenarios are written in Portuguese (`# language: pt`) in `tests/<feature>/features/`
- Load tests live in `tests/load/locustfile.py` and are not part of the pytest suite
- `cli.py` and `seed.py` are excluded from coverage (`omit` in `pyproject.toml`) — do not write tests for them
- `entrypoint.sh` must use LF line endings (enforced via `.gitattributes`)
