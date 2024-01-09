import re
import random
from typing import Any

from aiogram.dispatcher import FSMContext
from database.storage import es
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


async def is_valid_price(price: str):
    # symbols_list = [char for char in price if char.isnumeric()]
    # _clear_price = ''.join(symbols_list)
    _clear_price = float(price)
    return _clear_price


async def is_valid_quantity(quantity: str):
    if quantity.lower() == "нет":
        return None
    else:
        return int(quantity)


async def get_data(key: str, state: FSMContext):
    async with state.proxy() as storage:
        return storage[key]


async def generate_article() -> int:
    while True:
        article = int(random.randint(100000, 999999))
        if await es.check_unique_article(article=article):
            continue
        else:
            return article


async def generate_page_product(products: list[Product]) -> str:
    message: str = "<u>📋 Список товаров</u>:\n\n"
    for product in products:
        line = f"""🔹<b>{product.product_name}</b>\nЦена: <b>{product.price} ₽</b>\nКоличество: <b>{product.quantity}</b>\nАртикул: <code>{product.article}</code>\n\n"""
        message += line
    return message
