import asyncio
from typing import List, Dict, Optional
from fastmcp import Client
from src.config.config import DefaultConfig
from src.tools.base import Tool, ToolResult


class MCPTools:
    """
    Manager for Model Context Protocol (MCP) tools.

    This class handles the connection to MCP servers and converts the available
    MCP tools into Contextify Tool instances. It acts as a bridge between
    the MCP ecosystem and the Contextify tool system.
    """

    def _create_tool_callback(self, tool_name: str):
        """
        Create a callback function for a specific tool.

        Args:
            tool_name (str): The name of the tool.

        Returns:
            Callable: The callback function to execute the tool.
        """

        async def callback(args: Dict) -> ToolResult:
            try:
                # The client context manager handles the connection lifecycle
                async with self.client:
                    result = await self.client.call_tool(tool_name, args)
                return ToolResult(output=str(result), success=True)
            except Exception as e:
                return ToolResult(error=str(e), success=False)

        return callback

    def __init__(self):
        """
        Initialize the MCPTools manager.

        Sets up the MCP client using the servers configured in DefaultConfig.
        """
        self.client: Optional[Client] = None
        if DefaultConfig.mcp_servers:
            self.client = Client({"mcpServers": DefaultConfig.mcp_servers})

    def list_tools(self) -> List[Tool]:
        """
        List available tools from the configured MCP servers.

        Connects to the MCP servers, retrieves the list of tools, and wraps them
        in Tool instances with a closure callback.

        Returns:
            List[Tool]: A list of available tools. Returns an empty list if no servers
            are configured or if an error occurs.
        """
        if not self.client:
            return []

        async def _list_tools():
            async with self.client:
                return await self.client.list_tools()

        try:
            # Check if there is a running event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # If we are in a running loop, run in a separate thread
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    tools = executor.submit(asyncio.run, _list_tools()).result()
            else:
                tools = asyncio.run(_list_tools())
        except Exception:
            return []

        return [
            Tool(
                name=tool.name,
                description=tool.description,
                parameters=tool.inputSchema,
                callback=self._create_tool_callback(tool.name),
            )
            for tool in tools
        ]


if __name__ == "__main__":
    mcp_tools = MCPTools()
    tools = mcp_tools.list_tools()
    for tool in tools:
        print(f"Tool Name: {tool.get_name()}")
        print(f"Tool Description: {tool.get_description()}")
        print(f"Input Schema: {tool.parameters}")
