from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import config
from database.es_storage import DataBaseService
from database.redis_storage import RedisStorage

es = DataBaseService(config)
redis = RedisStorage(config)
bot = Bot(token=config.bot.bot_token.get_secret_value(), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
