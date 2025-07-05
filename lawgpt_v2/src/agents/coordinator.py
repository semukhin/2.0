# src/agents/coordinator.py

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.llm_factory import get_smart_llm

class PlanSchema(BaseModel):
    """Схема для плана выполнения, генерируемого координатором."""
    plan: List[str] = Field(description="Список шагов (агентов) для выполнения задачи. Возможные значения: 'WebSearchAgent', 'LegalSearchAgent', 'DocumentAnalysisAgent', 'CaseLawSynthesisAgent', 'DocumentDrafterAgent', 'ResponseFinalizerAgent'.")
    search_query: str = Field(description="Оптимизированный поисковый запрос для следующего агента-исследователя.")

# Промпт для агента-координатора
coordinator_prompt_template = ChatPromptTemplate.from_messages()

# Цепочка для координатора
coordinator_chain = coordinator_prompt_template | get_smart_llm().with_structured_output(PlanSchema)