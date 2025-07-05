# src/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

class SessionManager:
    """
    Класс, управляющий движком SQLAlchemy и фабрикой сессий.
    """
    def __init__(self):
        self._engine = None
        self._session_factory = None

    def init(self, db_url: str):
        """
        Инициализирует асинхронный движок и фабрику сессий.
        """
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
        if self._engine is None:
            raise Exception("SessionManager не инициализирован")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

    async def get_session(self) -> AsyncGenerator:
        """
        Предоставляет сессию базы данных как асинхронный генератор.
        """
        if self._session_factory is None:
            raise Exception("SessionManager не инициализирован")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

# Глобальный экземпляр менеджера сессий
sessionmanager = SessionManager()

async def get_db() -> AsyncGenerator:
    """
    Зависимость FastAPI для получения сессии базы данных.
    """
    async for session in sessionmanager.get_session():
        yield session