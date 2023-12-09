import asyncio

from loguru import logger
from service import BotService
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
        bot = BotService(config)
        # await database.create_pool()
        # asyncio.create_task(bot.start_bot())
        await bot.start_bot()
        await database.create_pool()
    finally:
        await bot.stop_bot()
        await database.close()



if __name__ == "__main__":
    asyncio.run(main())



