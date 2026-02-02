from src.agents.react import ReAct
from src.llms.agent import Agent
from src.tools.registry import ToolRegistry
from src.utils.tracer import Tracer
from src.agents.reflect import meta_learn

if __name__ == "__main__":
    import time
    import asyncio
    from src.tools.base import ToolCall

    from src.tools.bash.bash_tool import BashTool
    from src.tools.text.view_tool import ViewTool
    from src.tools.text.edit_tool import CreateFileTool, InsertFileTool, ReplaceFileTool
    from src.tools.help.ask_human import AskHumanForHelpTool

    from src.llms.anthropic import (
        get_anthropic_client,
        get_anthropic_response_with_cache,
    )
    from src.llms.deepseek import (
        get_deepseek_client,
        get_deepseek_response_with_cache,
    )

    proj_path = [
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\open-webui",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\MoneyPrinterTurbo",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\banana-slides",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\NarratoAI",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\DeepTutor",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\BiliNote",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\AionUi",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\AI-Media2Doc",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\huobao-drama",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\Pixelle-Video",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\ChatLab",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\skid-homework",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\Risuai",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\BuildingAI",
        "C:\\Users\\hylnb\\Workspace\\deploy_benchmark\\valuecell",
    ]

    async def main():
        for proj in proj_path:
            print(f"Project: {proj}")
            while True:
                trace_path = f"C://Users//hylnb//Workspace//Contextify//.cache//trace//tracer_{int(time.time())}.txt"
                skill_file = "C:\\Users\\hylnb\\Workspace\\Contextify\\.contextify\\skills\\generating-docker-compose-files\\SKILL.md"

                # 读取skill_file内容
                with open(skill_file, "r") as f:
                    skill_content = f.read()

                tool_registry = ToolRegistry(
                    [
                        # BashTool(cwd="C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"),
                        BashTool(cwd=proj),
                        ViewTool(),
                        CreateFileTool(),
                        InsertFileTool(),
                        ReplaceFileTool(),
                        AskHumanForHelpTool(),
                    ],
                    include_mcp_tools=False,
                )
                res = await tool_registry.execute_tool_call(
                    ToolCall(tool_name="bash", tool_args='{"command": "git clean -fd"}')
                )
                print(f"git clean -fd result: {res}")
                res = await tool_registry.execute_tool_call(
                    ToolCall(
                        tool_name="bash", tool_args='{"command": "git reset --hard"}'
                    )
                )
                print(f"git reset --hard result: {res}")

                # $containers = docker ps -aq
                # if ($containers) {
                #     Write-Host "Stopping containers..."
                #     docker stop $containers
                #     Write-Host "Removing containers..."
                #     docker rm $containers
                # } else {
                #     Write-Host "No containers found."
                # }
                res = await tool_registry.execute_tool_call(
                    ToolCall(
                        tool_name="bash",
                        tool_args="""{"command": "$ids = docker ps -aq; if ($ids) { docker stop $ids; docker rm -f $ids }"}""",
                    )
                )
                print(f"remove docker containers result: {res}")
                # $images = docker images -q
                # if ($images) {
                #     Write-Host "Removing images..."
                #     docker rmi -f $images
                # } else {
                #     Write-Host "No images found."
                # }
                res = await tool_registry.execute_tool_call(
                    ToolCall(
                        tool_name="bash",
                        tool_args="""{"command": "$ids = docker images -q; if ($ids) { docker rmi -f $ids }"}""",
                    )
                )
                print(f"remove docker images result: {res}")

                # input("Press Enter to continue...")

                agent = Agent(
                    tools=tool_registry,
                    client=get_anthropic_client(),
                    invoke=get_anthropic_response_with_cache,
                    # client=get_deepseek_client(),
                    # invoke=get_deepseek_response_with_cache,
                    tracer=Tracer(trace_path),
                )
                agent.append_user_message(
                    f"""<SKILL>{skill_content}</SKILL>为该仓库生成compose.yaml文件并用docker部署. {proj}"""
                )
                # agent.append_user_message(
                #     """找到代码仓库的运行入口. C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"""
                # )
                # agent.append_user_message(
                #     """深度调研一下这个代码仓库. C:\\Users\\hylnb\\Workspace\\deploy\\valuecell"""
                # )
                react = ReAct(agent=agent)
                try:
                    res = await react.solve(
                        debug=False, feedback=True, max_input_tokens=1024 * 64
                    )
                    print(f"run result: {res}")
                finally:
                    await tool_registry.close_tools()

                await meta_learn(trace_path, skill_file)

                input("Press Enter to continue...")

    asyncio.run(main())
