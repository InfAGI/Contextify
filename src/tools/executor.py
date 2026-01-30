import asyncio
from typing import List, Dict
from src.tools.base import Tool, ToolCall, ToolResult


class ToolExecutor:
    """
    Executor class for managing and executing tools.

    This class handles the registration of tools and provides methods to execute
    tool calls either individually, sequentially, or in parallel. It also manages
    the lifecycle of tools, such as closing them when done.
    """

    def __init__(self, tools: List[Tool]):
        """
        Initialize the ToolExecutor with a list of tools.

        Args:
            tools (List[Tool]): A list of Tool instances to be managed by this executor.
        """
        self._tools = tools
        # Create a mapping from tool name to tool instance for quick lookup
        self._tools_map: Dict[str, Tool] = {tool.name: tool for tool in tools}

    async def close_tools(self):
        """
        Close all registered tools that have a close method.

        This method iterates through all tools and calls their `close` method
        if it exists, ensuring resources are properly released.

        Returns:
            list: A list of results from the close operations.
        """
        # Collect all close tasks for tools that implement the close method
        tasks = [tool.close() for tool in self._tools if hasattr(tool, "close")]
        # Execute all close tasks concurrently
        res = await asyncio.gather(*tasks)
        return res

    async def execute_tool_call(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a single tool call.

        Args:
            tool_call (ToolCall): The tool call object containing the tool name and arguments.

        Returns:
            ToolResult: The result of the tool execution, containing output, error, and success status.
        """
        # Check if the requested tool name exists in the registered tools map
        if tool_call.tool_name not in self._tools_map.keys():
            return ToolResult(
                id=tool_call.id,
                error=f"The tool name {tool_call.tool_name} is unavailable. The available tools are: {[tool.name for tool in self._tools]}",
                success=False,
            )

        # Execute the corresponding tool
        return await self._tools_map[tool_call.tool_name].execute(tool_call)

    async def parallel_tool_call(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        Execute multiple tool calls in parallel.

        Args:
            tool_calls (List[ToolCall]): A list of tool calls to execute.

        Returns:
            List[ToolResult]: A list of results corresponding to the tool calls.
        """
        # Use asyncio.gather to run all tool calls concurrently
        return await asyncio.gather(
            *[self.execute_tool_call(call) for call in tool_calls]
        )

    async def sequential_tool_call(
        self, tool_calls: List[ToolCall]
    ) -> List[ToolResult]:
        """
        Execute multiple tool calls sequentially.

        Args:
            tool_calls (List[ToolCall]): A list of tool calls to execute.

        Returns:
            List[ToolResult]: A list of results corresponding to the tool calls.
        """
        # Iterate through tool calls and execute them one by one
        return [await self.execute_tool_call(call) for call in tool_calls]


if __name__ == "__main__":
    from pydantic import BaseModel, Field
    import json

    # Define parameters for a simple calculator tool
    class AddParameters(BaseModel):
        a: int = Field(..., description="The first number")
        b: int = Field(..., description="The second number")

    # Implement a concrete tool
    class AddTool(Tool):
        def __init__(self):
            super().__init__(
                name="add_numbers",
                description="Adds two numbers together",
                parameters=AddParameters,
            )

        async def _execute(self, a: int, b: int) -> ToolResult:
            return ToolResult(output=str(a + b), success=True)

    async def main():
        print("Running ToolExecutor tests...")

        # Initialize the tool and executor
        add_tool = AddTool()
        executor = ToolExecutor(tools=[add_tool])

        # Test 1: Single tool call
        print("\n--- Test 1: Single Tool Call ---")
        tool_call = ToolCall(
            id="call_1",
            tool_name="add_numbers",
            tool_args=json.dumps({"a": 10, "b": 20}),
        )
        result = await executor.execute_tool_call(tool_call)
        print(f"Result: {result.output} (Success: {result.success})")

        # Test 2: Parallel tool calls
        print("\n--- Test 2: Parallel Tool Calls ---")
        calls = [
            ToolCall(
                id="call_2",
                tool_name="add_numbers",
                tool_args=json.dumps({"a": 1, "b": 2}),
            ),
            ToolCall(
                id="call_3",
                tool_name="add_numbers",
                tool_args=json.dumps({"a": 3, "b": 4}),
            ),
        ]
        results = await executor.parallel_tool_call(calls)
        for res in results:
            print(f"ID: {res.id}, Result: {res.output}")

        # Test 3: Error handling (unknown tool)
        print("\n--- Test 3: Unknown Tool ---")
        bad_call = ToolCall(id="call_4", tool_name="subtract_numbers", tool_args="{}")
        result = await executor.execute_tool_call(bad_call)
        print(f"Error: {result.error}")

        await executor.close_tools()

    # Run the async main function
    asyncio.run(main())
