from config import Settings
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from loguru import logger
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from heandlers import client, admin


class BotService:
    def __init__(self, config: Settings):
        self.bot = Bot(token=config.bot.bot_token.get_secret_value(), parse_mode=types.ParseMode.HTML)  # "html"
        # self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

    async def start_bot(self) -> None:
        executor.start_polling(
            self.dp, skip_updates=True, on_startup=self.on_startup, on_shutdown=self.on_shutdown)
        # await self.dp.start_polling(self.bot)

    async def on_startup(self,):
        client.register_handlers_client(self.dp)
        admin.register_handlers_admin(self.dp)
        print("Бот вышел в онлайн.")

    async def on_shutdown(self,):
        self.dp.stop_polling()
        print("Бот прекратил работу.")






