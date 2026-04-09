# Agent Setup

This repository includes a lightweight agent workflow for making safe, repeatable changes to the FastAPI template.

## Purpose

Use this file as the entry point for any human or AI contributor that needs to:

- understand the repository quickly
- make changes without breaking architectural boundaries
- know which rules and task playbooks to follow

Related files:

- `rules.md`: repository constraints and engineering rules
- `skills.md`: common task playbooks for this codebase
- `README.md`: setup, runtime, and developer commands
- `DESIGN_DOCUMENT.md`: architecture and design intent

## Repository Summary

This codebase is a reusable FastAPI backend template with:

- JWT authentication and refresh tokens
- role-based access control
- async SQLAlchemy and PostgreSQL support
- structured logging and global exception handling
- pytest coverage for API and unit behavior

## Working Model

When changing the codebase, follow this order:

1. Read the relevant sections in `README.md` and `DESIGN_DOCUMENT.md`.
2. Inspect the endpoint, service, schema, and model files involved in the change.
3. Keep business logic in services, not in route handlers.
4. Reuse shared utilities in `app/core/`, `app/db/`, and `app/api/v1/dependencies.py`.
5. Add or update tests for behavioral changes.
6. Run targeted validation before closing the task.
7. Update documentation if APIs, config, or workflows changed.

## High-Value Areas

- `app/main.py`: app factory, middleware, router registration
- `app/api/v1/endpoints/`: HTTP handlers
- `app/api/v1/dependencies.py`: auth and role guards
- `app/services/`: business logic
- `app/models/`: SQLAlchemy models
- `app/schemas/`: request and response contracts
- `app/core/`: config, security, exceptions, logging
- `tests/api/`: endpoint behavior
- `tests/unit/`: schema and security behavior

## Default Validation Commands

Use the smallest command set that proves the change:

```bash
pytest tests/unit/
pytest tests/api/
pytest
alembic upgrade head
python run.py
```

## Handoff Checklist

Before handing work off, confirm:

- affected behavior is covered by tests
- config changes are mirrored in `.env.example`
- new models or schema changes include migration follow-up if needed
- docs match the implemented behavior
- no secrets or machine-specific artifacts were added

