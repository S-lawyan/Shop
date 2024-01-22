from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from bot.utils.models import Product
from bot.glossaries.glossary import glossary
from bot.utils import utilities as utl
# from bot.config import config
import math
from bot.keyboards.client_kb import *
from loguru import logger
from bot.filters import IsGroup, IsDirect
from bot.service import dp, bot, es


@dp.message_handler(IsGroup(), content_types=types.ContentType.TEXT, state='*')
async def query_messages(message: types.Message, state: FSMContext):
    request = str(message.text)
    products_poll: list[Product] = await es.execute_query(request=request)
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
        # TODO Может быть сделать отдельно функцию, которая будет считать время жизни каждого такого сообщения
        #  и через время удалять его из state, чтобы не переполнять ОЗУ


async def send_products_list(products_list: list[Product], page: int = 0) -> str:
    per_page = int(config.bot.per_page)
    start_index: int = page * per_page
    end_index: int = start_index + per_page
    products_on_page: list[Product] = products_list[start_index:end_index]
    return await utl.generate_page_product(products=products_on_page)


@dp.callback_query_handler(IsDirect(), lambda query: query.data.startswith("previous:"), state=None)
async def previous_page(call: types.CallbackQuery, state: FSMContext):
    products_poll: list[Product] = await es.execute_query(trader_id=int(call.from_user.id))
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


@dp.callback_query_handler(IsDirect(), lambda query: query.data.startswith("next:"), state=None)
async def next_page(call: types.CallbackQuery, state: FSMContext):
    products_poll: list[Product] = await es.execute_query(trader_id=call.from_user.id)
    data = await state.get_data()
    products_poll: list[Product] = data.get(f"{call.message.message_id}_{call.message.chat.id}")
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


@dp.errors_handler(IsDirect(), exception=MessageNotModified)
async def message_not_modified_handler(update: types.Update, error):
    await update.callback_query.answer()
    logger.error(error)
    return True

# TODO на месте флажков нужно сделать получение пулла продуктов из БД sqlite3, думаю.
#  Либо Redis, который нужно отдельно изучать. Скорее первое.
#  Далее сделать механизм удаления старых сообщений из личного чата по истечении времени, чтобы "от дурака".
