"""
This module provides the TodoTool class for managing todo lists associated with specific sessions.

Functionality:
    - Manages persistence of Todo items to a JSON file.
    - files are stored in `.contextify/todos/{session_id}.json`.
    - Provides methods to read and write the todo list.

Usage:
    tool = TodoTool(session_id="my-session")
    todos = tool._read_todo_list()
    tool._write_todo_list(todos)
"""

from typing import Literal, override
from pydantic import BaseModel, Field
import json
import os
from typing import List, Optional
from src.tools.plan.todo import Todo
from src.tools.base import Tool, ToolResult
from src.utils.log import logger


class TodoArgs(BaseModel):
    command: Literal["read_todo", "write_todo"] = Field(
        description="The command to operate on the todo list, either 'read_todo' or 'write_todo'"
    )
    todos: Optional[List[Todo]] = Field(
        default=[],
        description="If command is 'write_todo', the whole list of todo items to operate on",
    )


class TodoTool(Tool):
    """
    A tool for managing Todo lists for a specific session.
    """

    def __init__(
        self,
        session_id: str,
        base_path: str = os.path.join(".cache", "todos"),
    ):
        """
        Initialize the TodoTool with a session ID.

        Args:
            session_id (str): The unique identifier for the session.
            base_path (str): The base directory to store todo files. Defaults to '.cache/todos'.
        """
        self.session_id = session_id
        self.base_path = base_path
        self._ensure_storage_directory()
        self.file_path = self._get_file_path()
        super().__init__(
            name="manage_todo",
            description="Manage todo lists",
            parameters=TodoArgs,
        )

    def _ensure_storage_directory(self):
        """Ensures the storage directory exists."""
        if os.path.isabs(self.base_path):
            self.base_dir = self.base_path
        else:
            self.base_dir = os.path.join(os.getcwd(), self.base_path)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_file_path(self) -> str:
        """Returns the full path to the todo file."""
        return os.path.join(self.base_dir, f"{self.session_id}.json")

    def _read_todo_list(self) -> List[Todo]:
        """
        Reads the todo list from the storage file.

        Returns:
            List[Todo]: A list of Todo objects. Returns an empty list if the file doesn't exist or is invalid.
        """
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
            return [Todo.model_validate(item) for item in json.loads(content)]

    def _write_todo_list(self, todos: List[Todo]):
        """
        Writes the todo list to the storage file.

        Args:
            todos (List[Todo]): The list of Todo objects to save.
        """
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in todos], f, indent=4, ensure_ascii=False)

    @override
    async def _execute(self, **kwargs) -> ToolResult:
        args = TodoArgs.model_validate(kwargs)
        if args.command == "read_todo":
            todos = self._read_todo_list()
            return ToolResult(
                success=True,
                output=json.dumps(
                    [t.model_dump() for t in todos], ensure_ascii=False, indent=4
                ),
            )
        elif args.command == "write_todo":
            self._write_todo_list(args.todos)
            return ToolResult(success=True, output="Todo list updated successfully")


if __name__ == "__main__":
    from src.tools.registry import ToolRegistry
    from src.tools.base import ToolCall

    tool = TodoTool(session_id="my-session")
    # todos = tool._read_todo_list()
    # logger.info(todos)
    # test_todos = [
    #     Todo(
    #         status="pending",
    #         context="Complete the documentation",
    #         priority="high",
    #         progress="0%",
    #     ),
    #     Todo(
    #         status="pending",
    #         context="Add unit tests",
    #         priority="medium",
    #         progress="0%",
    #     ),
    # ]
    # tool._write_todo_list(test_todos)
    # todos = tool._read_todo_list()
    # logger.info(todos)

    # Test the tool with the new methods
    # result = tool._execute(command="read_todo")
    # logger.info(result)
    # result = tool._execute(
    #     command="write_todo",
    #     todos=[
    #         Todo(
    #             status="pending",
    #             context="Review the code",
    #             priority="low",
    #             progress="3%",
    #         )
    #     ],
    # )
    # logger.info(result)
    # todos = tool._read_todo_list()
    # logger.info(todos)

    import asyncio

    async def test_tool():
        registry = ToolRegistry(tools=[tool], include_mcp_tools=False)
        res = await registry.execute_tool_call(
            tool_call=ToolCall(
                id="1",
                tool_name="manage_todo",
                tool_args=json.dumps(
                    {
                        "command": "read_todo",
                    }
                ),
            )
        )
        print(res)
        res = await registry.execute_tool_call(
            tool_call=ToolCall(
                id="2",
                tool_name="manage_todo",
                tool_args=json.dumps(
                    {
                        "command": "write_todo",
                        "todos": [
                            {
                                "status": "pending",
                                "context": "Review the code",
                                "priority": "low",
                                "progress": "6%",
                            }
                        ],
                    }
                ),
            )
        )
        print(res)

        res = await registry.execute_tool_call(
            tool_call=ToolCall(
                id="3",
                tool_name="manage_todo",
                tool_args=json.dumps(
                    {
                        "command": "read_todo",
                    }
                ),
            )
        )
        print(res)

    asyncio.run(test_tool())
