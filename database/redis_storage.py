from bot.config import Settings
import aioredis
import json
from loguru import logger

from bot.utils.models import Product


class RedisStorage:
    def __init__(self, config: Settings):
        self.redis = None
        self.config = config

    async def create(self):
        try:
            self.redis = await aioredis.from_url(
                url=self.config.redis.get_redis_url(),
                max_connections=self.config.redis.connections_limit
            )
            result = await self.redis.ping()
            logger.warning(f"Connected to Redis. Server responded with: {result}")
            logger.warning("Redis connect was created successfully!")
        except (Exception,) as e:
            logger.error(f"Ошибка при подключении к Redis: {e}")

    async def close(self):
        await self.redis.close()
        logger.warning("Redis connect was closed!")

    async def get_data(self, key: str):
        try:
            _response = await self.redis.get(key)
            _response = _response.decode('utf-8')
            return _response
        except (Exception,) as e:
            logger.error(f"Ошибка получения данных {key} из Redis: {e}")

    async def set_data(self, key: str, value: list, ttl: int):
        try:
            # serialized_values = [value.__dict__ for value in value]
            # reformed_value = json.dumps(serialized_values)
            await self.redis.set(name=key, value=value, ex=60 * int(ttl))  # json.dumps(value)
            logger.info(f"Успешное добавление данных в Redis:\nkey: {key}\nvalue: {value}")
        except (Exception,) as e:
            logger.error(f"Ошибка сохранения данных в Redis: {e}\nkey: {key}\nvalue: {str(json.dumps(value))}")


async def _pars_json_products(response: list) -> list[Product]:
    return [_pars_json_product(product) for product in response]


def _pars_json_product(product: dict) -> Product:
    _product = Product()
    _product.product_name = str(product["product_name"])
    _product.price = float(product["price"])
    _product.article = int(product["article"])
    _product.trader_id = int(product["trader_id"])
    return _product
