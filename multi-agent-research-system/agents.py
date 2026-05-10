from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search, web_scrape

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", temperature=0.7)

# research-agent
def build_research_agent():
    tools = [
        web_search
    ]

    return create_agent(llm, tools, name="research-agent")

# reading-agent
def build_reading_agent():
    tools = [
        web_scrape
    ]

    return create_agent(llm, tools, name="reading-agent")

# writer-chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a expert research writer that writes a comprehensive report based on the research findings and provide clear, structured & insightful reports."),
    ("human", """Based on the following research findings, write a comprehensive report:\n      Topic: {topic}
     
    Research Findings: {research}
     
    Structure the report as:
     - Introduction
     - Key Findings
     - Conclusion
     - Sources & References

    Be detailed, factual, and ensure the report is well-structured and insightful. Use the research findings to support your analysis and conclusions. Provide clear citations for any sources referenced in the report.
     """
    )
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a critical analyst that reviews research reports for accuracy, depth, and clarity. Your task is to evaluate the report based on the research findings and provide constructive feedback for improvement."),
    ("human", """Review the following research report and provide feedback:\n      
     Topic: {topic}
     Report: {report}

     Respond in this exact format:
     Score: X/10
     Strengths:
      - ...
      - ...
     Areas for Improvement:
      - ...
      - ...
     One line verdict: 
      - ...
    """)]
)

critic_chain = critic_prompt | llm | StrOutputParser()