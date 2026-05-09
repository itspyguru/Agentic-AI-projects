from langchain.agents import create_agent as build_agent
from tools.date import get_current_date
from tools.calculator import calculator
from tools.url_scraper import url_scraper
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search

def create_agent(llm, system_prompt=""):
    tools = [
        get_current_date,
        calculator,
        url_scraper,
        web_search,
        wikipedia_search
    ]

    return build_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            system_prompt +
            """
            To get current date use the get_current_date tool. Do not use it for any other purpose.
            To calculate a mathematical expression use the calculator tool. Do not use it for any other purpose.
            To scrape the content of a URL use the url_scraper tool. Do not use it for any other purpose.
            When a questions asks about - recent events, current news, or anything that requires up-to-date information, use the web_search tool to perform a web search and get the latest information. Do not use it for any other purpose.
            When a question asks about general knowledge, historical facts, or information that is likely to be found on Wikipedia, use the wikipedia_search tool to get the relevant information. Do not use it for any other purpose.
            """
        )
    )