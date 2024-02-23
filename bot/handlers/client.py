import io

import openpyxl
from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.client_kb import *
from database.storage import es
from bot.utils import utilities as utl
from aiogram.dispatcher.filters import Text
from bot.utils.models import Product


class TraderStates(StatesGroup):
    get_shop_name = State()
    get_fio = State()
    get_file = State()
    get_insert_variants = State()
    get_price_list = State()
    get_insert_object = State()


# ================= БЛОК ОСНОВНЫХ КОМАНД БОТА ==============================
async def command_start(message: types.Message) -> None:
    if await es.check_in_traders_index(field="tg_id", value=int(message.from_user.id)):
        await message.answer(text=glossary.get_phrase("trader_main_menu"), reply_markup=admin_panel_main)
    else:
        await message.answer(
            text=glossary.get_phrase(
                "start_greeting",
                username=message.from_user.first_name
            ),
            reply_markup=kb_registration,
        )


async def command_help_message(message: types.Message) -> None:
    await message.answer(text=glossary.get_phrase("help"))


async def command_cancel_message(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.answer(text=glossary.get_phrase("cancelled"), reply_markup=admin_panel_main)


# ================= БЛОК РЕГИСТРАЦИИ НОВОГО ТРЕЙДЕРА ==============================
async def start_registration(call: types.CallbackQuery) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=glossary.get_phrase("get_shop_name"))
    await TraderStates.get_shop_name.set()


async def get_shop_name_to_fio(message: types.Message, state: FSMContext) -> None:
    shop_name = message.text
    async with state.proxy() as storage:
        storage["shop_name"] = shop_name
    if await es.check_in_traders_index(field="name", value=shop_name):
        await message.answer(text=glossary.get_phrase("reply_shop_name"))
    else:
        await message.answer(text=glossary.get_phrase("get_fio"))
        await TraderStates.get_fio.set()


async def get_fio_to_tg_id(message: types.Message, state: FSMContext) -> None:
    fio = message.text
    # if await utl.is_valid_name(name=fio):
    async with state.proxy() as storage:
        shop_name = storage["shop_name"]
    tg_id = message.from_user.id
    await es.save_trader(tg_id=tg_id, trader_name=shop_name, fio=fio)
    await message.answer(text=glossary.get_phrase("reg_finish", fio=fio), reply_markup=admin_panel_main)
    await state.finish()


async def process_file(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as storage:
        delete_flag = storage["delete_old_price"]
    products = []
    field_rows = []
    file_content = io.BytesIO()
    await message.document.download(destination_file=file_content)
    wb = openpyxl.load_workbook(file_content)
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        try:
            product = Product()
            product.product_name = row[0]
            product.price = float(row[1])
            product.trader_id = int(message.from_user.id)
            product.article = await utl.generate_article()
            products.append(product)
        except (Exception,) as exc:
            field_rows.append(row)
            continue
    await es.save_bulk_products(products=products, delete_flag=delete_flag)
    await message.answer(glossary.get_phrase("success_insert_price", correct_rows=len(products)))
    if len(field_rows) != 0:
        msg = await utl.generate_message_with_uncorrected_rows(rows=field_rows)
        await message.answer(text=msg)
    await state.finish()


async def process_price(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as storage:
        delete_flag = storage["delete_old_price"]
    price_list = message.text
    products, uncorrected_rows = await utl.preprocessing_price_list(price_list=price_list, trader=message.from_user.id)
    await es.save_bulk_products(products=products, delete_flag=delete_flag)
    await message.answer(text=glossary.get_phrase("success_insert_price", correct_rows=len(products)), reply_markup=admin_panel_main)
    if len(uncorrected_rows) != 0:
        msg = await utl.generate_message_with_uncorrected_rows(rows=uncorrected_rows)
        await message.answer(text=msg)
    await state.finish()


async def add_option_handler(message: types.Message, state: FSMContext):
    sent_message = await message.answer("Что делать со старыми данными?", reply_markup=kb_insert_variants)
    async with state.proxy() as storage:
        storage["sent_message"] = sent_message


async def insert_method(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as storage:
        sent_message: types.Message = storage["sent_message"]
        await sent_message.edit_reply_markup(reply_markup=None)
    if call.data == "add_old_price":
        async with state.proxy() as storage:
            storage["delete_old_price"] = False
    elif call.data == "delete_old_price":
        async with state.proxy() as storage:
            storage["delete_old_price"] = True
    sent_message = await call.message.answer("Выберите способ загрузки", reply_markup=kb_insert_object)
    async with state.proxy() as storage:
        storage["sent_message"] = sent_message


async def insert_object(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as storage:
        sent_message: types.Message = storage["sent_message"]
        await sent_message.edit_reply_markup(reply_markup=None)
    if call.data == "insert_file":
        await call.message.answer("Отправь мне файл в формате .xlsx", reply_markup=kb_cancel)
        await TraderStates.get_file.set()
    elif call.data == "insert_price":
        await call.message.answer("Отправь прайс-лист", reply_markup=kb_cancel)
        await TraderStates.get_price_list.set()


def register_handlers_client(dp: Dispatcher):
    # start
    dp.register_message_handler(command_start, commands=["start"], state=None)
    # help
    dp.register_message_handler(command_help_message, commands=["help"], state='*')
    dp.register_message_handler(command_help_message, Text(startswith='помощь', ignore_case=True), state='*')
    # Cancel
    dp.register_message_handler(command_cancel_message, commands=["cancel"], state='*')
    dp.register_message_handler(command_cancel_message, Text(equals='отмена', ignore_case=True), state='*')
    # Registration new trader
    dp.register_callback_query_handler(start_registration, text=["registration"], state=None)
    dp.register_message_handler(get_shop_name_to_fio, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_shop_name)
    dp.register_message_handler(get_fio_to_tg_id, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_fio)
    # choosing
    dp.register_message_handler(add_option_handler, Text(equals='загрузить много', ignore_case=True), state=None)
    dp.register_message_handler(add_option_handler, commands=["many"], content_types=types.ContentType.TEXT, state=None)
    dp.register_callback_query_handler(
        insert_method,
       lambda callback_query: callback_query.data.startswith('delete_') or callback_query.data.startswith('add_'),
       state="*"
    )
    dp.register_callback_query_handler(
        insert_object,
       lambda callback_query: callback_query.data.startswith('insert_'),
       state="*"
    )
    # process file
    dp.register_message_handler(process_file, content_types=["document"], state=TraderStates.get_file)
    # process mass
    dp.register_message_handler(process_price, content_types=types.ContentType.TEXT, state=TraderStates.get_price_list)
