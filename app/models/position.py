"""
ORM-модель должности (направления).

Примеры должностей: «Senior Developer», «Team Lead», «Sales Manager».
Вынесена отдельно для соблюдения 3НФ: исключает повторение строк
в таблице вакансий при одинаковых должностях.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Position(Base):
    """Должность или направление работы."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
