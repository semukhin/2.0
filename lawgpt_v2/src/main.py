# src/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import settings
from src.db.session import sessionmanager
from src.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Менеджер жизненного цикла приложения. Обрабатывает события запуска и остановки.
    """
    print("--- Запуск приложения ---")
    # Инициализация менеджера сессий БД при старте
    sessionmanager.init(settings.DATABASE_URL)
    yield
    # Закрытие пула соединений БД при остановке
    await sessionmanager.close()
    print("--- Остановка приложения ---")

app = FastAPI(
    title="LawGPT 2.0 API",
    description="Продвинутая многоагентная система для юридического анализа.",
    version="2.0.0",
    lifespan=lifespan
)

# Включение всех модульных маршрутизаторов
app.include_router(api_router)

@app.get("/", tags=)
def read_root():
    """
    Корневой эндпоинт для проверки работоспособности API.
    """
    return {"message": "Добро пожаловать в API LawGPT 2.0"}