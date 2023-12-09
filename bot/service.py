from bot.config import Settings
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from loguru import logger
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.heandlers import client, admin


class BotService:
    def __init__(self, config: Settings):
        self.bot = Bot(token=config.bot.bot_token.get_secret_value(), parse_mode=types.ParseMode.HTML)  # MARKDOWN_V2
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

    async def start_bot(self) -> None:
        await self.dp.skip_updates()
        # admin.register_handlers_admin(self.dp)
        client.register_handlers_client(self.dp)
        logger.info("The bot is running!")
        await self.dp.start_polling(self.bot)

    async def stop_bot(self) -> None:
        self.dp.stop_polling()
