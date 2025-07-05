# src/graph/agent_state.py

from typing import List, Dict, Any, Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Определяем возможные шаги плана для строгой типизации
AgentPlan = Literal

class AgentState(TypedDict):
    """
    Определяет состояние графа. Этот объект передается между узлами.
    """
    # Входные данные
    original_query: str
    user_id: int
    
    # План от координатора
    plan: List[AgentPlan]
    
    # Промежуточные результаты
    search_query: str
    retrieved_documents: str
    analyzed_facts: List]
    synthesized_argument: str
    draft_document: str
    
    # Финальный результат
    final_response: str
    
    # История сообщений для LLM
    messages: Annotated[list, add_messages]
    
    # Для цикла самокоррекции
    retrieval_attempts: int
    retrieval_relevance: str # 'Relevant' или 'Irrelevant'