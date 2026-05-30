"""
ORM-модель категории вакансий и резюме.

Примеры категорий: «Разработка», «Менеджмент», «Продажи».
Вынесены в отдельную таблицу для приведения к 3НФ:
устранена зависимость non-key атрибута name от составного ключа.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    """Категория направления деятельности (разработка, продажи и т.д.)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
