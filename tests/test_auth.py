import pytest
from httpx import AsyncClient

from tests.conftest import USER_PAYLOAD

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["login"] == USER_PAYLOAD["login"]
    assert data["first_name"] == USER_PAYLOAD["first_name"]
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_login(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    resp = await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


async def test_register_password_too_short(client: AsyncClient):
    payload = {**USER_PAYLOAD, "password": "short"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_register_login_too_short(client: AsyncClient):
    payload = {**USER_PAYLOAD, "login": "ab"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_register_missing_fields(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={"login": "only"})
    assert resp.status_code == 422


async def test_register_custom_role(client: AsyncClient):
    payload = {**USER_PAYLOAD, "role": "hr"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    assert resp.json()["role"] == "hr"


async def test_register_invalid_role(client: AsyncClient):
    payload = {**USER_PAYLOAD, "role": "superadmin"}
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": USER_PAYLOAD["password"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_refresh_token_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": USER_PAYLOAD["password"]},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_token_invalid(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "not.a.valid.token"}
    )
    assert resp.status_code == 401


async def test_refresh_with_access_token_rejected(client: AsyncClient):
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": USER_PAYLOAD["password"]},
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": access_token}
    )
    assert resp.status_code == 401


async def test_change_password_success(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": USER_PAYLOAD["password"], "new_password": "newsecure456"},
        headers=auth_headers,
    )
    assert resp.status_code == 204

    fail = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": USER_PAYLOAD["password"]},
    )
    assert fail.status_code == 401

    ok = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": "newsecure456"},
    )
    assert ok.status_code == 200


async def test_change_password_wrong_old(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "wrongold", "new_password": "newpass999"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


async def test_change_password_unauthenticated(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "x", "new_password": "newpass999"},
    )
    assert resp.status_code == 401


async def test_change_password_new_too_short(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": USER_PAYLOAD["password"], "new_password": "short"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_protected_endpoint_with_bad_token(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "x", "new_password": "newpass999"},
        headers={"Authorization": "Bearer bad.token.here"},
    )
    assert resp.status_code == 401
