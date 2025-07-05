from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.llm_factory import get_fast_llm

# Response finalizer agent logic placeholder

class FinalResponse(BaseModel):
    final_response: str = Field(description="Финальный, отформатированный для пользователя ответ.")

finalizer_prompt = ChatPromptTemplate.from_template(
    """
    Приведи следующий текст к профессиональному юридическому стилю, добавь необходимые цитаты и оговорки, если требуется.
    Текст:
    ---
    {draft_document}
    ---
    """
)

finalizer_llm = get_fast_llm().with_structured_output(FinalResponse)

response_finalizer_chain = finalizer_prompt | finalizer_llm
