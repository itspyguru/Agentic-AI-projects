import os
import asyncio
from typing import List, Dict, Any

from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from server import filesystem_server, shell_server, git_server
from prompts.prompt_reader import get_planner_prompt

load_dotenv()

MCP_SERVERS = {
    "filesystem": filesystem_server.mcp,
    "shell": shell_server.mcp,
    "git": git_server.mcp,
}


class PlanStep(BaseModel):
    step_number: int
    tool: str
    description: str
    arguments: Dict[str, Any]


class ExecutionPlan(BaseModel):
    goal: str
    steps: List[PlanStep]


def _format_args(parameters: dict) -> str:
    props = parameters.get("properties", {})
    required = set(parameters.get("required", []))
    parts = []
    for name, spec in props.items():
        marker = "" if name in required else "?"
        parts.append(f"{name}{marker}: {spec.get('type', 'any')}")
    return ", ".join(parts)


async def _build_tool_catalog() -> str:
    sections = []
    for label, server in MCP_SERVERS.items():
        tools = await server.list_tools()
        lines = [f"{label} tools:"]
        for tool in tools:
            desc = (tool.description or "").strip().splitlines()[0]
            args = _format_args(tool.parameters)
            lines.append(f"- {tool.name}({args}): {desc}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


async def get_planner_agent():
    tools_text = await _build_tool_catalog()
    parser = PydanticOutputParser(pydantic_object=ExecutionPlan)

    prompt = ChatPromptTemplate.from_messages([
        ("system", get_planner_prompt() + "\n\n{format_instructions}"),
        ("user", "{request}"),
    ]).partial(
        tools=tools_text,
        format_instructions=parser.get_format_instructions(),
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    return prompt | llm | parser


async def main():
    planner = await get_planner_agent()
    request = "help me create a snake game in python"
    plan = await planner.ainvoke({"request": request})
    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
