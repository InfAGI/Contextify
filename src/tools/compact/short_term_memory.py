from src.llms.agent import Agent
from src.tools.registry import ToolRegistry
from src.tools.text.view_tool import ViewTool
from src.tools.text.edit_tool import CreateFileTool, InsertFileTool, ReplaceFileTool

prompt = """Wait, do not perform any actions other than recording. Please document the key context and task progress in detail based on the previous conversation, following the 5W1H principle for future reference. Key context should be saved in the `.contextify/short_term_memory/context/xxx.md`. Task progress should be saved in the `.contextify/short_term_memory/progress/xxx.md`. After completing the documentation, return a detailed response and do not perform any actions other than recording."""


class ShortTermMemoryManager:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.tools = ToolRegistry(
            [
                ViewTool(),
                CreateFileTool(),
                InsertFileTool(),
                ReplaceFileTool(),
            ],
            include_mcp_tools=False,
        )

    async def solve(self, agent: Agent):
        while True:
            _, tool_calls, content = await agent.invoke()
            if not tool_calls:
                return content

    async def summarize(self):
        agent = self.agent.fork(tools=self.tools)
        agent.append_user_message(prompt)
        result = await self.solve(agent)
        self.agent.messages = [self.agent.messages[0]] + [
            {
                "role": "assistant",
                "content": result,
            }
        ]
        self.agent.print_history()


if __name__ == "__main__":
    import json
    import asyncio

    from src.llms.anthropic import (
        get_anthropic_client,
        get_anthropic_response_with_cache,
    )

    path = """src\\tools\\compact\\messages.json"""

    with open(path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    agent = Agent(
        client=get_anthropic_client(),
        invoke=get_anthropic_response_with_cache,
        messages=messages,
    )

    memory_manager = ShortTermMemoryManager(agent)

    async def main():
        await memory_manager.summarize()

    asyncio.run(main())
