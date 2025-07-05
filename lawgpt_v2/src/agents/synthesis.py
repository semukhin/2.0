from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.agents.llm_factory import get_smart_llm

class SynthesizedArgument(BaseModel):
    synthesized_argument: str = Field(description="Связный юридический аргумент, основанный на анализе фактов.")

synthesis_prompt = ChatPromptTemplate.from_template(
    """
    На основе следующих структурированных фактов и аргументов из документов:
    ---
    {analyzed_facts}
    ---
    Сформулируй связный юридический аргумент, выяви закономерности, противоречия и подтверждающие доказательства.
    """
)

synthesis_llm = get_smart_llm().with_structured_output(SynthesizedArgument)

synthesis_chain = synthesis_prompt | synthesis_llm
