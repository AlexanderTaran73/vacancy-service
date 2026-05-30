"""
Роутер вакансий. Все эндпоинты требуют JWT.

GET / поддерживает фильтрацию по статусу и категории, а также пагинацию.
Query-параметр 'status' переименован в vacancy_status, чтобы не конфликтовать
с именем модуля fastapi.status, импортированного в том же файле.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.vacancy import VacancyStatus
from app.schemas.vacancy import VacancyCreate, VacancyResponse, VacancyUpdate
from app.services import vacancy as vacancy_service

router = APIRouter()


@router.get("/", response_model=list[VacancyResponse])
async def list_vacancies(
    # alias="status" сохраняет имя query-параметра в API как ?status=...
    vacancy_status: VacancyStatus | None = Query(None, alias="status"),
    category_id: int | None = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Список вакансий с фильтрами по статусу и категории. Требует JWT."""
    return await vacancy_service.get_all(db, vacancy_status, category_id, skip, limit)


@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Возвращает вакансию по id. 404 если не найдена."""
    return await vacancy_service.get_one(db, vacancy_id)


@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    data: VacancyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Создаёт вакансию. Проверяет существование category_id и position_id."""
    return await vacancy_service.create(db, data)


@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    data: VacancyUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Обновляет вакансию (частичное обновление: можно передавать только изменяемые поля)."""
    return await vacancy_service.update(db, vacancy_id, data)


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Удаляет вакансию. 404 если не найдена."""
    await vacancy_service.delete(db, vacancy_id)
