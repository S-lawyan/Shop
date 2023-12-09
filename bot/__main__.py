import asyncio

from loguru import logger
from bot.service import BotService
from config import config
from database.mysqldb import database


async def main():
    logger.add(
        "logs/avia_bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
    )
    try:
        await database.create_pool()
        bot = BotService(config)
        await bot.start_bot()
    finally:
        await bot.stop_bot()
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())