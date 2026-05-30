"""
Общие FastAPI-зависимости.

get_current_user — защитная зависимость для эндпоинтов, требующих аутентификации.
Проверяет JWT, тип токена (только 'access') и наличие пользователя в БД.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# tokenUrl указывает Swagger UI на эндпоинт для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Валидирует Bearer-токен и возвращает текущего пользователя.

    Порядок проверок:
    1. Декодирование JWT (подпись, срок действия).
    2. Тип токена должен быть 'access', а не 'refresh'.
    3. Пользователь с таким login должен существовать в БД.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        # Отклоняем refresh-токен на защищённых эндпоинтах
        if payload.get("type") != "access":
            raise exc
        login: str | None = payload.get("sub")
        if not login:
            raise exc
    except JWTError:
        raise exc

    result = await db.execute(select(User).where(User.login == login))
    user = result.scalar_one_or_none()
    if user is None:
        raise exc
    return user
