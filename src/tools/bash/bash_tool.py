from pydantic import BaseModel, Field
import asyncio

from src.tools.tool import ToolSpec
from src.tools.bash.bash_terminal import BashTerminal


class BashArgs(BaseModel):
    command: str = Field(description="The bash command to execute.")


class BashTool:

    def __init__(self, cwd: str = None):
        self._terminal = BashTerminal(cwd)
        self._loop = asyncio.new_event_loop()

    def deinit(self):
        try:
            self._loop.run_until_complete(self._terminal.stop())
        finally:
            self._loop.close()

    def execute(self, command: str):
        return self._loop.run_until_complete(self._terminal.run(command))

    def get_spec(self):
        return ToolSpec(
            tool_name="bash",
            tool_desc="Executes a given bash command in a persistent shell session and returns the stdout and stderr.",
            tool_args=BashArgs,
            tool_callback=self.execute,
        )


if __name__ == "__main__":
    from src.tools.tool_registry import ToolRegistry
    from src.tools.tool import ToolCall

    tool = BashTool()
    tool_spec = tool.get_spec()
    tool_registry = ToolRegistry()
    tool_registry.add_tool(tool_spec)

    # res = tool_registry.execute_tool(
    #     ToolCall(tool_name="bash", tool_args='{"command":"pwd"}')
    # )
    res = tool_registry.execute_tool(
        ToolCall(tool_name="bash", tool_args='{"command":"cat src/utils/log.py"}')
    )
    print(res)

    tool.deinit()
