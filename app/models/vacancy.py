"""
ORM-модель вакансии.

Вакансия связана с Category (направление) и Position (должность) через
внешние ключи — это обеспечивает 3НФ: все non-key атрибуты зависят
только от первичного ключа id, а не от названия категории или должности.

Статус хранится как VARCHAR (native_enum=False) для упрощения
управления схемой без PostgreSQL ENUM-типов.
"""

import enum

from sqlalchemy import Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VacancyStatus(str, enum.Enum):
    """Жизненный цикл вакансии: открыта для откликов или закрыта."""

    open = "open"
    closed = "closed"


class Vacancy(Base):
    """
    Вакансия внутри компании.

    position_id → positions.id (должность/направление).
    category_id → categories.id (сфера деятельности).
    """

    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    status: Mapped[VacancyStatus] = mapped_column(
        SAEnum(VacancyStatus, native_enum=False, length=20),
        default=VacancyStatus.open,
    )
