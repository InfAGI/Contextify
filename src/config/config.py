import os
from src.config.parser import ConfigParser


class Config(ConfigParser):

    def __init__(
        self,
        config_file: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../.contextify/config.json")
        ),
    ):
        super().__init__(config_file)
        self.deepseek_base_url = self.get("providers", "deepseek", "base_url")
        self.deepseek_api_key = self.get("providers", "deepseek", "api_key")
        self.deepseek_reasoning_model = self.get(
            "providers", "deepseek", "reasoning_model"
        )
        self.mcp_servers = self.get("mcpServers")


DefaultConfig = Config()

if __name__ == "__main__":
    print(DefaultConfig.get("providers", "deepseek", "base_url"))
    print(DefaultConfig.get("providers", "deepseek", "api_key"))
    print(DefaultConfig.deepseek_base_url)
    print(DefaultConfig.deepseek_api_key)
    print(DefaultConfig.deepseek_reasoning_model)
    print(DefaultConfig.mcp_servers)
