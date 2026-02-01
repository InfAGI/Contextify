from typing import Optional, List
from src.tools.base import Tool
from src.tools.executor import ToolExecutor
from src.tools.mcp_tool import MCPTools



class ToolRegistry(ToolExecutor):

    def __init__(
        self,
        tools: Optional[List[Tool]] = [],
        include_tools: List[str] = [],
        exclude_tools: List[str] = [],
        include_mcp_tools: bool = True,
    ):
        if include_mcp_tools:
            tools.extend(MCPTools().list_tools())

        if tools:
            if include_tools:
                tools = [tool for tool in tools if tool.get_name() in include_tools]
            if exclude_tools:
                tools = [tool for tool in tools if tool.get_name() not in exclude_tools]

        super().__init__(tools=tools)


if __name__ == "__main__":
    import json
    import asyncio
    import os
    from src.tools.base import ToolCall

    async def main():
        registry = ToolRegistry(include_mcp_tools=False)
        print("Tool Schemas:")
        print(json.dumps(registry.get_tool_schemas(), indent=4))
        print("\n" + "=" * 50 + "\n")

        # 1. Test BashTool
        print("Testing BashTool...")
        res = await registry.execute_tool_call(
            ToolCall(tool_name="bash", tool_args='{"command": "echo Hello from Bash"}')
        )
        print(f"Result: {res.output}")
        print("-" * 20)

        # 2. Test CreateFileTool
        test_file = os.path.abspath("test_temp_file.txt")
        print(f"Testing CreateFileTool ({test_file})...")
        res = await registry.execute_tool_call(
            ToolCall(
                tool_name="create_file",
                tool_args=json.dumps(
                    {"file_path": test_file, "file_text": "Line 1\nLine 2\nLine 3"}
                ),
            )
        )
        print(f"Result: {res.output}")
        print("-" * 20)

        # 3. Test ViewTool
        print("Testing ViewTool...")
        res = await registry.execute_tool_call(
            ToolCall(tool_name="view", tool_args=json.dumps({"path": test_file}))
        )
        print(f"Result:\n{res.output}")
        print("-" * 20)

        # 4. Test ReplaceFileTool
        print("Testing ReplaceFileTool...")
        res = await registry.execute_tool_call(
            ToolCall(
                tool_name="replace_file",
                tool_args=json.dumps(
                    {
                        "file_path": test_file,
                        "old_content": "Line 2",
                        "new_content": "Line 2 (Modified)",
                    }
                ),
            )
        )
        print(f"Result: {res.output}")

        # Verify modification
        res = await registry.execute_tool_call(
            ToolCall(tool_name="view", tool_args=json.dumps({"path": test_file}))
        )
        print(f"New Content:\n{res.output}")
        print("-" * 20)

        # 5. Test InsertFileTool
        print("Testing InsertFileTool...")
        res = await registry.execute_tool_call(
            ToolCall(
                tool_name="insert_file",
                tool_args=json.dumps(
                    {
                        "file_path": test_file,
                        "insert_line": 3,
                        "file_text": "Line 4 (Inserted)",
                    }
                ),
            )
        )
        print(f"Result: {res.output}")

        # Verify insertion
        res = await registry.execute_tool_call(
            ToolCall(tool_name="view", tool_args=json.dumps({"path": test_file}))
        )
        print(f"New Content:\n{res.output}")
        print("-" * 20)

        # Cleanup
        print("Cleaning up...")
        try:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"Removed {test_file}")
        except Exception as e:
            print(f"Error removing file: {e}")

        await registry.close_tools()

    asyncio.run(main())
