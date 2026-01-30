from pydantic import BaseModel, Field
from typing import override
from pathlib import Path

from src.tools.text.view_dir import view_directory
from src.tools.text.read_file import read_file
from src.tools.base import Tool, ToolResult


class ViewArgs(BaseModel):
    path: str = Field(
        description="Absolute path to file or directory, e.g. `/repo/file.py` or `/repo`."
    )
    start_line: int = Field(
        default=1,
        description="The start line number to read from. 1 means the first line.",
    )
    end_line: int = Field(
        default=-1,
        description="The end line number to read to. -1 means the last line.",
    )


class ViewTool(Tool):

    def __init__(self):
        super().__init__(
            name="view",
            description="Views the content of a file or directory tree. If the path is a directory, it will view the directory tree. If the path is a file, it will view the file content.",
            parameters=ViewArgs,
        )

    @override
    async def _execute(
        self, path: str, start_line: int = 1, end_line: int = -1
    ) -> ToolResult:
        if Path(path).is_dir():
            return ToolResult(
                output=view_directory(Path(path)),
                success=True,
            )
        return ToolResult(
            output=read_file(Path(path), start_line, end_line),
            success=True,
        )


if __name__ == "__main__":
    from src.utils.loop import run_async_in_thread

    view_tool = ViewTool()
    print(run_async_in_thread(view_tool._execute, path="."))
    print(run_async_in_thread(view_tool._execute, path="src/tools/text/view_tool.py", start_line=1, end_line=10))
