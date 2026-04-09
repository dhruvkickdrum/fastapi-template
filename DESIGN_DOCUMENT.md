# FastAPI Template Design Document

## 1. Purpose

This repository is a reusable FastAPI starter template for building secure, maintainable, production-oriented APIs. It is intended to give future projects a strong default foundation instead of rebuilding common backend concerns from scratch.

The template focuses on:

- authentication and authorization
- async database access
- validation and security
- consistent error handling
- structured logging
- testing and extensibility

## 2. Project Objective

Build a production-ready FastAPI boilerplate that any developer can clone and extend for real API projects. The template should be:

- scalable
- secure
- cleanly structured
- easy to extend
- testable
- deployment-friendly

## 3. Scope

### In Scope

- user registration with email and password
- login with JWT token generation
- password hashing
- protected routes
- role-based access control
- PostgreSQL integration with async SQLAlchemy
- reusable base model with timestamps
- Pydantic request and response validation
- CORS and environment-based configuration
- global exception handling
- structured logging
- pytest-based test foundation
- Swagger/OpenAPI documentation
- developer onboarding documentation

### Out of Scope

- domain-specific business modules
- frontend application
- OAuth/social login
- email delivery provider integration
- rate limiting infrastructure
- background job system
- distributed tracing platform

## 4. Current Repository Status

The repository already implements most of the core template features.

### Implemented

- FastAPI app factory and versioned router structure
- JWT-based authentication with access and refresh tokens
- bcrypt password hashing and verification
- role-based authorization using reusable dependencies
- async SQLAlchemy session management
- `User` model with `id`, `email`, `password_hash`, `full_name`, `role`, `is_active`, `is_verified`
- reusable base model with `created_at` and `updated_at`
- Pydantic schemas for auth, user payloads, and response envelopes
- global exception handlers with standardized error responses
- structured request logging with request IDs
- health endpoints
- test suite layout for API and unit tests
- Dockerfile and docker-compose setup
- `.env.example` for configuration

### Still Needed or Recommended

- actual Alembic migration files under `alembic/versions/`
- refresh-token rotation or revocation strategy
- rate limiting for auth endpoints
- stronger role validation using enum values instead of free-form strings
- CI pipeline for tests and coverage enforcement
- email verification workflow if needed by future projects
- production secrets manager integration
- optional observability additions such as metrics and tracing

## 5. High-Level Architecture

The project follows a layered backend structure:

1. API layer
   Exposes HTTP endpoints, validates request bodies, and returns standardized responses.

2. Dependency layer
   Handles current-user extraction, bearer token parsing, and RBAC guards.

3. Service layer
   Contains business logic for authentication and user operations.

4. Persistence layer
   Defines SQLAlchemy models, base model behavior, and database session lifecycle.

5. Core infrastructure layer
   Centralizes configuration, security helpers, exceptions, and logging setup.

6. Middleware layer
   Handles request logging and exception-to-response normalization.

7. Test layer
   Verifies schemas, security utilities, and API behavior.

## 6. Key Modules

### Application Entry

- `app/main.py`
  Creates the FastAPI app, registers middleware, exception handlers, routers, and lifecycle hooks.

### Configuration

- `app/core/config.py`
  Loads environment variables using Pydantic Settings. This is the single source of truth for runtime configuration.

### Security

- `app/core/security.py`
  Handles password hashing, password verification, JWT creation, and JWT decoding.

### Database

- `app/db/session.py`
  Creates the async SQLAlchemy engine and provides `get_db()` for session lifecycle management.

- `app/db/base_model.py`
  Defines the common UUID primary key and timestamp fields for all models.

### Models

- `app/models/user.py`
  Defines the user table and user-related flags.

### API

- `app/api/v1/endpoints/auth.py`
  Registration, login, and token refresh endpoints.

- `app/api/v1/endpoints/users.py`
  Current-user profile operations and admin-only user operations.

- `app/api/v1/endpoints/health.py`
  App and database health checks.

### Services

- `app/services/user_service.py`
  User creation, lookup, update, password change, and deactivation logic.

- `app/services/auth_service.py`
  Login and refresh flows.

### Response and Error Standardization

- `app/schemas/response.py`
  Common success and error envelope structures.

- `app/core/exceptions.py`
  Typed application exceptions.

- `app/middleware/exception_handler.py`
  Maps exceptions to standardized API responses.

### Logging

- `app/core/logging.py`
  Configures text or JSON logging.

- `app/middleware/logging.py`
  Logs requests and responses and injects `X-Request-ID`.

## 7. Core Data Model

### User

Primary fields:

- `id`
- `email`
- `full_name`
- `password_hash`
- `role`
- `is_active`
- `is_verified`
- `created_at`
- `updated_at`

### Base Model Pattern

Every future model should inherit the base model so the project gets:

- UUID primary key
- audit timestamps
- uniform modeling conventions

## 8. Main Functionalities

### Authentication

- register user
- login user
- issue access token
- issue refresh token
- validate access token on protected routes

### Authorization

- enforce authentication with bearer token
- enforce role-based access for admin routes
- support future role extension through dependency factories

### User Management

- read own profile
- update own profile
- change own password
- deactivate own account
- admin fetch by user ID
- admin create users with elevated role

### Platform and Operations

- health check
- database connectivity check
- structured logs
- standardized errors
- generated API docs

## 9. Algorithms and Core Mechanisms

This project does not rely on complex academic algorithms. The important logic is security and request-processing flow. The main mechanisms are below.

### 9.1 Password Strength Validation

Used in request schemas for registration and password change.

Validation rules:

- minimum length
- at least one uppercase letter
- at least one lowercase letter
- at least one digit
- at least one special character

Purpose:

