import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


def _vacancy_payload(category_id: int, position_id: int, **overrides) -> dict:
    return {
        "title": "Python Developer",
        "description": "We need a skilled Python dev.",
        "position_id": position_id,
        "category_id": category_id,
        "status": "open",
        **overrides,
    }


async def test_list_vacancies_empty(
    client: AsyncClient, auth_headers: dict,
    test_category: dict, test_position: dict,
):
    resp = await client.get("/api/v1/vacancies/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_vacancies_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/vacancies/")
    assert resp.status_code == 401


async def test_create_vacancy_success(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    payload = _vacancy_payload(test_category["id"], test_position["id"])
    resp = await client.post("/api/v1/vacancies/", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "open"
    assert "id" in data


async def test_create_vacancy_unauthenticated(
    client: AsyncClient, test_category: dict, test_position: dict
):
    payload = _vacancy_payload(test_category["id"], test_position["id"])
    resp = await client.post("/api/v1/vacancies/", json=payload)
    assert resp.status_code == 401


async def test_create_vacancy_invalid_category(
    client: AsyncClient, auth_headers: dict, test_position: dict
):
    payload = _vacancy_payload(99999, test_position["id"])
    resp = await client.post("/api/v1/vacancies/", json=payload, headers=auth_headers)
    assert resp.status_code == 404


async def test_create_vacancy_invalid_position(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    payload = _vacancy_payload(test_category["id"], 99999)
    resp = await client.post("/api/v1/vacancies/", json=payload, headers=auth_headers)
    assert resp.status_code == 404


async def test_create_vacancy_missing_title(
    client: AsyncClient, auth_headers: dict, test_category: dict, test_position: dict
):
    payload = _vacancy_payload(test_category["id"], test_position["id"])
    payload.pop("title")
    resp = await client.post("/api/v1/vacancies/", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_vacancy_invalid_status(
    client: AsyncClient, auth_headers: dict, test_category: dict, test_position: dict
):
    payload = _vacancy_payload(test_category["id"], test_position["id"], status="unknown")
    resp = await client.post("/api/v1/vacancies/", json=payload, headers=auth_headers)
    assert resp.status_code == 422


async def test_get_vacancy_success(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    created = (
        await client.post(
            "/api/v1/vacancies/",
            json=_vacancy_payload(test_category["id"], test_position["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.get(f"/api/v1/vacancies/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_vacancy_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/vacancies/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_update_vacancy(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    created = (
        await client.post(
            "/api/v1/vacancies/",
            json=_vacancy_payload(test_category["id"], test_position["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.put(
        f"/api/v1/vacancies/{created['id']}",
        json={"title": "Senior Python Dev", "status": "closed"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Senior Python Dev"
    assert data["status"] == "closed"


async def test_update_vacancy_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/vacancies/99999",
        json={"title": "X"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_update_vacancy_invalid_category(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    created = (
        await client.post(
            "/api/v1/vacancies/",
            json=_vacancy_payload(test_category["id"], test_position["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.put(
        f"/api/v1/vacancies/{created['id']}",
        json={"category_id": 99999},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_delete_vacancy(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    created = (
        await client.post(
            "/api/v1/vacancies/",
            json=_vacancy_payload(test_category["id"], test_position["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.delete(
        f"/api/v1/vacancies/{created['id']}", headers=auth_headers
    )
    assert resp.status_code == 204
    assert (
        await client.get(f"/api/v1/vacancies/{created['id']}", headers=auth_headers)
    ).status_code == 404


async def test_delete_vacancy_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/vacancies/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_filter_by_status(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    cat_id, pos_id = test_category["id"], test_position["id"]
    await client.post(
        "/api/v1/vacancies/",
        json=_vacancy_payload(cat_id, pos_id, status="open"),
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/vacancies/",
        json=_vacancy_payload(cat_id, pos_id, status="closed", title="Old Role"),
        headers=auth_headers,
    )

    open_resp = await client.get(
        "/api/v1/vacancies/", params={"status": "open"}, headers=auth_headers
    )
    assert all(v["status"] == "open" for v in open_resp.json())

    closed_resp = await client.get(
        "/api/v1/vacancies/", params={"status": "closed"}, headers=auth_headers
    )
    assert all(v["status"] == "closed" for v in closed_resp.json())


async def test_filter_by_category(
    client: AsyncClient,
    auth_headers: dict,
    test_position: dict,
    auth_headers_cat2: dict = None,
):
    cat1 = (
        await client.post(
            "/api/v1/categories/", json={"name": "Dev"}, headers=auth_headers
        )
    ).json()
    cat2 = (
        await client.post(
            "/api/v1/categories/", json={"name": "Design"}, headers=auth_headers
        )
    ).json()
    pos_id = test_position["id"]
    await client.post(
        "/api/v1/vacancies/",
        json=_vacancy_payload(cat1["id"], pos_id, title="Dev Job"),
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/vacancies/",
        json=_vacancy_payload(cat2["id"], pos_id, title="Design Job"),
        headers=auth_headers,
    )

    resp = await client.get(
        "/api/v1/vacancies/",
        params={"category_id": cat1["id"]},
        headers=auth_headers,
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category_id"] == cat1["id"]


async def test_pagination(
    client: AsyncClient,
    auth_headers: dict,
    test_category: dict,
    test_position: dict,
):
    cat_id, pos_id = test_category["id"], test_position["id"]
    for i in range(5):
        await client.post(
            "/api/v1/vacancies/",
            json=_vacancy_payload(cat_id, pos_id, title=f"Job {i}"),
            headers=auth_headers,
        )
    resp = await client.get(
        "/api/v1/vacancies/", params={"skip": 2, "limit": 2}, headers=auth_headers
    )
    assert len(resp.json()) == 2
