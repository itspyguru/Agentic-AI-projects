import os
import json
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from agent.workspace_agent import get_workspace_agent
from agent.planner_agent import get_planner_agent, ExecutionPlan
from agent.executor_agent import execute_plan as run_plan, ExecutionState, StepResult

load_dotenv()


async def get_orchestrator():
    workspace_agent = await get_workspace_agent()
    planner = await get_planner_agent()

    @tool
    async def plan_task(request: str) -> str:
        """Generate a step-by-step execution plan for a development request. Returns the plan as JSON."""
        print("*------- Creating User Plan ----------------* ")
        plan = await planner.ainvoke({"request": request})
        print("*------- User Plan Created ----------------* ")
        full_plan = plan.model_dump_json()
        print(full_plan)
        return full_plan

    @tool
    async def execute_plan(plan_json: str) -> str:
        """Run a plan (JSON produced by plan_task) deterministically by calling the named MCP tools in order. Returns an ExecutionState JSON with status, completed_steps, failed_steps, and per-step results."""
        print("* -------- Executing plans ------------------* ")
        plan = ExecutionPlan.model_validate_json(plan_json)
        state = await run_plan(plan)
        print(f"* -------- Status: {state.status} "
              f"(done: {len(state.completed_steps)}, failed: {len(state.failed_steps)}) ----* ")
        return state.model_dump_json()

    @tool
    async def workspace(query: str) -> str:
        """Delegate a filesystem, shell, or git task to the workspace agent using a natural-language instruction. Use this when a step needs judgment or to recover from a failed deterministic step."""
        result = await workspace_agent.ainvoke({"messages": [("user", query)]})
        return result["messages"][-1].text()

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )
    return create_agent(
        model=llm,
        tools=[plan_task, execute_plan, workspace],
        system_prompt=(
            "You are the orchestrator for a developer assistant. You coordinate specialist sub-agents to fulfill the user's request.\n\n"
            "Default workflow for any development task:\n"
            "1. Call `plan_task` with the user's request to produce a structured plan.\n"
            "2. Run the plan with `execute_plan` for fast, deterministic execution. It returns an ExecutionState JSON with fields: status ('completed' | 'failed'), current_step, completed_steps, failed_steps, step_results.\n"
            "3. Inspect the returned state. If `status` is 'failed', look at the last entry in `step_results` (its `tool`, `arguments`, and `error`) and delegate that specific step to `workspace` with a natural-language instruction.\n\n"
            "For simple one-shot tasks (e.g. 'show me git status'), you may skip planning and call `workspace` directly.\n"
            "Always summarize the final result for the user — do not just dump tool output."
        ),
    )

async def main():
    orc_agent = await get_orchestrator()
    result = await orc_agent.ainvoke({
        "messages": [
            ("user", "help me create a snake game using python. create a new folder for this project."),
        ],
    })
    print(result["messages"][-1].text())


if __name__ == "__main__":
    asyncio.run(main())