from typing import Optional, List
from src.tools.tool import ToolKit, ToolSpec
from src.tools.mcp_tools import MCPTools


class ToolRegistry(ToolKit):

    def __init__(
        self,
        tool_specs: Optional[List[ToolSpec]] = None,
        include_tools: List[str] = [],
        exclude_tools: List[str] = [],
    ):
        if tool_specs:
            if include_tools:
                tool_specs = [
                    tool for tool in tool_specs if tool.tool_name in include_tools
                ]
            if exclude_tools:
                tool_specs = [
                    tool for tool in tool_specs if tool.tool_name not in exclude_tools
                ]
        super().__init__(tool_specs if tool_specs else [])

        self.mcp_tools_manager = MCPTools()
        for tool in self.mcp_tools_manager.list_tools():
            if include_tools and tool.tool_name not in include_tools:
                continue

            if exclude_tools and tool.tool_name in exclude_tools:
                continue

            self.add_tool(tool)


if __name__ == "__main__":
    # registry = ToolRegistry(
    #     include_tools=["query-docs"],
    # )
    # print(registry.get_tool_schemas())
    registry = ToolRegistry(
        exclude_tools=["query-docs"],
    )
    print(registry.get_tool_schemas())