- reject weak credentials before storage
- provide consistent server-side validation even if clients do their own checks

### 9.2 Password Hashing Algorithm

Current choice:

- bcrypt via Passlib

Flow:

1. accept plain password
2. hash using configured bcrypt rounds
3. store only the hash
4. verify future logins by comparing plain password against stored hash

Purpose:

- prevent plain-text password storage
- make credential theft materially harder

### 9.3 JWT Token Generation Algorithm

Current choice:

- signed JWT using `SECRET_KEY` and configured algorithm

Claims used:

- `sub` for subject identity
- `type` to distinguish access and refresh tokens
- `role` for authorization decisions on access tokens
- `iat` for issued time
- `exp` for expiration

Flow:

1. authenticate the user
2. create access token with short TTL
3. create refresh token with longer TTL
4. return both to the client

### 9.4 Authorization and RBAC Flow

Mechanism:

- bearer token extraction
- JWT decoding
- user lookup from database
- active-user check
- role membership check

RBAC algorithm:

1. read `Authorization: Bearer <token>`
2. decode token
3. reject if invalid or expired
4. reject if token type is not `access`
5. fetch user by `sub`
6. reject if user is inactive or missing
7. compare `user.role` against allowed roles
8. allow or deny request

### 9.5 Database Session Lifecycle

The repository uses one async session per request through dependency injection.

Flow:

1. open async session
2. yield session to endpoint or service
3. commit on success
4. rollback on error
5. close session

Purpose:

- keeps transaction handling consistent
- prevents leaked sessions
- simplifies service implementation

### 9.6 Request Logging Flow

Flow:

1. generate a request ID
2. log request start metadata
3. execute downstream request
4. measure duration
5. log response metadata
6. return `X-Request-ID` header

Purpose:

- request traceability
- easier debugging and support
- structured logs for production pipelines

### 9.7 Exception Normalization

Flow:

1. application code raises typed exception
2. global handler maps it to status code and error code
3. API returns standardized error JSON

Purpose:

- makes client integration predictable
- reduces duplicated try/except blocks
- keeps error behavior consistent across endpoints

## 10. API Surface

### Auth Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### User Endpoints

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/change-password`
- `DELETE /api/v1/users/me`
- `GET /api/v1/users/{user_id}` for admin
- `POST /api/v1/users/` for admin

### Health Endpoints

- `GET /api/v1/health`
- `GET /api/v1/health/db`

## 11. Non-Functional Requirements

### Security

- no hardcoded secrets
- password hashes only
- JWT expiration enforced
- CORS configured from environment
- server-side validation on all inputs

### Scalability

- modular router and service organization
- async database access
- connection pooling for PostgreSQL
- versioned API structure

### Maintainability

- clear separation of concerns
- standardized response format
- centralized configuration
- typed exception system

### Testability

- pytest foundation
- API tests
- unit tests
- coverage threshold configured

## 12. Build and Implementation Steps

Recommended implementation order for this template:

1. Create project structure and app factory.
2. Add configuration management with `.env` support.
3. Add database engine, base model, and session lifecycle.
4. Define `User` model and schema contracts.
5. Implement password hashing and JWT helpers.
6. Implement user service and auth service.
7. Add auth endpoints and protected route dependencies.
8. Add RBAC guards and admin-only endpoints.
9. Add global exception handling and standardized responses.
10. Add structured logging middleware.
11. Add health endpoints.
12. Add tests for schemas, security, and auth/user APIs.
13. Add Alembic migrations.
14. Add Docker and developer onboarding docs.
15. Add production hardening features such as rate limiting and token revocation.

## 13. Suggested Extension Pattern

When adding a new domain module such as `Post`, `Order`, or `Tenant`, use the same pattern:

1. add SQLAlchemy model
2. add Pydantic schemas
3. add service layer
4. add API endpoints
5. add router registration
6. add migration
7. add API and unit tests

This keeps new modules aligned with the existing architecture.

## 14. Recommended Production Hardening Backlog

These are the next improvements that would make the template stronger for real deployment:

### High Priority

- add Alembic migration scripts for the existing schema
- validate role input with an enum
- add rate limiting on `/auth/login` and `/auth/register`
- add refresh token rotation or blacklist support
- enforce stronger production secret management

### Medium Priority

- add user listing endpoint with pagination for admin operations
- add audit logging for security-sensitive actions
- add CI workflow for linting, tests, and coverage
- add observability metrics

### Optional Future Features

- email verification
- password reset flow
- account lockout after repeated failed logins
- multi-tenant support
- OAuth providers

## 15. Risks and Design Considerations

### Token Revocation Gap

Stateless JWT is simple, but logout and forced invalidation are limited unless refresh tokens are stored, rotated, or blacklisted.

### Role Drift

Using plain strings for role values is flexible, but weakly controlled. Enums reduce accidental misuse.

### Migration Readiness

Alembic is configured, but the repository still needs real migration files before calling the template production-ready.

### Environment Discipline

The template is only secure if deployment uses proper secrets, restricted CORS origins, and production-grade TLS and proxy setup.

## 16. Acceptance Checklist

The template should be considered complete when all of the following are true:

- auth flow works end to end
- protected routes reject unauthorized access
- admin-only routes enforce role checks
- database models and sessions work with PostgreSQL
- migrations exist and apply cleanly
- validation errors use a consistent format
- logs are structured and useful in production
- test coverage stays above target threshold
- README and environment setup are clear for new developers

## 17. Summary

This repository already provides the backbone of a strong FastAPI starter template. The core architecture, security flow, validation, error handling, and testing structure are in place. The main remaining work is hardening and operational maturity: migrations, rate limiting, token lifecycle improvements, CI, and production deployment discipline.
