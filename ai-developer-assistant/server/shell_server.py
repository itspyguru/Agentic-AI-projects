from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path
from typing import List
import asyncio

mcp = FastMCP("Shell Server")

ALLOWED_COMMANDS = [
    "ls",
    "pwd",
    "echo",
    "cat",
    "touch",
    "date",
    "history",
    "python"
]

BLOCKED_COMMANDS = [
    "rm",
    "shutdown",
    "reboot",
    "sudo",
    "mkfs",
    "dd"
]

UNSAFE_SHELL_CHARS = [";", "&&", "||", "|", "`", "$("]

async def _run_shell_command(command: str) -> dict:
    parts = command.split()
    if not parts:
        return {"success": False, "error": "empty command"}

    base_command = parts[0]

    if any(token in command for token in UNSAFE_SHELL_CHARS):
        return {"success": False, "error": "unsafe shell characters detected"}

    if base_command in BLOCKED_COMMANDS:
        return {
            "success": False,
            "error": "Permission Denied"
        }

    if base_command not in ALLOWED_COMMANDS:
        return {
            "success": False,
            "error": "command not allowed"
        }


    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=15
        )

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": process.returncode
        }
    except asyncio.TimeoutError:
        process.kill()

        return {
            "success": False,
            "error": "command timed out"
        }

def get_full_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


@mcp.tool
async def run_command(command: str) -> dict:
    """
    Takes a terminal command and excutes it in a sandboxed environment

    Arg:
        command (str): the command to be exeucted in the terminal

    Return:
        Returns the stdout & stderr aafter running it on a terminal
    """

    return await _run_shell_command(command)

    
@mcp.tool
async def get_working_directory() -> dict:
    """
    Get the current working directory

    Arg:
        No arguments needed

    Return:
        Returns the current working directory 
    """

    return await _run_shell_command("pwd")

@mcp.tool
async def run_python_file(path: str) -> dict:
    """
    Run any python file in terminal

    Arg:
        path (str): the filepath of the file to be executed

    Returns:
        Returns the stdout & stderr aafter running it on a terminal
    """

    target = get_full_path(path)
    if not target.exists():
        return {
            "success": False,
            "error": "file does not exist"
        }

    if target.suffix != ".py":
        return {
            "success": False,
            "error": "Only Python files are allowed"
        }

    command = f"python {target}"
    return await _run_shell_command(command)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)