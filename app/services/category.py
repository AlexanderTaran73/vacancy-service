"""CRUD-сервис для категорий вакансий и резюме."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_all(db: AsyncSession) -> list[Category]:
    """Возвращает все категории, отсортированные по id."""
    result = await db.execute(select(Category).order_by(Category.id))
    return list(result.scalars().all())


async def get_one(db: AsyncSession, category_id: int) -> Category:
    """Возвращает категорию по id или бросает 404."""
    obj = await db.get(Category, category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return obj


async def create(db: AsyncSession, data: CategoryCreate) -> Category:
    """
    Создаёт новую категорию.

    Проверяет уникальность имени: дубль → 400.
    """
    existing = await db.execute(select(Category).where(Category.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )
    obj = Category(name=data.name)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, category_id: int, data: CategoryUpdate) -> Category:
    """Обновляет имя категории. Категория должна существовать → иначе 404."""
    obj = await get_one(db, category_id)
    obj.name = data.name
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, category_id: int) -> None:
    """Удаляет категорию. Категория должна существовать → иначе 404."""
    obj = await get_one(db, category_id)
    await db.delete(obj)
    await db.commit()
