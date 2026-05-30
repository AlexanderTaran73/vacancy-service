"""
Роутер категорий.

GET-эндпоинты публичны (не требуют JWT) — удобно для заполнения
форм создания вакансий и резюме без предварительной аутентификации.
Операции записи (POST/PUT/DELETE) требуют JWT.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import category as category_service

router = APIRouter()


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Возвращает все категории. Публичный эндпоинт."""
    return await category_service.get_all(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает категорию по id. Публичный эндпоинт."""
    return await category_service.get_one(db, category_id)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Создаёт категорию. Требует JWT. Дубль имени → 400."""
    return await category_service.create(db, data)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Обновляет имя категории. Требует JWT."""
    return await category_service.update(db, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Удаляет категорию. Требует JWT."""
    await category_service.delete(db, category_id)
