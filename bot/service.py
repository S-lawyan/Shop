from bot.config import Settings
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from loguru import logger
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot.handlers import client, admin_panel


class BotService:
    def __init__(self, config: Settings):
        self.bot = Bot(token=config.bot.bot_token.get_secret_value(), parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

    async def start_bot(self) -> None:
        await self.dp.skip_updates()
        await self.set_default_settings_bot()
        client.register_handlers_client(self.dp)
        admin_panel.register_handlers_admin_panel(self.dp)
        logger.warning("The bot is running!")
        await self.dp.start_polling(self.bot)

    async def stop_bot(self) -> None:
        self.dp.stop_polling()

    async def set_default_settings_bot(self):
        await self.dp.bot.set_my_commands(
            [
                types.BotCommand("start", "Запустить бота"),
                types.BotCommand("menu", "Меню продавца"),
                types.BotCommand("list", "Список позиций"),
                types.BotCommand("file", "Загрузить файлом"),
                types.BotCommand("price", "Загрузить прайс-лист"),
                types.BotCommand("help", "Помощь"),
            ]
        )
