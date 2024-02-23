from aiogram import types
from aiogram.utils.exceptions import MessageNotModified

from bot.utils.models import Product
from bot.glossaries.glossary import glossary
from bot.utils import utilities as utl
from bot.config import config
import math
from bot.keyboards.client_kb import pagination
from loguru import logger
from bot.filters import IsGroup, IsDirect
from bot.service import dp, bot, es, redis


@dp.message_handler(IsGroup(), content_types=types.ContentType.TEXT, state='*')
async def query_messages(message: types.Message):
    message_text: str = str(message.text)
    requests: list = message_text.split("\n")
    for request in requests:
        # products_poll: list[Product] = await get_products_poll_from_storage(request=request)
        products_poll: list[Product] = await es.search_products_poll(request=request)
        if len(products_poll) == 0:
            await bot.send_message(
                chat_id=message.from_user.id,
                text=glossary.get_phrase("no_data_on_request"),
            )
        else:
            total_pages: int = math.ceil(len(products_poll) / int(config.bot.per_page))
            message_text = await send_products_list(products_list=products_poll)
            personal_message = await bot.send_message(
                chat_id=message.from_user.id,
                text=message_text,
                reply_markup=await pagination(total_pages=total_pages),
            )
            # Сохраняется конкретный pool для конкретного сообщения
            await redis.set_data(key=f"{message.from_user.id}:{personal_message.message_id}", value=request, ttl=5)  # 720


@dp.callback_query_handler(IsDirect(), lambda query: query.data.startswith("previous:"), state=None)
async def previous_page(call: types.CallbackQuery):
    # Redis
    # products_poll: list[Product] = await get_products_poll_from_cash(key=f"{call.message.chat.id}:{call.message.message_id}")
    request: str = await redis.get_data(key=f"{call.message.chat.id}:{call.message.message_id}")
    if request:
        products_poll: list[Product] = await es.search_products_poll(request=request)
        total_pages: int = math.ceil(len(products_poll) / int(config.bot.per_page))
        page = int(call.data.split(":")[1]) - 1 if int(call.data.split(":")[1]) > 0 else 0
        message_text = await send_products_list(products_list=products_poll, page=page)
        try:
            await call.message.edit_text(
                text=message_text,
                reply_markup=await pagination(
                    total_pages=total_pages,
                    page=page
                )
            )
        except (IndexError, KeyError):
            pass
    else:
        await call.message.edit_text(text=glossary.get_phrase("ttl_is_over"), reply_markup=None)


@dp.callback_query_handler(IsDirect(), lambda query: query.data.startswith("next:"), state=None)
async def next_page(call: types.CallbackQuery):
    # Redis
    # products_poll: list[Product] = await get_products_poll_from_cash(key=f"{call.message.chat.id}:{call.message.message_id}")
    request: str = await redis.get_data(key=f"{call.message.chat.id}:{call.message.message_id}")
    if request:
        products_poll: list[Product] = await es.search_products_poll(request=request)
        total_pages: int = math.ceil(len(products_poll) / int(config.bot.per_page))
        page = int(call.data.split(":")[1]) + 1 if int(call.data.split(":")[1]) < (total_pages-1) else (total_pages-1)
        message_text = await send_products_list(products_list=products_poll, page=page)
        try:
            await call.message.edit_text(
                text=message_text,
                reply_markup=await pagination(
                    total_pages=total_pages,
                    page=page
                )
            )
        except (IndexError, KeyError):
            pass
    else:
        await call.message.edit_text(text=glossary.get_phrase("ttl_is_over"), reply_markup=None)


@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update: types.Update, error):
    await update.callback_query.answer()
    logger.error(error)
    return True


async def send_products_list(products_list: list[Product], page: int = 0) -> str:
    per_page = int(config.bot.per_page)
    start_index: int = page * per_page
    end_index: int = start_index + per_page
    products_on_page: list[Product] = products_list[start_index:end_index]
    return await utl.generate_page_product(products=products_on_page)
