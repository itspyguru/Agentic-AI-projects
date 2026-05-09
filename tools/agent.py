from langchain.agents import create_agent as build_agent

from tools.calculator import calculator
from tools.web_search import web_search
from tools.date import get_current_date
from tools.url_scraper import url_scraper
from tools.weather_search import weather_tool

def create_agent(llm, system_prompt=""):
    tools = [
        calculator,
        web_search,
        get_current_date,
        url_scraper,
        weather_tool
    ]

    return build_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            system_prompt
            + """
            When a question asks about:
            - recent events
            - current data
            - latest news
            - real-time information
            - something you are unsure about
            use the web_search tool.

            For mathematical calculations use the calculator tool.
            To get current date use the get_current_date tool.
            """
        )
    )