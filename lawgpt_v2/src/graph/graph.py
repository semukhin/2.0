# src/graph/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.redis import RedisSaver
from src.core.config import settings
from.agent_state import AgentState
from.nodes import (
    run_coordinator, run_web_search, run_legal_search,
    run_document_analysis, run_synthesis, run_response_finalizer,
    evaluate_retrieval, refine_query,
    route_after_coordinator, route_after_retrieval_evaluation, route_after_analysis
)

# Инициализация чекпоинтера для сохранения состояния в Redis
memory = RedisSaver.from_conn_string(settings.REDIS_URL)

# Создание графа
workflow = StateGraph(AgentState)

# Добавление узлов
workflow.add_node("coordinator", run_coordinator)
workflow.add_node("WebSearchAgent", run_web_search)
workflow.add_node("LegalSearchAgent", run_legal_search)
workflow.add_node("evaluate_retrieval", evaluate_retrieval)
workflow.add_node("refine_query", refine_query)
workflow.add_node("DocumentAnalysisAgent", run_document_analysis)
workflow.add_node("CaseLawSynthesisAgent", run_synthesis)
workflow.add_node("ResponseFinalizerAgent", run_response_finalizer)

# Определение ребер
workflow.set_entry_point("coordinator")

# 1. Маршрутизация от координатора
workflow.add_conditional_edges(
    "coordinator",
    route_after_coordinator,
    {
        "WebSearchAgent": "WebSearchAgent",
        "LegalSearchAgent": "LegalSearchAgent",
        "end": END
    }
)

# 2. Поток после поиска (включая цикл самокоррекции)
workflow.add_edge("WebSearchAgent", "evaluate_retrieval")
workflow.add_edge("LegalSearchAgent", "evaluate_retrieval")

workflow.add_conditional_edges(
    "evaluate_retrieval",
    route_after_retrieval_evaluation,
    {
        "refine": "refine_query",
        "DocumentAnalysisAgent": "DocumentAnalysisAgent",
        "ResponseFinalizerAgent": "ResponseFinalizerAgent", # Если анализ не нужен
        "end": END
    }
)
workflow.add_edge("refine_query", "LegalSearchAgent") # Повторная попытка поиска в базе знаний

# 3. Поток после анализа документов
workflow.add_conditional_edges(
    "DocumentAnalysisAgent",
    route_after_analysis,
    {
        "CaseLawSynthesisAgent": "CaseLawSynthesisAgent",
        "ResponseFinalizerAgent": "ResponseFinalizerAgent",
        "end": END
    }
)

# 4. Линейные переходы
workflow.add_edge("CaseLawSynthesisAgent", "ResponseFinalizerAgent")
workflow.add_edge("ResponseFinalizerAgent", END)

# Компиляция графа с чекпоинтером
graph_app = workflow.compile(checkpointer=memory)