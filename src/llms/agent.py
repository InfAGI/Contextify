import json
import copy
from src.llms.deepseek import get_deepseek_client, get_deepseek_response
from src.tools.registry import ToolRegistry
from src.utils.util import num_tokens
from src.utils.log import logger
from src.tools.base import ToolCall
from src.utils.tracer import Tracer


class Agent:

    def __init__(
        self,
        client=get_deepseek_client(),
        invoke=get_deepseek_response,
        messages: list = None,
        tools: ToolRegistry = None,
        tracer: Tracer = None,
    ):
        self._client = client
        self._invoke = invoke
        self._tracer = tracer

        if messages:
            self.messages = messages
        else:
            self.messages = []

        if tools:
            self.tools = tools
        else:
            self.tools = ToolRegistry(tools=[], include_mcp_tools=False)

    def fork(self, tools: ToolRegistry = None):
        return Agent(
            client=self._client,
            invoke=self._invoke,
            messages=copy.deepcopy(self.messages),
            tools=tools,
        )

    def calc_token_nums(self):
        token_nums = 0
        for message in self.messages:
            if "reasoning_content" in message and message["reasoning_content"]:
                token_nums += num_tokens(message["reasoning_content"])
            if "content" in message and message["content"]:
                token_nums += num_tokens(message["content"])
            if "tool_calls" in message and message["tool_calls"]:
                token_nums += num_tokens(
                    json.dumps(message["tool_calls"], ensure_ascii=False)
                )
        return token_nums

    def set_system_prompt(self, prompt):
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})

    def append_user_message(self, input):
        self.messages.append({"role": "user", "content": input})
        logger.info(f"Agent received input: {input}\n")
        if self._tracer:
            self._tracer.trace({"role": "user", "content": input})

    def append_message(self, msg):
        self.messages.append(msg)
        if self._tracer:
            self._tracer.trace(msg)

    async def invoke(self, input=None):
        if input:
            self.append_user_message(input)

        response = self._invoke(
            client=self._client,
            messages=self.messages,
            tools=self.tools.get_tool_schemas(),
        )

        message = {
            "role": "assistant",
        }
        if hasattr(response.choices[0].message, "content"):
            if response.choices[0].message.content:
                content = response.choices[0].message.content
                message["content"] = content
            else:
                content = None

        if hasattr(response.choices[0].message, "reasoning_content"):
            reasoning_content = response.choices[0].message.reasoning_content
            message["reasoning_content"] = reasoning_content
        else:
            reasoning_content = None

        if hasattr(response.choices[0].message, "tool_calls"):
            if response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls
            else:
                tool_calls = None
        else:
            tool_calls = None

        if tool_calls:
            message["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in tool_calls
            ]
        self.append_message(message)
        logger.info(f"Agent produced response: {message}")

        if reasoning_content:
            logger.info(f"Agent produced reasoning_content: {reasoning_content}")

        if tool_calls:
            logger.info(f"Agent produced tool_calls: {tool_calls}")
            for tool_call in tool_calls:
                tool_result = str(
                    await self.tools.execute_tool_call(
                        ToolCall(
                            id=tool_call.id,
                            tool_name=tool_call.function.name,
                            tool_args=tool_call.function.arguments,
                        )
                    )
                )

                self.append_message(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                )

                logger.info(
                    f"The tool {tool_call.function.name} produced result: {tool_result}"
                )

        if content:
            logger.info(f"Agent produced content: {content}")

        return reasoning_content, tool_calls, content

    def clear_reasoning_content(self):
        for message in self.messages:
            if hasattr(message, "reasoning_content"):
                message.reasoning_content = None

    def print_history(self):
        for i, msg in enumerate(self.messages):
            logger.info(f"Message {i}: {msg}\n")

    def remove_last_k_messages(self, k: int):
        self.messages = self.messages[:-k]


if __name__ == "__main__":
    import asyncio

    from src.tools.bash.bash_tool import BashTool
    from src.tools.text.view_tool import ViewTool
    from src.tools.text.edit_tool import CreateFileTool, InsertFileTool, ReplaceFileTool

    async def main():
        tool_registry = ToolRegistry(
            [
                BashTool(cwd="C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"),
                ViewTool(),
                CreateFileTool(),
                InsertFileTool(),
                ReplaceFileTool(),
            ]
        )
        agent = Agent(tools=tool_registry, tracer=Tracer(".cache/trace/tracer.txt"))
        await agent.invoke(
            "查看一下当前工作空间的目录结构.C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"
        )
        agent.print_history()
        await tool_registry.close_tools()

    asyncio.run(main())
