# src/core/config.py

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные окружения из файла.env
load_dotenv()

class Settings(BaseSettings):
    """
    Pydantic-модель для хранения настроек приложения.
    Загружает переменные из.env файла.
    """
    # Database
    DATABASE_URL: str
    REDIS_URL: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # LLMs and External Services
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str
    SMART_LLM_MODEL: str = "gpt-4o"
    FAST_LLM_MODEL: str = "gpt-4o-mini"

    # LangSmith Observability
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "LawGPT-v2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Глобальный экземпляр настроек для импорта в другие модули
settings = Settings()

# Отдельные переменные для Celery, чтобы избежать проблем с интроспекцией Pydantic
CELERY_BROKER_URL: str = settings.REDIS_URL
CELERY_RESULT_BACKEND: str = settings.REDIS_URL