from src.llms.agent import Agent
from src.utils.log import logger
from src.tools.registry import ToolRegistry
from src.tools.text.view_tool import ViewTool
from src.tools.text.edit_tool import CreateFileTool, InsertFileTool, ReplaceFileTool
from src.tools.compact.short_term_memory import ShortTermMemoryManager


class ReAct:

    def __init__(self, agent: Agent):
        self.agent = agent
        self.memory_manager = ShortTermMemoryManager(agent)

    async def solve(self, debug=False, max_input_tokens=64 * 1024, feedback=False):

        while True:
            token_nums = self.agent.calc_token_nums()
            if token_nums > max_input_tokens:
                logger.warning(
                    f"Token nums {token_nums} exceeds max input tokens {max_input_tokens}"
                )
                await self.memory_manager.summarize()

            self.agent.print_history()
            logger.info(f"Token nums: {token_nums}")

            if debug:
                input("Press Enter to continue...")

            _, tool_calls, content = await self.agent.invoke()
            if not tool_calls:
                logger.info(f"Final answer: {content}")
                if feedback:
                    res = input("Please provide feedback: ").strip()
                    if res:
                        self.agent.append_user_message(res)
                        continue
                return content


if __name__ == "__main__":
    import asyncio

    from src.tools.bash.bash_tool import BashTool
    from src.tools.text.view_tool import ViewTool
    from src.tools.text.edit_tool import CreateFileTool, InsertFileTool, ReplaceFileTool

    from src.llms.anthropic import (
        get_anthropic_client,
        get_anthropic_response_with_cache,
    )
    from src.llms.deepseek import (
        get_deepseek_client,
        get_deepseek_response_with_cache,
    )

    async def main():
        tool_registry = ToolRegistry(
            [
                BashTool(cwd="C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"),
                ViewTool(),
                CreateFileTool(),
                InsertFileTool(),
                ReplaceFileTool(),
            ],
            include_mcp_tools=False,
        )
        agent = Agent(
            tools=tool_registry,
            # client=get_anthropic_client(),
            # invoke=get_anthropic_response_with_cache,
            client=get_deepseek_client(),
            invoke=get_deepseek_response_with_cache,
        )
        agent.append_user_message(
            """为该仓库生成compose.yaml文件并用docker部署. C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"""
        )
        # agent.append_user_message(
        #     """深度调研一下这个代码仓库. C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"""
        # )
        react = ReAct(agent=agent)
        try:
            await react.solve(debug=False)
        finally:
            await tool_registry.close_tools()

    asyncio.run(main())
