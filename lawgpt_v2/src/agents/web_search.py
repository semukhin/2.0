from src.graph.tools.web_search import web_search_tool

def run_web_search(query: str) -> str:
    """Выполняет поиск в интернете через TavilySearchResults."""
    return web_search_tool.run(query)
