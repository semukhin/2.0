# src/graph/tools/kb_search.py

import asyncio
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.config import settings

# Инициализация модели для эмбеддингов вне функции для переиспользования
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)

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
async def hybrid_search(query: str, user_id: int) -> str:
    """
    Выполняет гибридный поиск (векторный + полнотекстовый) по юридическим документам пользователя.
    Используйте этот инструмент для поиска контекста в загруженных документах для ответа на вопросы пользователя.
    """
    print(f"--- Tool: Гибридный поиск для user {user_id} с запросом: '{query}' ---")
    
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(bind=engine)

    try:
        query_embedding = await embeddings_model.aembed_query(query)
        
        async with session_factory() as session:
            vector_search_task = session.execute(
                text("""
                    SELECT id, content FROM knowledge_base
                    WHERE owner_id = :user_id
                    ORDER BY embedding <=> :query_embedding
                    LIMIT 20
                """),
                {"user_id": user_id, "query_embedding": str(query_embedding)}
            )
            
            fts_search_task = session.execute(
                text("""
                    SELECT id, content FROM knowledge_base
                    WHERE owner_id = :user_id AND content_tsv @@ websearch_to_tsquery('english', :query)
                    ORDER BY ts_rank(content_tsv, websearch_to_tsquery('english', :query)) DESC
                    LIMIT 20
                """),
                {"user_id": user_id, "query": query}
            )
            
            vector_results, fts_results = await asyncio.gather(vector_search_task, fts_search_task)
            
            vector_docs = [(row, row[1]) for row in vector_results.fetchall()]
            fts_docs = [(row, row[1]) for row in fts_results.fetchall()]

        if not vector_docs and not fts_docs:
            return "В документах не найдено релевантной информации."

        reranked_ids = reciprocal_rank_fusion([vector_docs, fts_docs])
        
        top_5_ids = [doc_id for doc_id, score in reranked_ids[:5]]
        
        all_docs = {doc_id: content for doc_id, content in vector_docs + fts_docs}
        
        context_parts =
        for doc_id in top_5_ids:
            if doc_id in all_docs:
                context_parts.append(f"--- Document ID: {doc_id} ---\n{all_docs[doc_id]}")

        if not context_parts:
            return "Не удалось извлечь содержимое для найденных документов."
            
        return "\n\n".join(context_parts)
    except Exception as e:
        print(f"Ошибка в hybrid_search: {e}")
        return "Произошла ошибка при поиске в базе знаний."
    finally:
        await engine.dispose()