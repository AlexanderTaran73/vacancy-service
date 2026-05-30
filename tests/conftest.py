"""
Общие фикстуры pytest для интеграционного тестирования.

Ключевое решение: для каждого теста создаётся отдельный async-движок с NullPool.
NullPool не хранит соединения между вызовами — это исключает конфликт event loop'ов
между фикстурой и телом теста (asyncpg привязывает соединения к конкретному loop).

Переопределение get_db в _override_get_db создаёт новый движок на каждый
HTTP-запрос к тестовому приложению — соединение открывается в loop теста,
а не в loop фикстуры, и конфликтов не возникает.

Схема создаётся перед тестом и удаляется после него, обеспечивая полную
изоляцию между тестами без truncate и без shared-состояния.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # регистрирует все модели в Base.metadata
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Данные тестового пользователя используются в нескольких фикстурах
USER_PAYLOAD = {
    "first_name": "Test",
    "last_name": "User",
    "login": "testuser",
    "password": "testpass123",
}

_DB_URL = settings.TEST_DATABASE_URL


@pytest.fixture
async def client() -> AsyncClient:  # type: ignore[return]
    """
    Основная фикстура: HTTP-клиент для тестирования API.

    Жизненный цикл:
    1. Создаёт тестовую схему БД (create_all).
    2. Переопределяет зависимость get_db — каждый запрос получает
       отдельное соединение через NullPool в loop теста.
    3. Открывает AsyncClient через ASGI-транспорт (без реального HTTP).
    4. После теста очищает схему (drop_all) и освобождает движок.
    """
    engine = create_async_engine(_DB_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override_get_db():
        # Новый движок на каждый запрос гарантирует, что соединение
        # создаётся в loop теста, а не в loop фикстуры
        req_engine = create_async_engine(_DB_URL, poolclass=NullPool)
        factory = async_sessionmaker(bind=req_engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            yield session
        await req_engine.dispose()

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

    # Удаляем схему после каждого теста для полной изоляции
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Регистрирует тестового пользователя и возвращает данные профиля."""
    resp = await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def auth_headers(client: AsyncClient, registered_user: dict) -> dict:
    """Возвращает заголовки с Bearer-токеном для защищённых запросов."""
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": USER_PAYLOAD["login"], "password": USER_PAYLOAD["password"]},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_category(client: AsyncClient, auth_headers: dict) -> dict:
    """Создаёт тестовую категорию 'Development' и возвращает её данные."""
    resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Development"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def test_position(client: AsyncClient, auth_headers: dict) -> dict:
    """Создаёт тестовую должность 'Senior Developer' и возвращает её данные."""
    resp = await client.post(
        "/api/v1/positions/",
        json={"name": "Senior Developer"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()
