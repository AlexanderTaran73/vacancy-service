"""
Конфигурация приложения.

Настройки загружаются из переменных окружения или файла .env.
extra="ignore" позволяет передавать POSTGRES_* переменные
для docker-compose без ошибок валидации.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Параметры приложения: БД, JWT, тестовая БД."""

    DATABASE_URL: str           # asyncpg-совместимый URL основной БД
    TEST_DATABASE_URL: str = "" # URL тестовой БД (используется pytest)

    SECRET_KEY: str             # секрет для подписи JWT (минимум 32 символа)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
