from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.client_kb import *
from database.storage import es
from bot.utils import utilities as utl
from aiogram.dispatcher.filters import Text


class TraderStates(StatesGroup):
    get_shop_name = State()
    get_fio = State()


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
    if await utl.is_valid_name(name=fio):
        async with state.proxy() as storage:
            shop_name = storage["shop_name"]
        tg_id = message.from_user.id
        await es.save_trader(tg_id=tg_id, trader_name=shop_name, fio=fio)
        await message.answer(text=glossary.get_phrase("reg_finish", fio=fio), reply_markup=admin_panel_main)
        await state.finish()
    else:
        await message.answer(text=glossary.get_phrase("bad_fio"))


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
