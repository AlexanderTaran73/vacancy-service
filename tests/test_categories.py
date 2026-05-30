import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_list_categories_empty(client: AsyncClient):
    resp = await client.get("/api/v1/categories/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_category_success(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/categories/", json={"name": "Engineering"}, headers=auth_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Engineering"
    assert "id" in data


async def test_create_category_unauthenticated(client: AsyncClient):
    resp = await client.post("/api/v1/categories/", json={"name": "Engineering"})
    assert resp.status_code == 401


async def test_create_category_duplicate(client: AsyncClient, auth_headers: dict):
    await client.post("/api/v1/categories/", json={"name": "Engineering"}, headers=auth_headers)
    resp = await client.post(
        "/api/v1/categories/", json={"name": "Engineering"}, headers=auth_headers
    )
    assert resp.status_code == 400


async def test_create_category_empty_name(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/categories/", json={"name": ""}, headers=auth_headers
    )
    assert resp.status_code == 422


async def test_get_category_by_id(client: AsyncClient, test_category: dict):
    cat_id = test_category["id"]
    resp = await client.get(f"/api/v1/categories/{cat_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == cat_id


async def test_get_category_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/categories/99999")
    assert resp.status_code == 404


async def test_list_categories_returns_all(client: AsyncClient, auth_headers: dict):
    for name in ("Dev", "Sales", "HR"):
        await client.post("/api/v1/categories/", json={"name": name}, headers=auth_headers)
    resp = await client.get("/api/v1/categories/")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_update_category(client: AsyncClient, test_category: dict, auth_headers: dict):
    cat_id = test_category["id"]
    resp = await client.put(
        f"/api/v1/categories/{cat_id}",
        json={"name": "Updated Name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"


async def test_update_category_unauthenticated(client: AsyncClient, test_category: dict):
    resp = await client.put(
        f"/api/v1/categories/{test_category['id']}", json={"name": "X"}
    )
    assert resp.status_code == 401


async def test_update_category_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/categories/99999", json={"name": "X"}, headers=auth_headers
    )
    assert resp.status_code == 404


async def test_delete_category(client: AsyncClient, test_category: dict, auth_headers: dict):
    cat_id = test_category["id"]
    resp = await client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
    assert resp.status_code == 204
    assert (await client.get(f"/api/v1/categories/{cat_id}")).status_code == 404


async def test_delete_category_unauthenticated(client: AsyncClient, test_category: dict):
    resp = await client.delete(f"/api/v1/categories/{test_category['id']}")
    assert resp.status_code == 401


async def test_delete_category_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/categories/99999", headers=auth_headers)
    assert resp.status_code == 404
