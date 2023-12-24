import re
import random
from typing import Any

from aiogram.dispatcher import FSMContext
from database.mysqldb import db


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
    if quantity.lower() == "не ограничено":
        return None
    else:
        return int(quantity)


async def update_data(key: str, data: Any, state: FSMContext):
    async with state.proxy() as storage:
        storage[key] = data


async def get_data(key: str, state: FSMContext):
    async with state.proxy() as storage:
        return storage[key]


async def generate_article() -> int:
    while True:
        article = int(random.randint(100000, 999999))
        if await db.check_unique_article(article=article):
            continue
        else:
            return article


async def generate_page_product(products) -> str:
    message: str = "Список товаров:\n\n"
    for product in products:
        if product.quantity is not None:
            quantity = product.quantity
        else:
            quantity = ""
        line = f"""⚪ <b>{product.product_name}</b> - {product.price} {quantity} ({product.article})"""
        message += product + "\n"
    return message
