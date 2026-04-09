"""Tests for health endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


async def test_db_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health/db")
    assert resp.status_code == 200
    assert resp.json()["data"]["database"] == "connected"
