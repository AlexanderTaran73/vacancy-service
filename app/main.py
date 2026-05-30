"""
Точка входа приложения.

Создаёт экземпляр FastAPI и подключает все роутеры с префиксом /api/v1.
Импорт app.models необходим, чтобы SQLAlchemy зарегистрировал все ORM-модели
в Base.metadata до того, как Alembic начнёт работать с метаданными.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # регистрирует модели в Base.metadata
from app.routers import auth, categories, positions, resumes, vacancies


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Хук жизненного цикла приложения (зарезервирован для будущих событий)."""
    yield


app = FastAPI(
    title="Vacancy Service API",
    description="Internal company vacancy and resume management service",
    version="1.0.0",
    lifespan=lifespan,
)

# Регистрация роутеров с общим префиксом версии API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(vacancies.router, prefix="/api/v1/vacancies", tags=["Vacancies"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(positions.router, prefix="/api/v1/positions", tags=["Positions"])
