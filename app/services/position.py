"""CRUD-сервис для должностей (направлений)."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate


async def get_all(db: AsyncSession) -> list[Position]:
    """Возвращает все должности, отсортированные по id."""
    result = await db.execute(select(Position).order_by(Position.id))
    return list(result.scalars().all())


async def get_one(db: AsyncSession, position_id: int) -> Position:
    """Возвращает должность по id или бросает 404."""
    obj = await db.get(Position, position_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    return obj


async def create(db: AsyncSession, data: PositionCreate) -> Position:
    """
    Создаёт новую должность.

    Проверяет уникальность имени: дубль → 400.
    """
    existing = await db.execute(select(Position).where(Position.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position with this name already exists",
        )
    obj = Position(name=data.name)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, position_id: int, data: PositionUpdate) -> Position:
    """Обновляет имя должности. Должность должна существовать → иначе 404."""
    obj = await get_one(db, position_id)
    obj.name = data.name
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, position_id: int) -> None:
    """Удаляет должность. Должность должна существовать → иначе 404."""
    obj = await get_one(db, position_id)
    await db.delete(obj)
    await db.commit()
