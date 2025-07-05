# src/agents/llm_factory.py

from langchain_openai import ChatOpenAI
from src.core.config import settings

# Фабрика для создания экземпляров LLM
# Это позволяет централизованно управлять настройками моделей

def get_smart_llm():
    """Возвращает мощную модель для сложных рассуждений."""
    return ChatOpenAI(
        model=settings.SMART_LLM_MODEL, 
        temperature=0, 
        api_key=settings.OPENAI_API_KEY
    )

def get_fast_llm():
    """Возвращает быструю и дешевую модель для простых, структурированных задач."""
    return ChatOpenAI(
        model=settings.FAST_LLM_MODEL, 
        temperature=0, 
        api_key=settings.OPENAI_API_KEY
    )