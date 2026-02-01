from pydantic import BaseModel, Field
from typing import override
from src.tools.base import Tool, ToolResult


class AskHumanForHelpArgs(BaseModel):
    help: str = Field(description="The help message to ask the human.")


class AskHumanForHelpTool(Tool):

    def __init__(self):
        super().__init__(
            name="ask_human_help",
            description="Ask human for help.",
            parameters=AskHumanForHelpArgs,
        )

    @override
    async def _execute(self, help: str) -> ToolResult:
        res = input(f"Human Help: {help}\n")
        return ToolResult(
            output=res,
            success=True,
        )


if __name__ == "__main__":
    from src.utils.loop import run_async_in_thread

    ask_human_tool = AskHumanForHelpTool()
    print(
        run_async_in_thread(
            ask_human_tool._execute,
            help="What is the meaning of life?",
        )
    )
