# Skills Catalog

This file lists the common workflows for contributors working in this repository.

## Skill: Add a New Resource

Use when adding a new domain object such as `Post`, `Order`, or `Tenant`.

Touch these areas:

- `app/models/`
- `app/schemas/`
- `app/services/`
- `app/api/v1/endpoints/`
- `app/api/v1/router.py`
- `tests/api/`
- `tests/unit/`
- `alembic/versions/`

Minimum workflow:

1. Add the SQLAlchemy model.
2. Add request and response schemas.
3. Add the service methods.
4. Add versioned endpoints.
5. Register the router.
6. Add migration support.
7. Add API and unit tests.

Validation:

```bash
pytest tests/api/
pytest tests/unit/
alembic upgrade head
```

## Skill: Change Authentication or RBAC

Use when changing login, token handling, password rules, or role enforcement.

Touch these areas:

- `app/core/security.py`
- `app/api/v1/dependencies.py`
- `app/services/auth_service.py`
- `app/api/v1/endpoints/auth.py`
- `app/api/v1/endpoints/users.py`
- `tests/unit/test_security.py`
- `tests/api/test_auth.py`
- `tests/api/test_users.py`

Minimum workflow:

1. Make the security or permission change in shared logic first.
2. Update endpoint and service wiring.
3. Verify protected-route behavior and error responses.
4. Update docs if the auth contract changes.

Validation:

```bash
pytest tests/unit/test_security.py
pytest tests/api/test_auth.py
pytest tests/api/test_users.py
```

## Skill: Add or Change Configuration

Use when introducing new environment variables or runtime switches.

Touch these areas:

- `app/core/config.py`
- `.env.example`
- `README.md`
- any module that consumes the new setting

Minimum workflow:

1. Add the setting with a clear type and default behavior.
2. Wire it into the runtime code.
3. Document the variable in `.env.example` and `README.md`.
4. Add tests if the setting changes runtime behavior.

Validation:

```bash
pytest
```

## Skill: Add a Migration

Use when changing models, constraints, or persistent fields.

Touch these areas:

- `app/models/`
- `alembic/versions/`
- any affected services, schemas, and tests

Minimum workflow:

1. Update the SQLAlchemy model.
2. Generate or write the Alembic migration.
3. Verify upgrade behavior.
4. Update tests if persistence behavior changed.

Validation:

```bash
alembic upgrade head
pytest
```

## Skill: Debug a Failing Test

Use when the repo is already failing or a change introduces regressions.

Recommended order:

1. Reproduce the smallest failing test target.
2. Inspect the affected endpoint, service, or schema.
3. Fix the root cause, not the assertion.
4. Re-run the targeted test.
5. Re-run the nearest broader suite.

Validation:

```bash
pytest path/to/failing_test.py
pytest tests/unit/
pytest tests/api/
```

## Skill: Prepare a Production-Facing Change

Use when a change affects deployment, observability, or operational safety.

Check these areas:

- env vars and defaults
- auth and secret handling
- migrations
- logging behavior
- docs and runbooks

Minimum workflow:

1. Confirm local and production defaults are safe.
2. Verify docs do not expose outdated commands or settings.
3. Confirm operational changes are reflected in `README.md`.
4. Call out any manual deployment step that still exists.

