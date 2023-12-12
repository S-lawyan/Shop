from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.client_kb import *
from database.mysqldb import db
from bot.utils import utilities as utl


class TraderStates(StatesGroup):
    get_shop_name = State()
    get_fio = State()



# ================= БЛОК ОСНОВНЫХ КОМАНД БОТА ==============================
async def command_start(message: types.Message) -> None:
    if await db.check_trader(tg_id=int(message.from_user.id)):
        await message.answer(text=glossary.get_phrase("repeat_start"), reply_markup=kb_open_admin_panel)
    else:
        await message.answer(
            text=glossary.get_phrase(
                "start_greeting",
                username=message.from_user.first_name
            ),
            reply_markup=kb_registration,
        )


async def command_help_callback(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(text=glossary.get_phrase("help"))


async def command_help_message(message: types.CallbackQuery, state: FSMContext) -> None:
    await message.answer(text=glossary.get_phrase("help"))


# ================= БЛОК РЕГИСТРАЦИИ НОВОГО ТРЕЙДЕРА ==============================
async def start_registration(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=glossary.get_phrase("get_shop_name"))
    await TraderStates.get_shop_name.set()


async def get_shop_name_to_fio(message: types.Message, state: FSMContext) -> None:
    shop_name = message.text
    async with state.proxy() as storage:
        storage["shop_name"] = shop_name
    if await db.check_shop_name(shop_name=shop_name):
        await message.answer(text=glossary.get_phrase("reply_shop_name"))
    else:
        await message.answer(text=glossary.get_phrase("get_fio"))
        await TraderStates.get_fio.set()


async def get_fio_to_tg_id(message: types.Message, state: FSMContext) -> None:
    fio = message.text
    if await utl.is_valid_name(name=fio):
        async with state.proxy() as storage:
            shop_name = storage["shop_name"]
        tg_id = message.from_user.id
        await db.save_trader(tg_id=tg_id, trader_name=shop_name, fio=fio)
        await message.answer(text=glossary.get_phrase("reg_finish", fio=fio), reply_markup=kb_open_admin_panel)
        await state.finish()
    else:
        await message.answer(text=glossary.get_phrase("bad_fio"))





def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start"], state=None)
    # При команде
    dp.register_message_handler(command_help_message, commands=["help"], state='*')
    # При нажатии на кнопку
    dp.register_callback_query_handler(command_help_callback, text=["help"], state='*')
    dp.register_callback_query_handler(start_registration, text=["registration"], state=None)
    dp.register_message_handler(get_shop_name_to_fio, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_shop_name)
    dp.register_message_handler(get_fio_to_tg_id, content_types=types.ContentType.TEXT,
                                state=TraderStates.get_fio)

