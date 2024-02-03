from bot.service import dp
from loguru import logger
from bot.service import es
from bot.service import redis
from aiogram import executor
from bot import filters
import bot.handlers
from aiogram import types


async def set_default_settings_bot(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("chat", "Ссылка на чат"),
            types.BotCommand("help", "Помощь"),
        ]
    )


async def on_startup(dp):
    logger.warning("Starting bot...")
    logger.add(
        "bot/logs/avia_bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="DEBUG",
    )
    await set_default_settings_bot(dp=dp)
    await redis.create()
    await es.es_healthcheck()
    logger.warning("The bot is started!")


async def on_shutdown(dp):
    await dp.storage.close()
    await redis.close()
    logger.warning("The bot is stop!")


def main():
    filters.setup(dp=dp)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)


if __name__ == "__main__":
    main()
