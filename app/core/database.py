"""
Подключение к базе данных.

Создаёт асинхронный движок SQLAlchemy, фабрику сессий и базовый класс
для ORM-моделей. expire_on_commit=False важно для async-контекста:
без него атрибуты объекта становились бы невалидными после commit.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Асинхронный движок без пула событий (echo=False — отключает SQL-лог в prod)
engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # объекты остаются живыми после commit в async-контексте
)


class Base(DeclarativeBase):
    """Общий базовый класс для всех ORM-моделей."""


async def get_db() -> AsyncSession:  # type: ignore[return]
    """FastAPI-зависимость: открывает сессию и закрывает её после запроса."""
    async with AsyncSessionLocal() as session:
        yield session
