import os

import yaml
from pydantic import BaseModel, SecretStr
from loguru import logger


class BotConfig(BaseModel):
    bot_token: SecretStr
    channel_id: int
    channel_url: str
    per_page: int


class ESConfig(BaseModel):
    es_host: str
    es_port: int
    es_user: str
    es_pass: SecretStr
    es_connections_limit: int
    connection_attempt: int
    products: str
    consumers: str
    traders: str

    def get_mysql_uri(self) -> str:
        uri_template = "mysql+asyncmy://{user}:{password}@{host}:{port}/{db_name}"
        return uri_template.format(
            user=self.db_user,
            password=self.db_pass.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            db_name=self.db_name,
        )


class RedisConfig(BaseModel):
    redis_host: str
    redis_port: int
    redis_user: str
    redis_pass: SecretStr
    connections_limit: int
    #ttl: int

    def get_redis_url(self) -> str:
        redis_url: str = "redis://{user}:{password}@{host}:{port}/0"
        # "redis://[[user]:[password]]@host:port/1"
        # f"redis://{self.config.redis.redis_user}:{self.config.redis.redis_pass.get_secret_value()}@{self.config.redis.redis_host}:{self.config.redis.redis_port}/0",
        return redis_url.format(
            user=self.redis_user,
            password=self.redis_pass.get_secret_value(),
            host=self.redis_host,
            port=self.redis_port
        )


class Settings(BaseModel):
    es: ESConfig
    redis: RedisConfig
    bot: BotConfig


def load_config(config_path: str) -> Settings:
    try:
        with open(config_path, "r") as file:
            dictionary: dict = yaml.load(stream=file, Loader=yaml.FullLoader)
            _config: Settings = Settings.model_validate(dictionary)
        return _config

    except FileNotFoundError:
        logger.error(f"Конфигурационный файл отсутствует по пути: {config_path}")

    except yaml.YAMLError as exception:
        logger.error(f"Ошибка при загрузке YAML: {exception}")

    except Exception as e:
        logger.error(f"Ошибка при загрузке конфигурационного файла: {e}")


# Получаю директорию бота
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Получаю директорию проекта
PROJECT_DIR = os.path.dirname(BOT_DIR)
# Подгружаю конфиги и запускаю бота
config: Settings = load_config(config_path=os.path.join(PROJECT_DIR, "config.yaml"))

__all__ = ["config", "Settings"]
