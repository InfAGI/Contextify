import json
from typing import Type, Dict, Callable
from pydantic import BaseModel, Field
from abc import ABC
import asyncio


def is_pydantic_model(obj):
    """
    Check if an object is a Pydantic model class.

    Args:
        obj: The object to check.

    Returns:
        bool: True if it is a Pydantic model class, False otherwise.
    """
    return isinstance(obj, type) and issubclass(obj, BaseModel)


class ToolCall(BaseModel):
    """
    Represents a request to call a tool.

    Attributes:
        id (str): Unique identifier for the tool call.
        tool_name (str): The name of the tool to be called.
        tool_args (str): The arguments for the tool call as a JSON string.
    """

    id: str = ""
    tool_name: str = ""
    tool_args: str = ""


class ToolResult(BaseModel):
    """
    Represents the result of a tool execution.

    Attributes:
        id (str): The identifier of the tool call this result corresponds to.
        output (str): The output of the tool execution if successful.
        error (str): The error message if the tool execution failed.
        success (bool): True if the execution was successful, False otherwise.
    """

    id: str = ""
    output: str = ""
    error: str = ""
    success: bool = False


class Tool(ABC):
    """
    Abstract base class for all tools.

    This class defines the interface that all tools must implement.
    It provides methods to get tool metadata (name, description, parameters)
    and a method to execute the tool.
    """

    def __init__(
        self,
        name: str = None,
        description: str = None,
        parameters: Type[BaseModel] | Dict = None,
        callback: Callable[[Dict], ToolResult] = None,
    ):
        """
        Initialize the tool.

        Args:
            name (str, optional): The name of the tool.
            description (str, optional): A brief description of what the tool does.
            parameters (Type[BaseModel] | Dict, optional): The parameters schema for the tool, either as a Pydantic model or a dictionary.
            callback (Callable[[Dict], ToolResult], optional): The callback function to execute the tool.
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.callback = callback

    def get_name(self) -> str:
        """
        Get the name of the tool.

        Returns:
            str: The tool name.
        """
        return self.name

    def get_description(self) -> str:
        """
        Get the description of the tool.

        Returns:
            str: The tool description.
        """
        return self.description

    def get_parameters(self) -> Type[BaseModel] | Dict:
        """
        Get the parameters schema of the tool.

        Returns:
            Type[BaseModel] | Dict: The parameters schema.
        """
        return self.parameters

    def json_definition(self) -> Dict:
        """
        Generate the JSON definition of the tool for LLM consumption.

        Returns:
            Dict: The JSON definition including type, name, description, and parameters.
        """
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": (
                    self.get_parameters().model_json_schema()
                    if is_pydantic_model(self.get_parameters())
                    else self.get_parameters()
                ),
            },
        }

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute the tool with the given arguments.

        Args:
            tool_call (ToolCall): The tool call request.

        Returns:
            ToolResult: The result of the tool execution.
        """
        result = ToolResult(id=tool_call.id, success=False)

        try:
            if is_pydantic_model(self.get_parameters()):
                args = (
                    self.get_parameters()
                    .model_validate_json(tool_call.tool_args)
                    .model_dump()
                )
            else:
                args = json.loads(tool_call.tool_args)
        except Exception as e:
            result.error = f"Validating the tool `{tool_call.tool_name}` with args `{tool_call.tool_args}` failed: {str(e)}"
            return result

        try:
            res = await self._execute(**args)
            result.output = res.output
            result.error = res.error
            result.success = res.success
            return result
        except Exception as e:
            result.error = f"Executing the tool `{tool_call.tool_name}` with args `{tool_call.tool_args}` failed: {str(e)}"
            return result

    async def _execute(self, args: Dict) -> ToolResult:
        """
        Execute the tool with the given arguments.

        Args:
            args (Dict): The arguments for the tool execution.

        Returns:
            ToolResult: The result of the tool execution.
        """
        if self.callback:
            return self.callback(args)
        raise NotImplementedError("Must implement _execute method")

    async def close(self):
        """
        Close any resources used by the tool.
        """
        return None


if __name__ == "__main__":
    # Test example
    print("Running Tool tests...")

    # Define parameters for a simple calculator tool
    class AddParameters(BaseModel):
        a: int = Field(..., description="The first number")
        b: int = Field(..., description="The second number")

    # Implement a concrete tool
    class AddTool(Tool):
        def __init__(self):
            super().__init__(
                name="add_numbers",
                description="Adds two numbers together",
                parameters=AddParameters,
            )

        async def _execute(self, a: int, b: int) -> ToolResult:
            try:
                result = a + b
                return ToolResult(output=str(result), success=True)
            except Exception as e:
                return ToolResult(error=str(e), success=False)

    async def main():
        # Instantiate the tool
        tool = AddTool()

        # Check definition
        print("\nTool Definition:")
        print(json.dumps(tool.json_definition(), indent=4))

        # 1. Test Successful Execution
        print("\n1. Testing Successful Execution (2 + 3):")
        tool_call_success = ToolCall(
            id="call_1", tool_name="add_numbers", tool_args=json.dumps({"a": 2, "b": 3})
        )
        result = await tool.execute(tool_call_success)
        print(result)
        assert result.success is True
        assert result.output == "5"
        assert result.id == "call_1"
        print("Passed!")

        # 2. Test Validation Error (Missing argument)
        print("\n2. Testing Validation Error (Missing 'b'):")
        tool_call_validation_error = ToolCall(
            id="call_2", tool_name="add_numbers", tool_args=json.dumps({"a": 2})
        )
        result = await tool.execute(tool_call_validation_error)
        print(result)
        assert result.success is False
        assert "validating" in result.error.lower()
        print("Passed!")

        # 3. Test Invalid JSON
        print("\n3. Testing Invalid JSON:")
        tool_call_json_error = ToolCall(
            id="call_3", tool_name="add_numbers", tool_args="{invalid_json}"
        )
        result = await tool.execute(tool_call_json_error)
        print(result)
        assert result.success is False
        assert "validating" in result.error.lower()
        print("Passed!")

    # Run the async main function
    asyncio.run(main())
