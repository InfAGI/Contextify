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


DefaultConfig = Config()

if __name__ == "__main__":
    print(DefaultConfig.get("providers", "deepseek", "base_url"))
    print(DefaultConfig.get("providers", "deepseek", "api_key"))
