import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from tavily import TavilyClient

import os
from dotenv import load_dotenv
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for the given query and return the results."""
    results = tavily_client.search(query, max_results=5)
    output = []
    for result in results["results"]:
        output.append(f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content']}\n")

    return "\n".join(output)

@tool
def web_scrape(url: str) -> str:
    """Scrape the content of the given URL and return the text for deeper reading."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)
    except requests.RequestException as e:
        return f"Error fetching the URL: {e}"

# query = "What is the latest news on west bengal elections?"
# print(web_search.invoke(query))