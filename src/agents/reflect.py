import asyncio
from src.agents.react import ReAct
from src.llms.agent import Agent
from src.tools.registry import ToolRegistry
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

prompt = (
    """<SKILL>
---
name: meta-learning
description: Meta-learning extracts reusable knowledge from experience. Apply after completing any task to build and refine skills over time.
---

# Meta-Learning

1. Reflection

Based on execution progress, answer the following questions:

- What went right? Why did it work?
- What went wrong? Why did it fail?
- If you could redo the task, how would you improve?

2. Documentation

Distill improved step-by-step SOP into the SKILL.md file (create or update). Note that the SOP should be general methodology that can be applied to other similar tasks rather than specific to the current task.</SKILL>"""
    + "The experience file is {experience_file}. The skill file is {skill_file}."
)


async def meta_learn(experience_file: str, skill_file: str):
    tool_registry = ToolRegistry(
        [
            ViewTool(),
            CreateFileTool(),
            InsertFileTool(),
            ReplaceFileTool(),
        ],
        include_mcp_tools=False,
    )
    agent = Agent(
        tools=tool_registry,
        client=get_anthropic_client(),
        invoke=get_anthropic_response_with_cache,
        # client=get_deepseek_client(),
        # invoke=get_deepseek_response_with_cache,
    )
    agent.append_user_message(
        prompt.format(experience_file=experience_file, skill_file=skill_file)
    )
    react = ReAct(agent=agent)
    try:
        await react.solve(debug=False, feedback=False, max_input_tokens=1024 * 64)
    finally:
        await tool_registry.close_tools()


if __name__ == "__main__":
    experience_file = (
        "C:\\Users\\hylnb\\Workspace\\Contextify\\.cache\\trace\\tracer_1769948958.txt"
    )
    skill_file = "C:\\Users\\hylnb\\Workspace\\Contextify\\.contextify\\skills\\generating-docker-compose-files\\SKILL.md"

    async def main():
        await meta_learn(experience_file, skill_file)

    asyncio.run(main())
