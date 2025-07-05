# src/graph/nodes.py

from.agent_state import AgentState
from src.agents.coordinator import coordinator_chain
from src.agents.document_analysis import analysis_chain
from src.agents.llm_factory import get_fast_llm, get_smart_llm
from.tools.web_search import web_search_tool
from.tools.kb_search import hybrid_search
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

# --- Узлы Агентов ---

async def run_coordinator(state: AgentState) -> dict:
    """Запускает агента-координатора для создания плана."""
    print("--- УЗЕЛ: Координатор ---")
    response = await coordinator_chain.ainvoke({
        "messages": state["messages"],
        "original_query": state["original_query"]
    })
    return {"plan": response.plan, "search_query": response.search_query}

async def run_web_search(state: AgentState) -> dict:
    """Выполняет поиск в интернете."""
    print(f"--- УЗЕЛ: Поиск в интернете ({state['search_query']}) ---")
    result = await web_search_tool.ainvoke({"query": state["search_query"]})
    return {"retrieved_documents": result}

async def run_legal_search(state: AgentState) -> dict:
    """Выполняет гибридный поиск по базе знаний."""
    print(f"--- УЗЕЛ: Поиск в базе знаний ({state['search_query']}) ---")
    result = await hybrid_search.ainvoke({"query": state["search_query"], "user_id": state["user_id"]})
    return {"retrieved_documents": result}

async def run_document_analysis(state: AgentState) -> dict:
    """Анализирует извлеченные документы."""
    print("--- УЗЕЛ: Анализ документов ---")
    if not state.get("retrieved_documents"):
        return {"analyzed_facts":}
    
    response = await analysis_chain.ainvoke({"documents": state["retrieved_documents"]})
    return {"analyzed_facts": [fact.dict() for fact in response.facts]}

async def run_synthesis(state: AgentState) -> dict:
    """Синтезирует аргумент из проанализированных фактов."""
    print("--- УЗЕЛ: Синтез аргумента ---")
    prompt = ChatPromptTemplate.from_template(
        """Основываясь на следующем запросе пользователя и извлеченных фактах, создай связный юридический аргумент.
        Запрос: {query}
        Факты: {facts}"""
    )
    synthesis_chain = prompt | get_smart_llm()
    response = await synthesis_chain.ainvoke({
        "query": state["original_query"],
        "facts": state["analyzed_facts"]
    })
    return {"synthesized_argument": response.content}

async def run_response_finalizer(state: AgentState) -> dict:
    """Форматирует финальный ответ для пользователя."""
    print("--- УЗЕЛ: Финализация ответа ---")
    # Собираем весь контекст, который есть в состоянии
    context = f"""
    Исходный запрос: {state.get('original_query', 'N/A')}
    Результаты поиска: {state.get('retrieved_documents', 'N/A')}
    Извлеченные факты: {state.get('analyzed_facts', 'N/A')}
    Синтезированный аргумент: {state.get('synthesized_argument', 'N/A')}
    Проект документа: {state.get('draft_document', 'N/A')}
    """
    
    prompt = ChatPromptTemplate.from_template(
        """Основываясь на всей проделанной работе, сформируй окончательный, исчерпывающий и хорошо отформатированный ответ для пользователя.
        Если есть цитаты или ссылки на документы, обязательно укажи их.
        
        Контекст работы:
        {context}
        
        Сформируй финальный ответ:
        """
    )
    finalizer_chain = prompt | get_smart_llm()
    response = await finalizer_chain.ainvoke({"context": context})
    return {"final_response": response.content, "messages": [("ai", response.content)]}

# --- Узлы для цикла самокоррекции ---

async def evaluate_retrieval(state: AgentState) -> dict:
    """Оценивает релевантность найденных документов."""
    print("--- УЗЕЛ: Оценка релевантности поиска ---")
    if not state.get("retrieved_documents"):
        return {"retrieval_relevance": "Irrelevant"}

    prompt = ChatPromptTemplate.from_template(
        """Оцени, являются ли следующие документы релевантными для ответа на запрос пользователя.
        Ответь только 'Relevant' или 'Irrelevant'.
        
        Запрос пользователя: {query}
        Найденные документы: {documents}
        """
    )
    eval_chain = prompt | get_fast_llm()
    response = await eval_chain.ainvoke({
        "query": state["original_query"],
        "documents": state["retrieved_documents"][:1000] # Ограничиваем для экономии
    })
    relevance = "Relevant" if "relevant" in response.content.lower() else "Irrelevant"
    print(f"Результат оценки: {relevance}")
    return {"retrieval_relevance": relevance}

async def refine_query(state: AgentState) -> dict:
    """Уточняет поисковый запрос, если предыдущий поиск был нерелевантным."""
    print("--- УЗЕЛ: Уточнение запроса ---")
    prompt = ChatPromptTemplate.from_template(
        """Предыдущий поисковый запрос "{search_query}" по теме "{original_query}" вернул нерелевантные результаты.
        Сгенерируй новый, более точный или альтернативный поисковый запрос, чтобы найти нужную информацию.
        Верни только сам новый запрос.
        """
    )
    refine_chain = prompt | get_fast_llm()
    response = await refine_chain.ainvoke({
        "search_query": state["search_query"],
        "original_query": state["original_query"]
    })
    return {"search_query": response.content, "retrieval_attempts": state.get("retrieval_attempts", 0) + 1}

# --- Условные ребра ---

def route_after_coordinator(state: AgentState) -> str:
    """Маршрутизирует выполнение после координатора на основе плана."""
    if not state.get("plan"):
        return "end"
    first_step = state["plan"]
    return first_step

def route_after_retrieval_evaluation(state: AgentState) -> str:
    """Маршрутизирует после оценки релевантности поиска."""
    attempts = state.get("retrieval_attempts", 0)
    if state.get("retrieval_relevance") == "Irrelevant" and attempts < 2:
        return "refine"
    else:
        # Находим следующий шаг после поиска в плане
        plan = state["plan"]
        current_step_index = -1
        if "LegalSearchAgent" in plan:
            current_step_index = plan.index("LegalSearchAgent")
        elif "WebSearchAgent" in plan:
            current_step_index = plan.index("WebSearchAgent")
        
        if current_step_index!= -1 and current_step_index + 1 < len(plan):
            return plan[current_step_index + 1]
        return "end"

def route_after_analysis(state: AgentState) -> str:
    """Маршрутизация после анализа документов."""
    plan = state["plan"]
    try:
        current_step_index = plan.index("DocumentAnalysisAgent")
        if current_step_index + 1 < len(plan):
            return plan[current_step_index + 1]
    except ValueError:
        pass
    return "end"