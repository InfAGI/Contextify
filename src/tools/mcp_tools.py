import asyncio
from typing import List, Dict
from fastmcp import Client
from src.config.config import DefaultConfig
from src.tools.tool import ToolSpec


class MCPTools:
    def __init__(self):
        self.client = Client({"mcpServers": DefaultConfig.mcp_servers})

    def call_tool(self, tool_name: str, tool_args: Dict) -> str:
        async def _call_tool():
            async with self.client:
                result = await self.client.call_tool(tool_name, tool_args)
                return str(result)

        return asyncio.run(_call_tool())

    def list_tools(self) -> List[ToolSpec]:
        async def _list_tools():
            async with self.client:
                return await self.client.list_tools()

        return [
            ToolSpec(
                tool_name=tool.name,
                tool_desc=tool.description,
                tool_args=tool.inputSchema,
                tool_callback=self.call_tool,
            )
            for tool in asyncio.run(_list_tools())
        ]


if __name__ == "__main__":
    mcp_tools = MCPTools()
    tools = mcp_tools.list_tools()
    for tool in tools:
        print(f"工具名: {tool.tool_name}")
        print(f"工具描述: {tool.tool_desc}")
        print(f"输入模式: {tool.tool_args}")

    # res = mcp_tools.call_tool(
    #     tool_name="resolve-library-id",
    #     tool_args={"query": "如何使用mcp client?", "libraryName": "fastmcp"},
    # )
    # print(res)

    res = mcp_tools.call_tool(
        tool_name="query-docs",
        tool_args={"query": "如何使用mcp client?", "libraryId": "/jlowin/fastmcp"},
    )
    print(res)
