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
    ):
        tools.extend(MCPTools().list_tools())

        if tools:
            if include_tools:
                tools = [tool for tool in tools if tool.get_name() in include_tools]
            if exclude_tools:
                tools = [tool for tool in tools if tool.get_name() not in exclude_tools]

        super().__init__(tools=tools)


if __name__ == "__main__":
    registry = ToolRegistry()
    print(registry.get_tool_schemas())
