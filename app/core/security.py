"""
Утилиты безопасности: хеширование паролей и работа с JWT.

Для хеширования паролей используется библиотека bcrypt напрямую,
без passlib — это обходит несовместимость passlib 1.7.x с bcrypt >= 4.0.
JWT-токены содержат поле 'type' (access/refresh), что позволяет на сервере
отклонять access-токен там, где ожидается refresh, и наоборот.
"""

from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import settings


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет пароль в открытом виде против bcrypt-хеша."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    """Возвращает bcrypt-хеш пароля с автоматической солью."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _create_token(data: dict, token_type: str, expire: timedelta) -> str:
    """Общая фабрика JWT-токенов. Добавляет exp и type в payload."""
    payload = data.copy()
    payload.update(
        {
            "exp": datetime.utcnow() + expire,
            "type": token_type,  # различаем access и refresh на стороне сервера
        }
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(data: dict) -> str:
    """Создаёт короткоживущий access-токен."""
    return _create_token(
        data,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(data: dict) -> str:
    """Создаёт долгоживущий refresh-токен для обновления пары."""
    return _create_token(
        data,
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """Декодирует JWT и возвращает payload. Бросает JWTError при невалидном токене."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
