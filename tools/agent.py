from langchain.agents import create_agent as build_agent
from tools.date import get_current_date
from tools.calculator import calculator
from tools.url_scraper import url_scraper
from tools.web_search import web_search
from tools.wikipedia_search import wikipedia_search
from tools.image_tools import generate_image_tool, analyze_image_tool

def create_agent(llm, uploaded_image=None, generated_images=None, system_prompt=""):
    tools = [
        get_current_date,
        calculator,
        url_scraper,
        web_search,
        wikipedia_search,
        generate_image_tool(generated_images),
        analyze_image_tool(llm, uploaded_image),
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
            When a question asks about - recent events, current news, or anything that requires up-to-date information, use the web_search tool to perform a web search and get the latest information. Do not use it for any other purpose.
            When a question asks about general knowledge, historical facts, or information that is likely to be found on Wikipedia, use the wikipedia_search tool to get the relevant information. Do not use it for any other purpose.
            When the user asks to create, draw, design, generate, or visualize an image, use the generate_image_tool with a vivid descriptive prompt. The image is shown to the user automatically — do not include the file path in your reply.
            When the user has uploaded an image and is asking about it (describe, identify, read text from, etc.), use the analyze_uploaded_image tool. Do not use it if no image is uploaded.
            When the user asks to analyze an uploaded image, first check if an image has been uploaded. If not, reply that no image is available. If an image is available, use the analyze_uploaded_image tool with the user's question about the image to get the answer.
            When the user asks to generate an image, use the generate_image_tool with a vivid descriptive prompt to create the image. The image is shown to the user automatically — do not include the file path in your reply.
            """
        )
    )
