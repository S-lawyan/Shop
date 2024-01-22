import asyncio

from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import config
from database.storage import DataBaseService
# from aiogram.contrib.fsm_storage.redis import RedisStorage2


es = DataBaseService(config)
bot = Bot(token=config.bot.bot_token.get_secret_value(), parse_mode=types.ParseMode.HTML)
loop = asyncio.get_event_loop()
# storage = RedisStorage2(host="localhost", port=6379, db=5, loop=loop)
dp = Dispatcher(bot, storage=MemoryStorage())
