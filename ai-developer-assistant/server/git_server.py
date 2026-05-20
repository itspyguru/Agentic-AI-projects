from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path
from typing import List
import asyncio

mcp = FastMCP("Git Server")


def get_full_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


async def _run_git(args: List[str], repo: str = ".") -> dict:
    target = get_full_path(repo)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")

    command = ["git", "-C", str(target), *args]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=15,
        )
    except asyncio.TimeoutError:
        process.kill()
        return {"success": False, "error": "git command timed out"}

    return {
        "success": process.returncode == 0,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "returncode": process.returncode,
    }


@mcp.tool
async def git_status(repo: str = ".") -> dict:
    """
    Get git status in porcelain format.

    Arg:
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["status", "--porcelain"], repo)


@mcp.tool
async def git_log(n: int = 10, repo: str = ".") -> dict:
    """
    Get the most recent commits.

    Arg:
        n (int): number of commits to show
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["log", f"-n{n}", "--oneline"], repo)


@mcp.tool
async def git_diff(staged: bool = False, repo: str = ".") -> dict:
    """
    Show changes in the working tree or index.

    Arg:
        staged (bool): if True, show staged changes
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    args = ["diff"]
    if staged:
        args.append("--staged")
    return await _run_git(args, repo)


@mcp.tool
async def git_branch_list(repo: str = ".") -> dict:
    """
    List all branches.

    Arg:
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["branch", "--all"], repo)


@mcp.tool
async def git_current_branch(repo: str = ".") -> dict:
    """
    Get the name of the current branch.

    Arg:
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["branch", "--show-current"], repo)


@mcp.tool
async def git_show(commit: str, repo: str = ".") -> dict:
    """
    Show details of a commit.

    Arg:
        commit (str): commit hash or reference
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["show", commit], repo)


@mcp.tool
async def git_blame(path: str, line: int, repo: str = ".") -> dict:
    """
    Show who last changed a specific line in a file.

    Arg:
        path (str): file path inside the repo
        line (int): line number to blame
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    return await _run_git(["blame", "-L", f"{line},{line}", path], repo)


@mcp.tool
async def git_add(paths: List[str], repo: str = ".") -> dict:
    """
    Stage one or more paths.

    Arg:
        paths (list[str]): files or directories to stage
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    if not paths:
        return {"success": False, "error": "no paths provided"}
    return await _run_git(["add", *paths], repo)


@mcp.tool
async def git_commit(message: str, repo: str = ".") -> dict:
    """
    Create a commit with the given message.

    Arg:
        message (str): commit message
        repo (str): path of the repository

    Return:
        dict with stdout, stderr, returncode
    """
    if not message.strip():
        return {"success": False, "error": "empty commit message"}
    return await _run_git(["commit", "-m", message], repo)


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
