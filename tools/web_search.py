import os
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

@tool
def web_search(query: str) -> str:
    """Search the live web for up-to-date information. Use this for current events,
      recent news, real-time data, or anything that may have changed after the model's
      training cutoff."""
    try:
        response = client.search(query, max_results=5)
        hits = response.get("results", [])
        return "\n\n".join(
            f"{h['title']}\n{h['url']}\n{h.get('content', '')}" for h in hits
        ) or "No results."
    except Exception as e:
        return f"Error performing web search: {e}"