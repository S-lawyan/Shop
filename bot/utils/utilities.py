import re
import random

from aiogram.dispatcher import FSMContext
from bot.service import es
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
        if await es.check_in_products_index(field="article", value=article):
            continue
        else:
            return article


async def generate_page_product(products: list[Product]) -> str:
    message: str = "<u>📋 Результат выполнения запроса</u>:\n\n"
    for product in products:
        line = f"""🔹<b>{product.product_name}</b>\nЦена: <b>{product.price} ₽</b>\nКоличество: <b>{product.quantity}</b>\nАртикул: <code>{product.article}</code>\n\n"""
        message += line
    return message

# Для RedisStorage
# import time
# from bot.service import storage
# Задаем время жизни состояния
# state_ttl = 3600


# async def set_state(user_id, chat_id, value):
#     # Сохраняем состояние и текущее время
#     await storage.set_data(chat=chat_id, user=user_id, data={'state': value, 'timestamp': time.time()})
#
#
# async def get_state(user_id, chat_id):
#     data = await storage.get_data(user=user_id, chat=chat_id)
#     if data:
#         # Проверяем, не истекло ли время жизни состояния
#         if time.time() - data['timestamp'] > state_ttl:
#             # Если истекло - сбрасываем состояние
#             await storage.reset_data(user_id)
#             return None
#         else:
#             return data['state']
#     else:
#         return None
