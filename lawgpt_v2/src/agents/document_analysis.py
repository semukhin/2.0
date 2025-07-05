# src/agents/document_analysis.py

from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.llm_factory import get_fast_llm

class ExtractedFact(BaseModel):
    """Структурированная информация, извлеченная из юридического документа."""
    fact_summary: str = Field(description="Краткое изложение ключевого факта, аргумента или положения.")
    source_document_id: str = Field(description="ID документа, из которого извлечен факт (если известен).")
    direct_quote: str = Field(description="Точная цитата из документа, подтверждающая факт.")

class AnalysisResult(BaseModel):
    """Контейнер для всех фактов, извлеченных из одного фрагмента текста."""
    facts: List[ExtractedFact]

# Промпт для анализатора документов
analysis_prompt_template = ChatPromptTemplate.from_template(
"""Твоя задача — внимательно проанализировать предоставленный юридический текст и извлечь из него все значимые факты, аргументы, определения и положения.

Для каждого найденного значимого элемента используй инструмент `ExtractedFact`. Не упускай ничего важного.

Проанализируй следующий текст:
---
{documents}
---
"""
)

# LLM с привязанным инструментом
analysis_llm = get_fast_llm().with_structured_output(AnalysisResult)

# Цепочка для анализа
analysis_chain = analysis_prompt_template | analysis_llm