"""
CRUD-сервис для вакансий с поддержкой фильтрации.

Перед созданием или обновлением вакансии выполняется проверка существования
связанных category_id и position_id через вспомогательные функции.
Это гарантирует ссылочную целостность на уровне приложения и даёт
осмысленный 404 вместо 500 от нарушения FK-ограничения БД.
"""

from fastapi import HTTPException, status as http_status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.position import Position
from app.models.vacancy import Vacancy, VacancyStatus
from app.schemas.vacancy import VacancyCreate, VacancyUpdate


async def _check_category(db: AsyncSession, category_id: int) -> None:
    """Проверяет существование категории; 404 если не найдена."""
    if not await db.get(Category, category_id):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )


async def _check_position(db: AsyncSession, position_id: int) -> None:
    """Проверяет существование должности; 404 если не найдена."""
    if not await db.get(Position, position_id):
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )


async def get_all(
    db: AsyncSession,
    status_filter: VacancyStatus | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Vacancy]:
    """
    Возвращает список вакансий с опциональной фильтрацией.

    status_filter — фильтр по статусу (open/closed).
    category_id  — фильтр по категории.
    skip/limit   — пагинация.
    """
    query = select(Vacancy)
    if status_filter is not None:
        query = query.where(Vacancy.status == status_filter)
    if category_id is not None:
        query = query.where(Vacancy.category_id == category_id)
    query = query.offset(skip).limit(limit).order_by(Vacancy.id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_one(db: AsyncSession, vacancy_id: int) -> Vacancy:
    """Возвращает вакансию по id или бросает 404."""
    obj = await db.get(Vacancy, vacancy_id)
    if not obj:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found",
        )
    return obj


async def create(db: AsyncSession, data: VacancyCreate) -> Vacancy:
    """
    Создаёт вакансию.

    Перед сохранением проверяет, что category_id и position_id существуют.
    """
    await _check_category(db, data.category_id)
    await _check_position(db, data.position_id)

    obj = Vacancy(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, vacancy_id: int, data: VacancyUpdate) -> Vacancy:
    """
    Частично обновляет вакансию (PATCH-семантика через PUT).

    exclude_none=True позволяет передавать только изменяемые поля.
    FK-поля проверяются так же, как при создании.
    """
    obj = await get_one(db, vacancy_id)
    changes = data.model_dump(exclude_none=True)

    if "category_id" in changes:
        await _check_category(db, changes["category_id"])
    if "position_id" in changes:
        await _check_position(db, changes["position_id"])

    for field, value in changes.items():
        setattr(obj, field, value)

    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, vacancy_id: int) -> None:
    """Удаляет вакансию. Вакансия должна существовать → иначе 404."""
    obj = await get_one(db, vacancy_id)
    await db.delete(obj)
    await db.commit()
