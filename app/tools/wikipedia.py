import wikipediaapi
from app.tools.base import Tool

@Tool.as_tool
def get_wikipedia_summary(topic: str, lang: str = "en") -> str:
    """Fetches the summary of a Wikipedia page.
    
    Args:
        topic (str): The topic to search on Wikipedia.
        lang (str): The language code (default is English: "en").
    
    Returns:
        str: The summary of the Wikipedia page or an error message.
    """
    wiki = wikipediaapi.Wikipedia(user_agent="mars-agent")
    page = wiki.page(topic)

    if not page.exists():
        return f"No Wikipedia page found for '{topic}'."
    
    return page.summary
