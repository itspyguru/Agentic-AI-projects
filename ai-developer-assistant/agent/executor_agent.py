import asyncio
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.planner_agent import get_planner_agent, ExecutionPlan
from agent.workspace_agent import MCP_CONFIG


async def execute_plan(plan: ExecutionPlan) -> list:
    client = MultiServerMCPClient(MCP_CONFIG)
    tools = await client.get_tools()
    tool_map = {t.name: t for t in tools}

    results = []
    for step in plan.steps:
        print(f"[{step.step_number}] {step.tool} — {step.description}")

        tool = tool_map.get(step.tool)
        if tool is None:
            print(f"    ✗ unknown tool: {step.tool}")
            results.append({"step": step.step_number, "error": "unknown tool"})
            break

        try:
            output = await tool.ainvoke(step.arguments)
            print(f"    ✓ {output}")
            results.append({"step": step.step_number, "output": output})
        except Exception as e:
            print(f"    ✗ {e}")
            results.append({"step": step.step_number, "error": str(e)})
            break

    return results


async def main():
    planner = await get_planner_agent()
    plan = await planner.ainvoke({"request": "help me create a snake game in python"})
    print(f"GOAL: {plan.goal}\n")
    await execute_plan(plan)


if __name__ == "__main__":
    asyncio.run(main())
