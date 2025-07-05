# src/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

class SessionManager:
    """
    Класс, управляющий движком SQLAlchemy и фабрикой сессий.
    """
    def __init__(self):
        self._engine = None
        self._session_factory = None

    def init(self, db_url: str = None):
        """
        Инициализирует асинхронный движок и фабрику сессий.
        """
        if db_url is None:
            db_url = settings.DATABASE_URL
        self._engine = create_async_engine(db_url, echo=True)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def close(self):
        """
        Закрывает соединения движка.
        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Предоставляет сессию базы данных как асинхронный генератор.
        """
        if self._session_factory is None:
            self.init()
        async with self._session_factory() as session:
            yield session

# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()

async def get_db() -> AsyncGenerator:
    """
    Зависимость FastAPI для получения сессии базы данных.
    """
    async for session in session_manager.get_session():
        yield session