import wikipedia
from langchain.tools import tool

@tool
def wikipedia_search(query: str) -> str:
    """Perform a search on Wikipedia and return the summary of the top result."""
    try:
        results = wikipedia.search(query)
        if not results:
            return "No results found."
        summary = wikipedia.summary(results[0], sentences=3)
        return f"{results[0]}: {summary}"
    except Exception as e:
        return f"Error performing Wikipedia search: {e}"