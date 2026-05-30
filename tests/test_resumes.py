import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

CANDIDATE = {
    "name": "Ivan Ivanov",
    "email": "ivan@example.com",
    "phone": "+79001234567",
    "skills": ["Python", "FastAPI"],
    "experience_years": 3,
}


def _resume_payload(category_id: int, **overrides) -> dict:
    return {
        "candidate_data": CANDIDATE,
        "category_id": category_id,
        "status": "active",
        **overrides,
    }


async def test_list_resumes_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/resumes/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_resumes_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/resumes/")
    assert resp.status_code == 401


async def test_create_resume_success(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    resp = await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(test_category["id"]),
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "active"
    assert data["candidate_data"]["name"] == CANDIDATE["name"]
    assert "id" in data


async def test_create_resume_unauthenticated(client: AsyncClient, test_category: dict):
    resp = await client.post(
        "/api/v1/resumes/", json=_resume_payload(test_category["id"])
    )
    assert resp.status_code == 401


async def test_create_resume_invalid_category(
    client: AsyncClient, auth_headers: dict
):
    resp = await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(99999),
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_create_resume_invalid_status(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    resp = await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(test_category["id"], status="unknown_status"),
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_create_resume_missing_candidate_data(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    resp = await client.post(
        "/api/v1/resumes/",
        json={"category_id": test_category["id"], "status": "active"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


async def test_get_resume_success(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.get(f"/api/v1/resumes/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_resume_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/resumes/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_get_resume_unauthenticated(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.get(f"/api/v1/resumes/{created['id']}")
    assert resp.status_code == 401


async def test_update_resume(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.put(
        f"/api/v1/resumes/{created['id']}",
        json={"status": "under_review"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "under_review"


async def test_update_resume_candidate_data(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    new_data = {**CANDIDATE, "experience_years": 10}
    resp = await client.put(
        f"/api/v1/resumes/{created['id']}",
        json={"candidate_data": new_data},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["candidate_data"]["experience_years"] == 10


async def test_update_resume_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.put(
        "/api/v1/resumes/99999",
        json={"status": "inactive"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_update_resume_invalid_category(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.put(
        f"/api/v1/resumes/{created['id']}",
        json={"category_id": 99999},
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_delete_resume(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.delete(
        f"/api/v1/resumes/{created['id']}", headers=auth_headers
    )
    assert resp.status_code == 204
    assert (
        await client.get(f"/api/v1/resumes/{created['id']}", headers=auth_headers)
    ).status_code == 404


async def test_delete_resume_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/resumes/99999", headers=auth_headers)
    assert resp.status_code == 404


async def test_delete_resume_unauthenticated(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    created = (
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    ).json()
    resp = await client.delete(f"/api/v1/resumes/{created['id']}")
    assert resp.status_code == 401


async def test_filter_by_status(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    cat_id = test_category["id"]
    await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(cat_id, status="active"),
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(cat_id, status="inactive"),
        headers=auth_headers,
    )

    resp = await client.get(
        "/api/v1/resumes/", params={"status": "active"}, headers=auth_headers
    )
    assert all(r["status"] == "active" for r in resp.json())


async def test_filter_by_category(
    client: AsyncClient, auth_headers: dict
):
    cat1 = (
        await client.post(
            "/api/v1/categories/", json={"name": "Backend"}, headers=auth_headers
        )
    ).json()
    cat2 = (
        await client.post(
            "/api/v1/categories/", json={"name": "Frontend"}, headers=auth_headers
        )
    ).json()

    await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(cat1["id"]),
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/resumes/",
        json=_resume_payload(cat2["id"]),
        headers=auth_headers,
    )

    resp = await client.get(
        "/api/v1/resumes/",
        params={"category_id": cat1["id"]},
        headers=auth_headers,
    )
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category_id"] == cat1["id"]


async def test_resume_pagination(
    client: AsyncClient, auth_headers: dict, test_category: dict
):
    for _ in range(5):
        await client.post(
            "/api/v1/resumes/",
            json=_resume_payload(test_category["id"]),
            headers=auth_headers,
        )
    resp = await client.get(
        "/api/v1/resumes/", params={"skip": 1, "limit": 2}, headers=auth_headers
    )
    assert len(resp.json()) == 2
