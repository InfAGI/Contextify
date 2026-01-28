import json
from typing import Type, Callable, List, Dict
from pydantic import BaseModel, Field


def is_pydantic_model(obj):
    return isinstance(obj, type) and issubclass(obj, BaseModel)


class ToolCall(BaseModel):
    tool_name: str
    tool_args: str


class ToolSpec(BaseModel):
    tool_name: str
    tool_desc: str
    tool_args: Type[BaseModel] | Dict
    tool_callback: Callable

    @property
    def tool_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.tool_desc,
                "parameters": (
                    self.tool_args.model_json_schema()
                    if is_pydantic_model(self.tool_args)
                    else self.tool_args
                ),
            },
        }


class ToolKit:

    def __init__(self, tools: List[ToolSpec]):
        self.tools = tools
        self.tool_names = [tool.tool_name for tool in tools]
        self.tool_schemas = [tool.tool_schema for tool in tools]
        self.tool_args = {tool.tool_name: tool.tool_args for tool in tools}
        self.tool_callbacks = {tool.tool_name: tool.tool_callback for tool in tools}

    def add_tool(self, tool: ToolSpec):
        self.tools.append(tool)
        self.tool_names.append(tool.tool_name)
        self.tool_schemas.append(tool.tool_schema)
        self.tool_args[tool.tool_name] = tool.tool_args
        self.tool_callbacks[tool.tool_name] = tool.tool_callback

    def get_tool_schemas(self):
        return self.tool_schemas

    def execute_tool(self, tool_call: ToolCall):
        if tool_call.tool_name not in self.tool_names:
            return f"The tool name {tool_call.tool_name} is unavailable. The available tools are: {self.tool_names}"

        try:
            args = self.tool_args[tool_call.tool_name]
            if is_pydantic_model(args):
                args = args.model_validate_json(tool_call.tool_args)
            else:
                args = json.loads(tool_call.tool_args)
        except Exception as e:
            return f"Validating the the tool `{tool_call.tool_name}` with args `{tool_call.tool_args}` failed: {str(e)}"

        try:
            return self.tool_callbacks[tool_call.tool_name](
                **args.model_dump() if isinstance(args, BaseModel) else args
            )
        except Exception as e:
            return f"Executing the tool `{tool_call.tool_name}` with args `{tool_call.tool_args}` failed: {str(e)}"


if __name__ == "__main__":

    class AskHumanHelp(BaseModel):
        question: str = Field(description="The question to ask human help")

    tool_spec = ToolSpec(
        tool_name="ask_human_help",
        tool_desc="Ask human help",
        tool_args=AskHumanHelp,
        tool_callback=lambda question: f"Human help: {question}",
    )
    schema = tool_spec.tool_schema
    print(schema)

    tool_kit = ToolKit([tool_spec])
    tool_call = ToolCall(tool_name="ask_human_help", tool_args='{"question": "你好"}')
    print(tool_kit.execute_tool(tool_call))

    # add a new tool
    class AddNumbers(BaseModel):
        a: int = Field(description="The first number")
        b: int = Field(description="The second number")

    tool_spec = ToolSpec(
        tool_name="add_numbers",
        tool_desc="Add two numbers",
        tool_args=AddNumbers,
        tool_callback=lambda a, b: f"The sum of {a} and {b} is {a + b}",
    )
    tool_kit.add_tool(tool_spec)
    tool_call = ToolCall(tool_name="add_numbers", tool_args='{"a": 1, "b": 2}')
    print(tool_kit.execute_tool(tool_call))

    # 添加一个tool_args为dict的tool
    tool_spec = ToolSpec(
        tool_name="echo",
        tool_desc="Echo the input",
        tool_args={"type": "object", "properties": {"input": {"type": "string"}}},
        tool_callback=lambda input: f"Echo: {input}",
    )
    tool_kit.add_tool(tool_spec)
    tool_call = ToolCall(tool_name="echo", tool_args='{"input": "hello"}')
    print(tool_kit.execute_tool(tool_call))
