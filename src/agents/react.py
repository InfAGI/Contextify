from src.llms.agent import Agent
from src.utils.log import logger
from src.tools.tool_registry import ToolRegistry


class ReAct:

    def __init__(self, agent: Agent):
        self.agent = agent

    def solve(self, debug=False, max_input_tokens=64 * 1024, feedback=False):

        while True:
            token_nums = self.agent.calc_token_nums()
            if token_nums > max_input_tokens:
                logger.warning(
                    f"Token nums {token_nums} exceeds max input tokens {max_input_tokens}"
                )
                # self.report()

            self.agent.print_history()
            logger.info(f"Token nums: {token_nums}")

            if debug:
                input("Press Enter to continue...")

            _, tool_calls, content = self.agent.invoke()
            if not tool_calls:
                logger.info(f"Final answer: {content}")
                if feedback:
                    res = input("Please provide feedback: ").strip()
                    if res:
                        self.agent.append_user_message(res)
                        continue
                return content


if __name__ == "__main__":
    from src.tools.bash.bash_tool import BashTool

    bash_tool = BashTool()
    tool_kit = ToolRegistry([bash_tool.get_spec()])
    agent = Agent(tools=tool_kit)

    agent.append_user_message("""深度调研一下代码库的目录结构,即: src目录下。不包括.conda、.log、.git、__pycache__等目录""")

    react = ReAct(agent=agent)
    react.solve(debug=False)

    bash_tool.deinit()
