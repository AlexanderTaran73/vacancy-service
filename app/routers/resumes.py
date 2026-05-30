"""
Роутер резюме. Все эндпоинты требуют JWT.

Аналогично роутеру вакансий: GET / поддерживает фильтрацию
по статусу и категории с пагинацией.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.resume import ResumeStatus
from app.models.user import User
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services import resume as resume_service

router = APIRouter()


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    resume_status: ResumeStatus | None = Query(None, alias="status"),
    category_id: int | None = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Список резюме с фильтрами по статусу и категории. Требует JWT."""
    return await resume_service.get_all(db, resume_status, category_id, skip, limit)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Возвращает резюме по id. 404 если не найдено."""
    return await resume_service.get_one(db, resume_id)


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    data: ResumeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Создаёт резюме. Проверяет существование category_id."""
    return await resume_service.create(db, data)


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: int,
    data: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Обновляет резюме (частичное обновление)."""
    return await resume_service.update(db, resume_id, data)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Удаляет резюме. 404 если не найдено."""
    await resume_service.delete(db, resume_id)
