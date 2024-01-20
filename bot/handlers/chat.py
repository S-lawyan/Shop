from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import User
from aiogram.utils.exceptions import MessageNotModified

from bot.utils.models import Product
from database.storage import es
from aiogram.dispatcher.filters import ChatTypeFilter
from bot.glossaries.glossary import glossary
from bot.utils import utilities as utl
# from bot.config import config
import math
from bot.keyboards.client_kb import *
from loguru import logger


async def query_messages(message: types.Message, state: FSMContext):
    request = str(message.text)
    products_poll: list[Product] = await es.execute_query(request=request)
    if len(products_poll) == 0:
        # await message.answer(text=glossary.get_phrase("no_data_on_request"))
        await bot.bot.send_message(
            chat_id=message.from_user.id,
            text=glossary.get_phrase("no_data_on_request"),
        )
    else:
        total_pages: int = math.ceil(len(products_poll) / int(config.bot.per_page))
        message_text = await send_products_list(products_list=products_poll)
        # await message.answer(text=message_text, reply_markup=await pagination(total_pages=total_pages))
        chat = Chat.get
        await bot.bot.send_message(
            chat_id=message.from_user.id,
            text=message_text,
            reply_markup=await pagination(total_pages=total_pages),
        )
        await state.update_data({f"{message.message_id}_products_poll": products_poll})
        # TODO Может быть сделать отдельно функцию, которая будет считать время жизни каждого такого сообщения
        #  и через время удалять его из state, чтобы не переполнять ОЗУ


async def send_products_list(products_list: list[Product], page: int = 0) -> str:
    per_page = int(config.bot.per_page)
    start_index: int = page * per_page
    end_index: int = start_index + per_page
    products_on_page: list[Product] = products_list[start_index:end_index]
    return await utl.generate_page_product(products=products_on_page)


async def previous_page(call: types.CallbackQuery, state: FSMContext):
    # products_poll: list[Product] = await es.get_trader_products(trader_id=int(call.from_user.id))
    products_poll: list[Product] = await utl.get_data(key=f"{call.message.message_id}_products_poll", state=state)
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


async def next_page(call: types.CallbackQuery, state: FSMContext):
    # products_poll: list[Product] = await es.get_trader_products(trader_id=call.from_user.id)
    products_poll: list[Product] = await utl.get_data(key=f"{call.message.message_id}_products_poll", state=state)
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


async def message_not_modified_handler(update: types.Update, error):
    await update.callback_query.answer()
    logger.error(error)
    return True


def register_handlers_chat(dp: Dispatcher):
    # start
    dp.register_message_handler(
        query_messages,
        ChatTypeFilter(types.ChatType.GROUP) | ChatTypeFilter(types.ChatType.SUPERGROUP),
        content_types=types.ContentType.TEXT,
        state='*'
    )
    dp.register_callback_query_handler(previous_page, lambda query: query.data.startswith("previous:"),
                                       state=None)
    dp.register_callback_query_handler(next_page, lambda query: query.data.startswith("next:"), state=None)
    dp.register_errors_handler(message_not_modified_handler, exception=MessageNotModified)


# TODO необходимо отправлять ответы в ЛС. Для этого нужен объект bot.
#  Разобраться со структурой проекта и том, как его правильно испортировать
