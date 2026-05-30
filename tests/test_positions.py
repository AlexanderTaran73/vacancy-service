import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_list_positions_empty(client: AsyncClient):
    resp = await client.get("/api/v1/positions/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_position_success(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/positions/", json={"name": "Backend Engineer"}, headers=auth_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Backend Engineer"
    assert "id" in data


async def test_create_position_unauthenticated(client: AsyncClient):
    resp = await client.post("/api/v1/positions/", json={"name": "Engineer"})
    assert resp.status_code == 401


async def test_create_position_duplicate(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/positions/", json={"name": "DevOps"}, headers=auth_headers
    )
    resp = await client.post(
        "/api/v1/positions/", json={"name": "DevOps"}, headers=auth_headers
    )
    assert resp.status_code == 400


async def test_create_position_empty_name(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/positions/", json={"name": ""}, headers=auth_headers
    )
    assert resp.status_code == 422


async def test_get_position_by_id(client: AsyncClient, test_position: dict):
    pos_id = test_position["id"]
    resp = await client.get(f"/api/v1/positions/{pos_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pos_id


async def test_get_position_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/positions/99999")
    assert resp.status_code == 404


async def test_update_position(client: AsyncClient, test_position: dict, auth_headers: dict):
    pos_id = test_position["id"]
    resp = await client.put(
        f"/api/v1/positions/{pos_id}",
        json={"name": "Lead Developer"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Lead Developer"


async def test_update_position_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/positions/99999", json={"name": "X"}, headers=auth_headers
    )
    assert resp.status_code == 404


async def test_delete_position(client: AsyncClient, test_position: dict, auth_headers: dict):
    pos_id = test_position["id"]
    resp = await client.delete(f"/api/v1/positions/{pos_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/positions/{pos_id}")).status_code == 404


async def test_delete_position_unauthenticated(client: AsyncClient, test_position: dict):
    resp = await client.delete(f"/api/v1/positions/{test_position['id']}")
    assert resp.status_code == 401


async def test_delete_position_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/positions/99999", headers=auth_headers)
    assert resp.status_code == 404
