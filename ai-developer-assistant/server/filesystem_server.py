from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pathlib import Path
from typing import List
from datetime import datetime

mcp = FastMCP("FileSystem Server")

def get_full_path(path: str) -> Path:
    return Path(path).expanduser().resolve()

@mcp.tool
def list_files(path: str) -> List[str]:
    """
    Returns the list of all the files in a given directory

    Arg:
        path (str): Path of the folder to scan

    Return:
        Returns a list of filenames in the given folder
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")
    if not target.is_dir():
        raise ToolError(f"Not a directory: {target}")

    return [file.name for file in target.iterdir()]


@mcp.tool
def read_file(path: str) -> str:
    """
    Read the content of the given file

    Arg:
        path (str): take the path of the file to be read

    Return:
        returns the content of the file after reading it.
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")
    if not target.is_file():
        raise ToolError(f"Not a file: {target}")

    return target.read_text()

@mcp.tool
def write_file(path: str, content: str) -> bool:
    """
    Write the given content to a file and saves it.

    Arg:
        path (str): the path of the file
        content (str): the content to be written in the file

    Return:
        Returns True if file is saved with the new content else False
    """

    target = get_full_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return True

@mcp.tool
def search_file_tool(path: str, name: str) -> List[str]:
    """
    Recursively searches for files matching the given name (or glob pattern) under the given directory.

    Arg:
        path (str): the directory to search in
        name (str): exact file name or a glob pattern (e.g. "*.py", "test_*.txt")

    Return:
        List of absolute paths of all matching files. Empty list if nothing matched.
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")
    if not target.is_dir():
        raise ToolError(f"Not a directory: {target}")

    return [str(match) for match in target.rglob(name)]


@mcp.tool
def delete_file(path: str) -> bool:
    """
    Delete a file at the given path.

    Arg:
        path (str): path of the file to delete

    Return:
        True if the file was deleted
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")
    if not target.is_file():
        raise ToolError(f"Not a file: {target}")

    target.unlink()
    return True


@mcp.tool
def create_directory(path: str) -> bool:
    """
    Create a directory (and parent directories if needed).

    Arg:
        path (str): path of the directory to create

    Return:
        True if the directory exists after the call
    """

    target = get_full_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return True


@mcp.tool
def file_info(path: str) -> dict:
    """
    Get metadata about a file or directory.

    Arg:
        path (str): path to inspect

    Return:
        dict with size, mtime, is_dir, is_file
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")

    stat = target.stat()
    return {
        "path": str(target),
        "size": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_file": target.is_file(),
        "is_dir": target.is_dir(),
    }


@mcp.tool
def grep(pattern: str, path: str, recursive: bool = True) -> List[dict]:
    """
    Search for a text pattern inside files.

    Arg:
        pattern (str): text to search for
        path (str): file or directory to search in
        recursive (bool): search subdirectories when path is a directory

    Return:
        list of {file, line_number, line} matches
    """

    target = get_full_path(path)
    if not target.exists():
        raise ToolError(f"Path does not exist: {target}")

    if target.is_file():
        files = [target]
    elif recursive:
        files = [f for f in target.rglob("*") if f.is_file()]
    else:
        files = [f for f in target.iterdir() if f.is_file()]

    matches = []
    for file in files:
        try:
            for i, line in enumerate(file.read_text().splitlines(), start=1):
                if pattern in line:
                    matches.append({
                        "file": str(file),
                        "line_number": i,
                        "line": line,
                    })
        except (UnicodeDecodeError, PermissionError):
            continue

    return matches


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
