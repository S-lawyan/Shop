import re

from aiogram.dispatcher import FSMContext
from bot.utils.models import Product


async def is_valid_name(name: str):
    # Проверяем, что строка содержит только буквы, дефисы и пробелы
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\- ]+$', name):
        return False
    # Проверяем, что строка не содержит цифры
    if re.search(r'\d', name):
        return False
    # Проверяем, что каждое слово в строке состоит не менее чем из 2 букв
    words = name.split()
    for word in words:
        if len(word) < 2:
            return False
    return True


async def get_data(key: str, state: FSMContext):
    async with state.proxy() as storage:
        return storage[key]


async def generate_page_product(products: list[Product]) -> str:
    message: str = f"""<u>Результат запроса</u>:\n\n"""
    for product in products:
        # user = await bot.get_chat(telegram_id)
        # username = user.username
        line = f"""🔹<b>{product.product_name}</b>\nЦена: <b>{product.price} ₽</b>\nКоличество: <b>{product.quantity}</b>\nАртикул: <code>{product.article}</code>\n<a href="tg://user?id={product.trader_id}">Написать продавцу</a>\n\n"""
        message += line
    return message
