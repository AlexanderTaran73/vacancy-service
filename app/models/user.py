"""
ORM-модель пользователя системы.

Роли определены перечислением UserRole. Хранятся как VARCHAR (native_enum=False),
что упрощает миграции и работу с тестовой БД без управления PostgreSQL ENUM-типами.
"""

import enum

from sqlalchemy import Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей: admin — полный доступ, hr — работа с резюме, employee — базовый."""

    admin = "admin"
    hr = "hr"
    employee = "employee"


class User(Base):
    """
    Пользователь системы.

    login — уникальный идентификатор для входа (не email).
    hashed_password — bcrypt-хеш, открытый пароль никогда не хранится.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=False, length=20),
        default=UserRole.employee,
    )
