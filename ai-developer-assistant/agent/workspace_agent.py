import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

load_dotenv()

SERVER_DIR = Path(__file__).resolve().parent.parent / "server"
FILESYSTEM_SERVER = str(SERVER_DIR / "filesystem_server.py")
SHELL_SERVER = str(SERVER_DIR / "shell_server.py")
GIT_SERVER = str(SERVER_DIR / "git_server.py")

async def get_workspace_agent():
    client = MultiServerMCPClient({
        "filesystem": {
            "command": "python",
            "args": [FILESYSTEM_SERVER],
            "transport": "stdio",
        },
        "shell": {
            "command": "python",
            "args": [SHELL_SERVER],
            "transport": "stdio",
        },
        "git": {
            "command": "python",
            "args": [GIT_SERVER],
            "transport": "stdio",
        },
    })

    tools = await client.get_tools()
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a workspace assistant. You can list, read, write, and delete files, "
            "inspect file metadata, search file contents, run sandboxed shell commands, "
            "execute Python files, and run git operations (status, log, diff, branches, "
            "show, blame, add, commit) on the user's workspace."
        ),
    )
