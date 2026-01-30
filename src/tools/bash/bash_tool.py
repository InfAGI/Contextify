from pydantic import BaseModel, Field
from typing import override

from src.tools.base import Tool, ToolResult
from src.tools.bash.bash_terminal import BashTerminal


class BashArgs(BaseModel):
    command: str = Field(description="The bash command to execute.")
    restart: bool = Field(
        default=False, description="Set to true to restart the bash session."
    )


class BashTool(Tool):

    def __init__(self, cwd: str = None):
        self._terminal = BashTerminal(cwd)
        super().__init__(
            name="bash",
            description="Executes a given bash command in a persistent shell session and returns the stdout and stderr.",
            parameters=BashArgs,
        )

    @override
    async def close(self):
        await self._terminal.stop()

    @override
    async def _execute(self, command: str, restart: bool = False) -> ToolResult:
        if restart and self._terminal:
            await self._terminal.stop()

        output, stderr = await self._terminal.run(command)

        return ToolResult(
            output=output,
            error=stderr,
            success=not stderr,
        )


if __name__ == "__main__":
    import asyncio
    from src.tools.registry import ToolRegistry
    from src.tools.base import ToolCall

    async def main():
        tool = BashTool()
        # registry expects a list of Tool instances
        tool_registry = ToolRegistry(tools=[tool])

        # Test 1: Simple echo command
        print("-" * 50)
        print("Test 1: Simple echo command")
        res = await tool_registry.execute_tool_call(
            ToolCall(tool_name="bash", tool_args='{"command":"echo \'Hello, World!\'"}')
        )
        print(res)

        # Test 2: List directory contents
        # Note: On Windows PowerShell, 'ls -la' might fail, using 'ls' or 'dir'
        print("\n" + "-" * 50)
        print("Test 2: List directory contents")
        res = await tool_registry.execute_tool_call(
            ToolCall(tool_name="bash", tool_args='{"command":"dir"}')
        )
        print(res)

        # Test 3: Check current working directory
        print("\n" + "-" * 50)
        print("Test 3: Check current working directory")
        res = await tool_registry.execute_tool_call(
            ToolCall(tool_name="bash", tool_args='{"command":"pwd"}')
        )
        print(res)

        # Test 4: Error handling (file not found)
        print("\n" + "-" * 50)
        print("Test 4: Error handling")
        res = await tool_registry.execute_tool_call(
            ToolCall(
                tool_name="bash", tool_args='{"command":"cat non_existent_file.txt"}'
            )
        )
        print(res)

        # Test 5: Restart session
        print("\n" + "-" * 50)
        print("Test 5: Restart session")
        res = await tool_registry.execute_tool_call(
            ToolCall(
                tool_name="bash",
                tool_args='{"command":"echo \'Restarting session...\'", "restart":true}',
            )
        )
        print(res)

        # Cleanup
        await tool_registry.close_tools()

    asyncio.run(main())
