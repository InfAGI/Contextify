"""
This module defines the data structures for managing Todo items within the planning tool.

Functionality:
    - Defines enumerations for Todo status and priority to ensure type safety and consistency.
    - Defines a `Todo` data model using Pydantic's `BaseModel` for robust data validation,
      serialization, and schema generation.

Implementation:
    - Uses Python's standard `enum` library for `TodoStatus` and `TodoPriority`.
    - Inherits from `pydantic.BaseModel` for the `Todo` class.
    - Fields are typed and include descriptions for better documentation and potential
      automated schema generation (e.g., for API endpoints or UI generation).

Usage:
    from src.tools.plan.todo import Todo, TodoStatus, TodoPriority

    # ID is automatically generated if not provided
    todo_item = Todo(
        context="Complete the documentation",
        priority=TodoPriority.HIGH
    )
    print(todo_item.json())

Dependencies:
    - pydantic: Required for `BaseModel` and `Field`.
    - enum: Required for creating enumeration classes.
    - uuid: Required for generating default unique identifiers.

Causal Constraints:
    - The `status` field must be one of the values defined in `TodoStatus`.
    - The `priority` field must be one of the values defined in `TodoPriority`.
    - `context` is a required field. `id` is auto-generated if missing.
"""

import uuid
from enum import Enum
from pydantic import BaseModel, Field


class TodoStatus(str, Enum):
    """
    Enum representing the lifecycle states of a Todo item.

    Values:
        - PENDING: The task has been created but not yet started.
        - IN_PROGRESS: The task is currently being worked on.
        - COMPLETED: The task has been finished successfully.
        - CANCELLED: The task has been abandoned or is no longer necessary.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TodoPriority(str, Enum):
    """
    Enum representing the urgency or importance of a Todo item.

    Values:
        - HIGH: Critical tasks that need immediate attention.
        - MEDIUM: Standard tasks with normal urgency.
        - LOW: Tasks that can be deferred or are of lower importance.
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Todo(BaseModel):
    """
    A Pydantic model representing a single unit of work (Todo item).

    This model enforces type checking and validation for todo attributes.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4().hex),
        description="The unique identifier for the todo item. Defaults to a UUID v4.",
    )

    status: TodoStatus = Field(
        default=TodoStatus.PENDING,
        description="The current lifecycle state of the todo item.",
    )

    context: str = Field(
        default="",
        description="The detailed description or context of the task to be performed.",
    )

    progress: str = Field(
        default="",
        description="A textual description of the current progress (e.g., '50%', 'Analysis done').",
    )

    priority: TodoPriority = Field(
        default=TodoPriority.MEDIUM,
        description="The priority level assigned to this task.",
    )

    class Config:
        """
        Pydantic model configuration.
        """

        # Allows populating the model with the value of the enum member rather than the member itself.
        use_enum_values = True
        # improved documentation for the schema
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "in_progress",
                "context": "Refactor the authentication middleware",
                "progress": "Identified key functions to change",
                "priority": "high",
            }
        }


if __name__ == "__main__":
    # 测试一下Todo模型
    todo_item = Todo(context="Complete the documentation", priority=TodoPriority.HIGH)
    print(todo_item.model_dump_json())
