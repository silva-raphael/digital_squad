from duckduckgo_search import DDGS

from app.tools.base import Tool

@Tool.as_tool
def search_duckduckgo(query: str, num_results=10):
    """
    Perform a DuckDuckGo search and return results.
    
    Args:
        query: Search query string.
        num_results: Number of search results to return.

    Returns: 
        List of search results with title, link, and snippet.
    """
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=num_results)
    return list(results)