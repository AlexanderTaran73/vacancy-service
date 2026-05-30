"""
ORM-модель резюме кандидата.

candidate_data хранится как JSON — гибкая структура данных кандидата
(имя, email, телефон, навыки, опыт). Использование JSON-поля обосновано
тем, что состав полей резюме может варьироваться, при этом другие сущности
не зависят от конкретных атрибутов кандидата.

category_id → categories.id: привязка к направлению поиска работы.
"""

import enum

from sqlalchemy import Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ResumeStatus(str, enum.Enum):
    """Статус рассмотрения резюме HR-отделом."""

    active = "active"
    inactive = "inactive"
    under_review = "under_review"


class Resume(Base):
    """
    Резюме кандидата на вакансию.

    candidate_data — JSON с произвольными данными кандидата.
    category_id — категория, по которой кандидат ищет работу.
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    status: Mapped[ResumeStatus] = mapped_column(
        SAEnum(ResumeStatus, native_enum=False, length=20),
        default=ResumeStatus.active,
    )
