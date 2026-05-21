import os
from typing import Optional, Literal, Any, Dict

from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from prompts.prompt_reader import get_reflection_prompt

load_dotenv()


FailureClass = Literal["TRANSIENT", "RECOVERABLE", "PLAN_INVALID", "ENVIRONMENT", "FATAL"]
NextAction = Literal["PROCEED", "RETRY", "RECOVER_THEN_RETRY", "REPLAN", "HALT"]


class ReflectionResult(BaseModel):
    step_number: int
    success: bool
    failure_class: Optional[FailureClass] = None
    next_action: NextAction
    reasoning: str
    recovery_instruction: Optional[str] = None


class StepContext(BaseModel):
    step_number: int
    description: str
    tool: str
    arguments: Dict[str, Any]
    output: Any = None
    error: Optional[str] = None


def get_reflection_agent():
    parser = PydanticOutputParser(pydantic_object=ReflectionResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_reflection_prompt() + "\n\n{format_instructions}"),
        ("user",
         "Step {step_number}: {description}\n"
         "Tool: {tool}\n"
         "Arguments: {arguments}\n"
         "Output: {output}\n"
         "Error: {error}"),
    ]).partial(format_instructions=parser.get_format_instructions())

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    return prompt | llm | parser
