# src/graph/tools/web_search.py

from langchain_community.tools.tavily_search import TavilySearchResults
from src.core.config import settings

# Инициализация инструмента для поиска в интернете
web_search_tool = TavilySearchResults(
    max_results=5,
    api_key=settings.TAVILY_API_KEY,
    description="Полезен для поиска актуальной информации, новостей или общих юридических определений в интернете."
)