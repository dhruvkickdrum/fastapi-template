# Repository Rules

These rules apply to all changes in this FastAPI template.

## 1. Architecture Rules

- Keep route handlers thin. Validation and HTTP concerns belong in endpoints; business logic belongs in services.
- Put reusable authorization logic in `app/api/v1/dependencies.py`, not inline inside endpoints.
- Put shared security helpers in `app/core/security.py`.
- New database models should inherit the shared base model pattern already used in the repo.
- New API modules must be mounted through `app/api/v1/router.py`.

## 2. API Contract Rules

- Preserve the versioned API structure under `app/api/v1/`.
- Return the standard success and error envelopes defined in `app/schemas/response.py`.
- Raise typed application exceptions and let the global exception handlers format the response.
- Do not silently change public endpoint paths, auth requirements, or response shapes.

## 3. Security Rules

- Never hardcode secrets, tokens, passwords, or connection strings.
- Always hash passwords through the shared security helpers.
- Use the existing JWT helpers for token creation and validation.
- Keep protected routes behind the current-user dependency and role guard pattern.
- If a change affects auth or permissions, add or update tests in the same task.

## 4. Database Rules

- Use async SQLAlchemy patterns already present in the repo.
- Model changes should be paired with Alembic migration follow-up.
- Do not add raw SQL unless the ORM path is insufficient and the reason is documented.
- Keep testability in mind: changes should still work with the SQLite test setup in `tests/conftest.py`.

## 5. Configuration Rules

- New settings must be added to `app/core/config.py`.
- Any new environment variable must also be documented in `.env.example` and `README.md`.
- Production-sensitive behavior must respect `ENVIRONMENT` and existing settings conventions.

## 6. Testing Rules

- Every behavior change should have targeted test coverage.
- Endpoint changes belong in `tests/api/`.
- Validation, schema, and helper logic belong in `tests/unit/`.
- Prefer focused tests over broad incidental coverage.
- Keep the coverage floor intact.

## 7. Logging and Error Rules

- Reuse the existing structured logging setup.
- Keep exceptions explicit and predictable.
- Avoid ad hoc response formats or print-based debugging in committed code.

## 8. Documentation Rules

- Update `README.md` when setup, commands, env vars, or public behavior changes.
- Update `DESIGN_DOCUMENT.md` when the architecture or intended extension pattern changes materially.
- Keep docs aligned with the actual code, not planned behavior.

## 9. Repository Hygiene Rules

- Do not commit `.env`, local databases, logs, or coverage artifacts.
- Keep changes scoped to the task.
- Prefer small, composable additions over broad refactors unless the task requires otherwise.

