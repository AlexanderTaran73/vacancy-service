"""
Роутер аутентификации.

Эндпоинты:
- POST /register    — создание учётной записи
- POST /login       — получение JWT-пары (access + refresh)
- POST /refresh     — обновление пары токенов по refresh-токену
- POST /change-password — смена пароля (требует JWT)

Логин использует форму OAuth2PasswordRequestForm для совместимости
со стандартом OAuth2 и Swagger UI (кнопка Authorize).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.schemas.token import Token, TokenRefresh
from app.schemas.user import ChangePassword, UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрирует нового пользователя. Дублирующий login → 400."""
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Аутентифицирует пользователя и выдаёт пару JWT-токенов.

    Принимает данные в формате application/x-www-form-urlencoded
    (поля: username, password) — стандарт OAuth2.
    """
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    return Token(
        access_token=create_access_token({"sub": user.login}),
        refresh_token=create_refresh_token({"sub": user.login}),
    )


@router.post("/refresh", response_model=Token)
async def refresh(data: TokenRefresh):
    """
    Обновляет пару токенов по refresh-токену.

    Refresh-токен однократно применяется и затем заменяется новым.
    Access-токен в качестве refresh принят не будет (проверка поля type).
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = decode_token(data.refresh_token)
        # Отклоняем попытку использовать access-токен вместо refresh
        if payload.get("type") != "refresh":
            raise exc
        login: str | None = payload.get("sub")
        if not login:
            raise exc
    except JWTError:
        raise exc

    return Token(
        access_token=create_access_token({"sub": login}),
        refresh_token=create_refresh_token({"sub": login}),
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Меняет пароль аутентифицированного пользователя. Требует JWT."""
    await auth_service.change_user_password(db, current_user, data)
