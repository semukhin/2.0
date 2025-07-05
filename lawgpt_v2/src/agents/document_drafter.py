from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.llm_factory import get_smart_llm

class DraftDocument(BaseModel):
    draft_document: str = Field(description="Сгенерированный проект юридического документа.")

# Промпт для составителя документов
_drafter_prompt = ChatPromptTemplate.from_template(
    """
    На основе следующего аргумента составь формальный юридический документ (например, меморандум, ходатайство, пункт договора).
    Аргумент:
    ---
    {synthesized_argument}
    ---
    """
)

drafter_llm = get_smart_llm().with_structured_output(DraftDocument)

document_drafter_chain = _drafter_prompt | drafter_llm
