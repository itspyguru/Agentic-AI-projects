import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

@tool
def url_scraper(url: str) -> str:
    """Scrape the content of a webpage given its URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator='\n', strip=True)[:5000]  # Limit to first 5000 chars
    except Exception as e:
        return f"Error scraping URL: {e}"