import os
from loguru import logger
from string import Template
import yaml


class Glossary:
    def __init__(
            self,
            # language: str,
            glossaries_path: str,
    ):
        # self.language = language
        self.data: dict = {}
        files = [os.path.join(glossaries_path, f) for f in os.listdir(glossaries_path) if f.endswith(".yaml")]
        for file in files:
            with open(file, "r", encoding="utf8") as fgl:
                self.data: dict = yaml.load(stream=fgl, Loader=yaml.FullLoader)

    def get_phrase(self, key, **kwargs):
        if key not in self.data:
            logger.error(f"В словаре нет фразы {key}")
            return key
        else:
            text = self.data.get(key)
            if isinstance(text, str):
                return Template(text).safe_substitute(**kwargs)
            else:
                return text


glossary = Glossary(
    glossaries_path=os.path.dirname(__file__),
    # language=config.bot.language
)

__all__ = ["glossary"]
