# src/graph/tools/kb_search.py

import asyncio
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

# Инициализация модели для эмбеддингов вне функции для переиспользования
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)

async def fts_search(session, query: str, user_id: int, limit: int = 10):
    sql = text("""
        SELECT id, ts_rank(content_tsv, plainto_tsquery(:query)) AS rank
        FROM knowledge_base
        WHERE owner_id = :user_id
        ORDER BY rank DESC
        LIMIT :limit
    """)
    result = await session.execute(sql, {"query": query, "user_id": user_id, "limit": limit})
    return [(row.id, row.rank) for row in result]

async def vector_search(session, embedding, user_id: int, limit: int = 10):
    sql = text("""
        SELECT id, 1 - (embedding <#> :embedding) AS score
        FROM knowledge_base
        WHERE owner_id = :user_id
        ORDER BY embedding <#> :embedding
        LIMIT :limit
    """)
    result = await session.execute(sql, {"embedding": embedding, "user_id": user_id, "limit": limit})
    return [(row.id, row.score) for row in result]

def reciprocal_rank_fusion(results: list[list[tuple]], k: int = 60) -> list[tuple[int, float]]:
    """Выполняет слияние ранжированных списков с использованием Reciprocal Rank Fusion."""
    fused_scores = {}
    for result_list in results:
        for rank, (doc_id, _) in enumerate(result_list):
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
            fused_scores[doc_id] += 1 / (rank + k)
    
    reranked_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return reranked_results

@tool
def hybrid_search(query: str, user_id: int) -> str:
    """
    Выполняет гибридный поиск (векторный + полнотекстовый) по юридическим документам пользователя.
    Возвращает id топ-N документов.
    """
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine)
    async def _search():
        query_embedding = await embeddings_model.aembed_query(query)
        async with session_factory() as session:
            fts = await fts_search(session, query, user_id)
            vect = await vector_search(session, query_embedding, user_id)
            fused = reciprocal_rank_fusion([fts, vect])
            top_ids = [doc_id for doc_id, _ in fused[:10]]
            return top_ids
    return asyncio.run(_search())