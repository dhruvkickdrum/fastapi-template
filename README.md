# FastAPI Production Template

A reusable, production-grade FastAPI boilerplate with JWT authentication, role-based access control, async PostgreSQL, structured logging, global error handling, and a full test suite.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
- [Agent Setup Files](#agent-setup-files)
- [Extending the Template](#extending-the-template)

---

## Features

| Area | What's included |
|---|---|
| **Auth** | JWT access + refresh tokens, bcrypt password hashing |
| **RBAC** | `user` / `admin` roles, reusable `require_role()` dependency |
| **Database** | Async SQLAlchemy 2.0, PostgreSQL via `asyncpg`, Alembic migrations |
| **Validation** | Pydantic v2 schemas, password-strength rules, email format checks |
| **Security** | CORS middleware, env-based secrets, no hardcoded credentials |
| **Logging** | Structured JSON logs via `python-json-logger`, request ID tracing |
| **Error handling** | Global exception handlers, standardised `ErrorResponse` shape |
| **Testing** | pytest-asyncio, in-memory SQLite, 44 tests, ≥70 % coverage enforced |
| **Docs** | Auto-generated Swagger UI at `/docs`, ReDoc at `/redoc` |
| **Docker** | `Dockerfile` + `docker-compose.yml` for local dev |

---

## Project Structure

```
fastapi-template/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── dependencies.py      # Auth dependencies & RBAC guards
│   │       ├── router.py            # Mounts all v1 sub-routers
│   │       └── endpoints/
│   │           ├── auth.py          # /auth/register, /login, /refresh
│   │           ├── users.py         # /users/me, /users/{id} (admin)
│   │           └── health.py        # /health, /health/db
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (reads .env)
│   │   ├── exceptions.py            # Typed app exceptions
│   │   ├── logging.py               # JSON structured logging setup
│   │   └── security.py              # JWT helpers, bcrypt wrappers
│   ├── db/
│   │   ├── session.py               # Async engine, session factory, get_db()
│   │   └── base_model.py            # UUID PK + created_at/updated_at mixin
│   ├── middleware/
│   │   ├── exception_handler.py     # Global FastAPI exception handlers
│   │   └── logging.py               # Per-request structured logging middleware
│   ├── models/
│   │   └── user.py                  # SQLAlchemy User model
│   ├── schemas/
│   │   ├── user.py                  # Pydantic request/response schemas
│   │   └── response.py              # Generic APIResponse[T] & ErrorResponse
│   ├── services/
│   │   ├── auth_service.py          # Login / refresh token business logic
│   │   └── user_service.py          # CRUD operations on User
│   └── main.py                      # App factory: middleware, routers, lifespan
├── alembic/                         # Migration scripts
├── tests/
│   ├── conftest.py                  # Shared fixtures (in-memory DB, test client)
│   ├── api/
│   │   ├── test_auth.py             # 13 auth endpoint tests
│   │   ├── test_users.py            # 10 user endpoint tests
│   │   └── test_health.py           # 2 health tests
│   └── unit/
│       ├── test_security.py         # 10 JWT / password unit tests
│       └── test_schemas.py          # 9 Pydantic validation unit tests
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── run.py
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Docker)

> Note: the dependency pins in `requirements.txt` are updated to install cleanly on modern Python versions, including Python 3.13 and Python 3.14 on Windows. If you are reusing an older virtual environment, recreate it before reinstalling dependencies.

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/your-org/fastapi-template.git
cd fastapi-template
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install aiosqlite             # only needed for running tests locally
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in all required values (see table below)
```

### 3. Start PostgreSQL

Using Docker Compose (recommended):

```bash
docker-compose up -d db
```

Or point `DATABASE_URL` at an existing PostgreSQL instance.

### 4. Run database migrations

```bash
alembic upgrade head
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | Async PostgreSQL URL: `postgresql+asyncpg://user:pass@host/db` |
| `SECRET_KEY` | ✅ | — | Random string ≥ 32 chars for signing JWTs |
| `ALGORITHM` | | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | `30` | Access token TTL in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | | `7` | Refresh token TTL in days |
| `ENVIRONMENT` | | `development` | `development`, `staging`, or `production` |
| `DEBUG` | | `false` | Enables SQLAlchemy query logging |
| `ALLOWED_ORIGINS` | | `http://localhost:3000` | Comma-separated CORS origins |
| `LOG_LEVEL` | | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | | `json` | `json` or `text` |
| `MIN_PASSWORD_LENGTH` | | `8` | Minimum password length |
| `BCRYPT_ROUNDS` | | `12` | bcrypt cost factor |

Generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **Note:** In `production` mode, the `/docs`, `/redoc`, and `/openapi.json` endpoints are automatically disabled.

---

## Running the Application

### Development (with auto-reload)

```bash
python run.py
```

### With Docker Compose (full stack)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

---

## Running Tests

Tests use an **in-memory SQLite database** — no PostgreSQL needed.

```bash
# Run all tests with coverage
SECRET_KEY="any-32-char-secret-for-tests-ok" \
DATABASE_URL="sqlite+aiosqlite:///:memory:" \
pytest

# Run only unit tests (faster)
pytest tests/unit/

# Run only API integration tests
pytest tests/api/

# Generate an HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

The `pytest.ini` enforces **≥ 70 % coverage** — the build will fail if this drops.

---

## API Documentation

When running in non-production mode, interactive docs are available at:

| URL | Tool |
|---|---|
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:8000/openapi.json` | Raw OpenAPI schema |

### Endpoints at a glance

```
POST   /api/v1/auth/register          Register a new user
POST   /api/v1/auth/login             Obtain access + refresh tokens
POST   /api/v1/auth/refresh           Refresh an access token

GET    /api/v1/users/me               Get own profile         [auth required]
PATCH  /api/v1/users/me               Update own profile      [auth required]
POST   /api/v1/users/me/change-password  Change password      [auth required]
DELETE /api/v1/users/me               Deactivate own account  [auth required]

GET    /api/v1/users/{id}             Get user by ID          [admin only]
POST   /api/v1/users/                 Create user with role   [admin only]

GET    /api/v1/health                 App health check
GET    /api/v1/health/db              Database connectivity
```

### Response envelope

All endpoints return a consistent envelope:

**Success:**
```json
{
  "success": true,
  "message": "OK",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error_code": "UNAUTHORIZED",
  "message": "Invalid email or password.",
  "details": null
}
```

---

## Agent Setup Files

This repository now includes lightweight collaboration docs for human and AI contributors:

| File | Purpose |
|---|---|
| `AGENTS.md` | Compatibility entry point for tools that look for the standard agent filename |
| `aagents.md` | Entry point for repo-specific agent workflow, high-value files, and handoff expectations |
| `rules.md` | Non-negotiable engineering, architecture, testing, security, and doc rules |
| `skills.md` | Reusable task playbooks for common changes such as new resources, auth updates, config changes, and migrations |

Recommended reading order:

1. `aagents.md`
2. `rules.md`
3. `skills.md`
4. `README.md`
5. `DESIGN_DOCUMENT.md`

---

## Extending the Template

### Add a new resource (e.g. `Post`)

1. **Model** — create `app/models/post.py` extending `BaseModel`
2. **Schema** — create `app/schemas/post.py` with request/response Pydantic models
3. **Service** — create `app/services/post_service.py` with business logic
4. **Router** — create `app/api/v1/endpoints/posts.py` and mount it in `app/api/v1/router.py`
5. **Migration** — run `alembic revision --autogenerate -m "add posts table" && alembic upgrade head`
6. **Tests** — add `tests/api/test_posts.py` and `tests/unit/test_post_schemas.py`

### Add a new role

In `app/api/v1/dependencies.py`, add your guard:

```python
require_moderator = require_role("moderator", "admin")
```

Then use it as a FastAPI dependency:

```python
@router.delete("/{id}", dependencies=[Depends(require_moderator)])
async def delete_post(id: uuid.UUID, db=Depends(get_db)):
    ...
```

### Switch to a different database

Update `DATABASE_URL` in `.env` to point at any SQLAlchemy-compatible async backend (e.g. `mysql+aiomysql://...`). The rest of the code is driver-agnostic.

### Enable email verification

1. Add an `email_verification_token` column to the `User` model
2. On register, generate a signed token and send it via your email provider (e.g. SendGrid, Resend)
3. Add a `GET /auth/verify-email?token=...` endpoint that sets `is_verified = True`

### Production checklist

- [ ] Change `SECRET_KEY` to a strong random value (at least 64 hex chars)
- [ ] Set `ENVIRONMENT=production` (disables Swagger UI)
- [ ] Set `BCRYPT_ROUNDS=12` or higher
- [ ] Configure `ALLOWED_ORIGINS` to your frontend domain(s) only
- [ ] Use a secrets manager (AWS Secrets Manager, HashiCorp Vault) instead of `.env`
- [ ] Add rate limiting (e.g. `slowapi`) to auth endpoints
- [ ] Set up database connection pooling appropriate for your load
- [ ] Add a reverse proxy (nginx / Caddy) with TLS termination in front of uvicorn
