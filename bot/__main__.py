import asyncio

from loguru import logger
from bot.service import BotService
from config import config
from database.storage import es


async def main():
    logger.add(
        "bot/logs/avia_bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
    )
    try:
        await es.es_healthcheck()
        bot = BotService(config)
        await bot.start_bot()
    finally:
        await bot.stop_bot()


if __name__ == "__main__":
    # TODO попробовать сделать без асинхра и понять в чем разница
    asyncio.run(main())