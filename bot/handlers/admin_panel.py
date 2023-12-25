import math

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.utils.models import Product
from bot.keyboards.client_kb import *
from database.mysqldb import db
from bot.utils import utilities as utl
from bot.utils.utilities import get_data
from loguru import logger
from aiogram.utils.exceptions import MessageNotModified
from aiogram import types
from bot.config import config
from aiogram.dispatcher.filters import Text


class TraderStates(StatesGroup):
    # manage products list
    get_product_name = State()
    get_price = State()
    get_quantity = State()
    delete_product = State()
    edit_product = State()


# ================= ПАНЕЛЬ АДМИНИСТРАТОРА ==============================

async def show_admin_panel_message(message: types.Message, state: FSMContext) -> None:
    await message.answer(text=glossary.get_phrase("trader_main_menu"), reply_markup=admin_panel_main)


# Adding the product
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(text=glossary.get_phrase("get_product_name"), reply_markup=kb_cancel)
    await TraderStates.get_product_name.set()


async def product_name_to_price(message: types.Message, state: FSMContext):
    product = Product()
    product.product_name = message.text
    await message.answer(text=glossary.get_phrase("get_price"), reply_markup=kb_cancel)
    await state.update_data(product=product)
    # await update_data(key="product", data=product, state=state)
    await TraderStates.get_price.set()


async def price_to_quantity(message: types.Message, state: FSMContext):
    product: Product = await get_data(key="product", state=state)
    # TODO Предобработка вводимой цены от строки до float
    try:
        product.price = await utl.is_valid_price(price=message.text)
        # await update_data(key="product", data=product, state=state)
        await state.update_data(product=product)
        await message.answer(text=glossary.get_phrase("get_quantity"))
        await TraderStates.get_quantity.set()
    except Exception as exc:
        logger.error(f"Ошибка при вводе цены товара : {exc}")
        await message.answer(text=glossary.get_phrase("uncorrected_enter"))


async def quantity_to_finish(message: types.Message, state: FSMContext):
    product: Product = await get_data(key="product", state=state)
    try:
        product.quantity = await utl.is_valid_quantity(quantity=message.text)
        article = await utl.generate_article()
        product.article = article
        product.trader_id = message.from_user.id
        await db.save_product(product=product)
        await state.finish()
        await message.answer(text=glossary.get_phrase("product_is_added"))
    except Exception as exc:
        logger.error(f"Ошибка при вводе количества товара : {exc}")
        await message.answer(text=glossary.get_phrase("uncorrected_enter"))


# Deleting the product
async def delete_product(message: types.Message):
    await message.answer(text=glossary.get_phrase("delete_product"), reply_markup=kb_cancel)
    await TraderStates.delete_product.set()


async def get_article_for_delete_product(message: types.Message, state: FSMContext):
    try:
        article = int(message.text)
        if not await db.check_unique_article(article=article):
            await message.answer(text=glossary.get_phrase("bad_article"), reply_markup=kb_cancel)
        else:
            await db.delete_product(product=int(article), trader_id=int(message.from_user.id))
            await message.answer(text=glossary.get_phrase("success_delete"))
    except:
        await message.answer(text=glossary.get_phrase("uncorrected_enter"), reply_markup=kb_cancel)


# Editing position
async def editing_product(message: types.Message, state: FSMContext):
    await message.answer(text=glossary.get_phrase("edit_product"), reply_markup=kb_cancel)
    await TraderStates.edit_product.set()


async def get_article_for_editing(message: types.Message, state: FSMContext):
    try:
        article = int(message.text)
        if not await db.check_unique_article(article=article):
            await message.answer(text=glossary.get_phrase("bad_article"), reply_markup=kb_cancel)
        else:
            # TODO делать запрос на изменение параметра позиции и запрос к БД на update
            # await db.delete_product(product=int(article), trader_id=int(message.from_user.id))
            # await message.answer(text=glossary.get_phrase("success_delete"))
    except:
        await message.answer(text=glossary.get_phrase("uncorrected_enter"), reply_markup=kb_cancel)


# Show the product list
async def show_products_list(message: types.Message, state: FSMContext):
    products_poll: list[Product] = await db.get_trader_products(trader_id=int(message.from_user.id))
    if len(products_poll) == 0:
        await message.answer(text=glossary.get_phrase("empty_product_list"))
    else:
        total_pages: int = math.ceil(len(products_poll) / config.bot.per_page)
        message_text = await send_products_list(products_list=products_poll)
        await message.answer(text=message_text, reply_markup=await pagination(total_pages=total_pages))


async def previous_page(call: types.CallbackQuery):
    products_poll: list[Product] = await db.get_trader_products(trader_id=int(call.from_user.id))
    total_pages: int = math.ceil(len(products_poll) / config.bot.per_page)
    page = int(call.data.split(":")[1]) - 1 if int(call.data.split(":")[1]) > 0 else 0
    message_text = await send_products_list(products_list=products_poll, page=page)
    try:
        await call.message.edit_text(text=message_text, reply_markup=await pagination(total_pages=total_pages, page=page))
    except (IndexError, KeyError):
        pass


async def next_page(call: types.CallbackQuery):
    products_poll: list[Product] = await db.get_trader_products(trader_id=call.from_user.id)
    total_pages: int = math.ceil(len(products_poll) / config.bot.per_page)
    page = int(call.data.split(":")[1]) + 1 if int(call.data.split(":")[1]) < (total_pages-1) else (total_pages-1)
    message_text = await send_products_list(products_list=products_poll, page=page)
    try:
        await call.message.edit_text(text=message_text, reply_markup=await pagination(total_pages=total_pages, page=page))
    except (IndexError, KeyError):
        pass


async def send_products_list(products_list: list[Product], page: int = 0) -> str:
    per_page = config.bot.per_page
    start_index: int = page * per_page
    end_index: int = start_index + per_page
    products_on_page: list[Product] = products_list[start_index:end_index]

    return await utl.generate_page_product(products=products_on_page)


# Intended errors handler
async def message_not_modified_handler(update: types.Update, error):
    await update.callback_query.answer()
    logger.error(error)
    return True


def register_handlers_admin_panel(dp: Dispatcher):
    # Vising admin panel
    dp.register_message_handler(show_admin_panel_message, commands=["menu"], state=None)
    dp.register_message_handler(show_admin_panel_message, Text(startswith='меню', ignore_case=True), state=None)
    # Adding product
    dp.register_message_handler(add_product, commands=["add"], state=None)
    dp.register_message_handler(add_product, Text(startswith='Добавить позицию'), state=None)
    dp.register_message_handler(product_name_to_price, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_product_name)
    dp.register_message_handler(price_to_quantity, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_price)
    dp.register_message_handler(quantity_to_finish, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_quantity)
    # Deleting product
    dp.register_message_handler(delete_product, commands=["dell"], state=None)
    dp.register_message_handler(delete_product, Text(startswith='Удалить позицию'), state=None)
    dp.register_message_handler(get_article_for_delete_product, content_types=types.ContentType.TEXT, state=TraderStates.delete_product)
    # Editing position

    # Vising product list
    dp.register_message_handler(show_products_list, commands=["list"], state=None)
    dp.register_message_handler(show_products_list, Text(startswith='Список позиций'), state=None)
    dp.register_callback_query_handler(previous_page, lambda query: query.data.startswith("previous:"),
                                       state=None)
    dp.register_callback_query_handler(next_page, lambda query: query.data.startswith("next:"), state=None)
    # Errors handlers
    dp.register_errors_handler(message_not_modified_handler, exception=MessageNotModified)
