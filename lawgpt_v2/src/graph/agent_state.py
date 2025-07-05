# src/graph/agent_state.py

from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    """
    Определяет состояние графа. Этот объект передается между узлами.
    """
    # Входные данные
    original_query: str
    user_id: int
    
    # План от координатора
    plan: List[str]
    
    # Промежуточные результаты
    search_query: str
    retrieved_documents: List[Document]
    analyzed_facts: Dict[str, Any]
    synthesized_argument: str
    draft_document: str
    
    # Финальный результат
    final_response: str
    
    # История сообщений для LLM
    messages: Annotated[list, add_messages]
    
    # Для цикла самокоррекции
    retrieval_attempts: int
    retrieval_relevance: str # 'Relevant' или 'Irrelevant'
    # ... другие промежуточные состояния по мере необходимости