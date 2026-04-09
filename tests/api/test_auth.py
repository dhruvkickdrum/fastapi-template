"""Integration tests for /api/v1/auth endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Secure@123",
                "full_name": "New User",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["email"] == "newuser@example.com"
        assert "password" not in data["data"]
        assert "password_hash" not in data["data"]

    async def test_register_duplicate_email(self, client: AsyncClient, regular_user):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "password": "Secure@123"},
        )
        assert resp.status_code == 409
        assert resp.json()["error_code"] == "CONFLICT"

    async def test_register_weak_password(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "weak@example.com", "password": "password"},
        )
        assert resp.status_code == 422

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "Secure@123"},
        )
        assert resp.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, regular_user):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "Test@1234"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, regular_user):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "Wrong@999"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "Test@1234"},
        )
        assert resp.status_code == 401

    async def test_login_inactive_user(self, client: AsyncClient, db_session, regular_user):
        regular_user.is_active = False
        await db_session.flush()
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "Test@1234"},
        )
        assert resp.status_code == 401


class TestRefreshToken:
    async def test_refresh_success(self, client: AsyncClient, regular_user):
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "Test@1234"},
        )
        refresh_token = login.json()["data"]["refresh_token"]
        resp = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()["data"]

    async def test_refresh_invalid_token(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "bad.token.here"}
        )
        assert resp.status_code == 401
