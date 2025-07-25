# src/db/base.py

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Соглашения об именовании для автоматической генерации ограничений в Alembic.
# Это предотвращает проблемы с автогенерируемыми скриптами миграций.
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy ORM.
    Включает асинхронную поддержку и соглашения об именовании для миграций.
    """
    __abstract__ = True
    
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)