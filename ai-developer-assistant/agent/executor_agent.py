import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent.planner_agent import get_planner_agent, ExecutionPlan
from agent.workspace_agent import MCP_CONFIG


class StepResult(BaseModel):
    step_number: int
    tool: str
    arguments: Dict[str, Any]
    success: bool
    output: Any = None
    error: Optional[str] = None


class ExecutionState(BaseModel):
    goal: str
    current_step: int = 0
    completed_steps: List[int] = []
    failed_steps: List[int] = []
    step_results: List[StepResult] = []
    status: str = "running"


async def execute_plan(plan: ExecutionPlan) -> ExecutionState:
    client = MultiServerMCPClient(MCP_CONFIG)
    tools = await client.get_tools()
    tool_map = {t.name: t for t in tools}

    state = ExecutionState(goal=plan.goal)
    total = len(plan.steps)

    for step in plan.steps:
        state.current_step = step.step_number
        print(f"[{step.step_number}/{total}] {step.tool} — {step.description}")

        tool = tool_map.get(step.tool)
        if tool is None:
            state.step_results.append(StepResult(
                step_number=step.step_number,
                tool=step.tool,
                arguments=step.arguments,
                success=False,
                error=f"unknown tool: {step.tool}",
            ))
            state.failed_steps.append(step.step_number)
            state.status = "failed"
            print(f"    ✗ unknown tool: {step.tool}")
            return state

        try:
            output = await tool.ainvoke(step.arguments)
            state.step_results.append(StepResult(
                step_number=step.step_number,
                tool=step.tool,
                arguments=step.arguments,
                success=True,
                output=output,
            ))
            state.completed_steps.append(step.step_number)
            print(f"    ✓ ok")
        except Exception as e:
            state.step_results.append(StepResult(
                step_number=step.step_number,
                tool=step.tool,
                arguments=step.arguments,
                success=False,
                error=str(e),
            ))
            state.failed_steps.append(step.step_number)
            state.status = "failed"
            print(f"    ✗ {e}")
            return state

    state.status = "completed"
    return state


async def main():
    planner = await get_planner_agent()
    plan = await planner.ainvoke({"request": "help me create a snake game in python"})
    print(f"GOAL: {plan.goal}\n")
    state = await execute_plan(plan)
    print("\n--- final state ---")
    print(state.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
