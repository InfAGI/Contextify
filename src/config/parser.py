import json


class ConfigParser:

    def __init__(self, config_file: str):
        with open(config_file, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def get(self, *keys, default=None):
        value = self.config
        for key in keys:
            if value and key in value:
                value = value[key]
            else:
                return default
        return value
