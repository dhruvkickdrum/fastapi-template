"""Integration tests for /api/v1/users endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestGetMe:
    async def test_get_me_authenticated(self, client: AsyncClient, user_token):
        resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["email"] == "user@example.com"
        assert "password_hash" not in data

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/users/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert resp.status_code == 401


class TestUpdateMe:
    async def test_update_full_name(self, client: AsyncClient, user_token):
        resp = await client.patch(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"full_name": "Updated Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["full_name"] == "Updated Name"

    async def test_update_email_conflict(
        self, client: AsyncClient, user_token, admin_user
    ):
        resp = await client.patch(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"email": "admin@example.com"},
        )
        assert resp.status_code == 409


class TestChangePassword:
    async def test_change_password_success(self, client: AsyncClient, user_token):
        resp = await client.post(
            "/api/v1/users/me/change-password",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"current_password": "Test@1234", "new_password": "NewPass@99"},
        )
        assert resp.status_code == 200

    async def test_change_password_wrong_current(self, client: AsyncClient, user_token):
        resp = await client.post(
            "/api/v1/users/me/change-password",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"current_password": "WrongOld@1", "new_password": "NewPass@99"},
        )
        assert resp.status_code == 400

    async def test_change_password_weak_new(self, client: AsyncClient, user_token):
        resp = await client.post(
            "/api/v1/users/me/change-password",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"current_password": "Test@1234", "new_password": "weak"},
        )
        assert resp.status_code == 422


class TestAdminEndpoints:
    async def test_admin_get_user(
        self, client: AsyncClient, admin_token, regular_user
    ):
        resp = await client.get(
            f"/api/v1/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["email"] == "user@example.com"

    async def test_regular_user_cannot_access_admin_route(
        self, client: AsyncClient, user_token, regular_user
    ):
        resp = await client.get(
            f"/api/v1/users/{regular_user.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    async def test_admin_create_user(self, client: AsyncClient, admin_token):
        resp = await client.post(
            "/api/v1/users/?role=admin",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "email": "newadmin@example.com",
                "password": "Admin@999",
                "full_name": "New Admin",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["role"] == "admin"

    async def test_get_nonexistent_user(self, client: AsyncClient, admin_token):
        import uuid
        resp = await client.get(
            f"/api/v1/users/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404
