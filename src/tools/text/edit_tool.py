from pydantic import BaseModel, Field
from typing import override
from pathlib import Path

from src.tools.text.write_file import write_file
from src.tools.text.insert_file import insert_file
from src.tools.text.replace_file import replace_file
from src.tools.base import Tool, ToolResult


class CreateFileArgs(BaseModel):
    file_path: str = Field(description="Absolute path to file, e.g. `/repo/file.py`.")
    file_text: str = Field(description="The content of the file to be created.")


class InsertFileArgs(BaseModel):
    file_path: str = Field(description="Absolute path to file, e.g. `/repo/file.py`.")
    insert_line: int = Field(description="The line number to insert the file text.")
    file_text: str = Field(
        description="The content of the file to be inserted after the `insert_line` of `file_path`."
    )


class ReplaceFileArgs(BaseModel):
    file_path: str = Field(description="Absolute path to file, e.g. `/repo/file.py`.")
    old_content: str = Field(
        description="The old content to be replaced in `file_path`."
    )
    new_content: str = Field(
        description="The new content to replace the `old_content` in `file_path`.",
    )


class CreateFileTool(Tool):

    def __init__(self):
        super().__init__(
            name="create_file",
            description="Creates a file at the specified path with the given content.",
            parameters=CreateFileArgs,
        )

    @override
    async def _execute(self, file_path: str, file_text: str) -> ToolResult:
        file_path = Path(file_path)
        if file_path.exists():
            return ToolResult(
                error=f"File {file_path} already exists.",
                success=False,
            )

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        return ToolResult(
            output=write_file(file_path, "", file_text),
            success=True,
        )


class InsertFileTool(Tool):

    def __init__(self):
        super().__init__(
            name="insert_file",
            description="Inserts the given content after the specified line number in the file.",
            parameters=InsertFileArgs,
        )

    @override
    async def _execute(
        self, file_path: str, insert_line: int, file_text: str
    ) -> ToolResult:
        file_path = Path(file_path)
        return ToolResult(
            output=insert_file(file_path, file_text, insert_line),
            success=True,
        )


class ReplaceFileTool(Tool):

    def __init__(self):
        super().__init__(
            name="replace_file",
            description="Replaces the old content with the new content in the file.",
            parameters=ReplaceFileArgs,
        )

    @override
    async def _execute(
        self, file_path: str, old_content: str, new_content: str
    ) -> ToolResult:
        file_path = Path(file_path)
        return ToolResult(
            output=replace_file(file_path, old_content, new_content),
            success=True,
        )


if __name__ == "__main__":
    from src.utils.loop import run_async_in_thread

    create_tool = CreateFileTool()
    print(
        run_async_in_thread(
            create_tool._execute,
            file_path="test/test.py",
            file_text="print('Hello, World!')",
        )
    )

    insert_tool = InsertFileTool()
    print(
        run_async_in_thread(
            insert_tool._execute,
            file_path="test/test.py",
            insert_line=1,
            file_text="print('Hello, World!xxxx')",
        )
    )

    replace_tool = ReplaceFileTool()
    print(
        run_async_in_thread(
            replace_tool._execute,
            file_path="test/test.py",
            old_content="print('Hello, World!xxxx')",
            new_content="print('Hello, World!yyyy')",
        )
    )
