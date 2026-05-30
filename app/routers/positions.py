"""
Роутер должностей.

GET-эндпоинты публичны. Операции записи требуют JWT.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.position import PositionCreate, PositionResponse, PositionUpdate
from app.services import position as position_service

router = APIRouter()


@router.get("/", response_model=list[PositionResponse])
async def list_positions(db: AsyncSession = Depends(get_db)):
    """Возвращает все должности. Публичный эндпоинт."""
    return await position_service.get_all(db)


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(position_id: int, db: AsyncSession = Depends(get_db)):
    """Возвращает должность по id. Публичный эндпоинт."""
    return await position_service.get_one(db, position_id)


@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Создаёт должность. Требует JWT. Дубль имени → 400."""
    return await position_service.create(db, data)


@router.put("/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Обновляет имя должности. Требует JWT."""
    return await position_service.update(db, position_id, data)


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Удаляет должность. Требует JWT."""
    await position_service.delete(db, position_id)
