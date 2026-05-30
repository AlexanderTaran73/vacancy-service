"""
Бизнес-логика аутентификации.

Содержит три операции: регистрацию нового пользователя, проверку
учётных данных при входе и смену пароля. HTTP-исключения выбрасываются
здесь (а не в роутере), чтобы бизнес-правила были сосредоточены в одном месте.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import ChangePassword, UserCreate


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    """
    Регистрирует нового пользователя.

    Проверяет уникальность login перед созданием — дубль login → 400.
    Пароль немедленно хешируется, открытый текст нигде не сохраняется.
    """
    existing = await db.execute(select(User).where(User.login == data.login))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login is already registered",
        )

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        login=data.login,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, login: str, password: str) -> User:
    """
    Проверяет учётные данные пользователя.

    Возвращает пользователя при совпадении login + password,
    иначе бросает 401. Одинаковое сообщение об ошибке для
    обоих случаев (нет пользователя / неверный пароль) — защита
    от перечисления пользователей.
    """
    result = await db.execute(select(User).where(User.login == login))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def change_user_password(
    db: AsyncSession, user: User, data: ChangePassword
) -> None:
    """
    Меняет пароль текущего пользователя.

    Требует подтверждения текущего пароля (old_password),
    чтобы злоумышленник с чужим токеном не мог сменить пароль.
    """
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    user.hashed_password = hash_password(data.new_password)
    db.add(user)
    await db.commit()
