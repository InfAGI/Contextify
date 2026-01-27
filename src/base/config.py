import yaml
import os


class ConfigParser:

    def __init__(self, config_file: str):
        with open(config_file, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if value and key in value:
                value = value[key]
            else:
                return default
        return value


class Config:

    def __init__(
        self,
        config_file: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../default.yaml")
        ),
    ):
        self.config = ConfigParser(config_file)
        self.deepseek_api_base = self.config.get("DEEPSEEK_API_BASE")
        self.deepseek_api_key = self.config.get("DEEPSEEK_API_KEY")
        self.deepseek_reasoning_model = self.config.get("DEEPSEEK_REASONING_MODEL")
        self.deepseek_chat_model = self.config.get("DEEPSEEK_CHAT_MODEL")
        self.embedding_api_base = self.config.get("EMBEDDING_API_BASE")
        self.embedding_api_key = self.config.get("EMBEDDING_API_KEY")
        self.embedding_model = self.config.get("EMBEDDING_MODEL")


DefaultConfig = Config()
