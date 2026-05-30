"""CRUD-сервис для резюме с поддержкой фильтрации по статусу и категории."""

from fastapi import HTTPException, status as http_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.resume import Resume, ResumeStatus
from app.schemas.resume import ResumeCreate, ResumeUpdate


async def _check_category(db: AsyncSession, category_id: int) -> None:
    """Проверяет существование категории; 404 если не найдена."""
    if not await db.get(Category, category_id):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


async def get_all(
    db: AsyncSession,
    status_filter: ResumeStatus | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Resume]:
    """Возвращает список резюме с опциональной фильтрацией и пагинацией."""
    query = select(Resume)
    if status_filter is not None:
        query = query.where(Resume.status == status_filter)
    if category_id is not None:
        query = query.where(Resume.category_id == category_id)
    query = query.offset(skip).limit(limit).order_by(Resume.id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_one(db: AsyncSession, resume_id: int) -> Resume:
    """Возвращает резюме по id или бросает 404."""
    obj = await db.get(Resume, resume_id)
    if not obj:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
    return obj


async def create(db: AsyncSession, data: ResumeCreate) -> Resume:
    """Создаёт резюме. Проверяет существование category_id → 404 при отсутствии."""
    await _check_category(db, data.category_id)

    obj = Resume(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, resume_id: int, data: ResumeUpdate) -> Resume:
    """
    Частично обновляет резюме.

    Поддерживает обновление candidate_data (JSON), category_id и status
    по отдельности или совместно.
    """
    obj = await get_one(db, resume_id)
    changes = data.model_dump(exclude_none=True)

    if "category_id" in changes:
        await _check_category(db, changes["category_id"])

    for field, value in changes.items():
        setattr(obj, field, value)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, resume_id: int) -> None:
    """Удаляет резюме. Резюме должно существовать → иначе 404."""
    obj = await get_one(db, resume_id)
    await db.delete(obj)
    await db.commit()
