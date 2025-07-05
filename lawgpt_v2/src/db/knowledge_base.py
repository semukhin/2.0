# src/db/models/knowledge_base.py

from sqlalchemy import (
    Column, BigInteger, String, Text, Index, func, ForeignKey, Integer
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    content_tsv: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    
    __table_args__ = (
        Index('idx_knowledge_base_embedding', embedding, postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64}),
        Index('idx_knowledge_base_tsv', content_tsv, postgresql_using='gin'),
        Index('idx_knowledge_base_metadata', metadata, postgresql_using='gin'),
    )