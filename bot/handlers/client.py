from aiogram import types
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.client_kb import *
from bot.utils import utilities as utl
from aiogram.dispatcher.filters import Text
from bot.service import dp, es
from bot.filters import IsDirect


class TraderStates(StatesGroup):
    get_fio = State()


# ================= БЛОК ОСНОВНЫХ КОМАНД БОТА ==============================
@dp.message_handler(commands=["start"], state=None)
async def command_start(message: types.Message) -> None:
    if await es.check_in_consumers_index(field="tg_id", value=int(message.from_user.id)):
        await message.answer(text=glossary.get_phrase("consumer_main_menu"), reply_markup=consumer_panel_main)
    else:
        await message.answer(
            text=glossary.get_phrase(
                "start_greeting",
                username=message.from_user.first_name
            ),
            reply_markup=kb_registration,
        )


@dp.message_handler(IsDirect(), commands=["help"], state='*')
@dp.message_handler(IsDirect(), Text(startswith="помощь", ignore_case=True), state='*')
async def command_help_message(message: types.Message) -> None:
    await message.answer(text=glossary.get_phrase("help"))


@dp.message_handler(IsDirect(), commands=["chat"], state='*')
@dp.message_handler(IsDirect(), Text(startswith="чат", ignore_case=True), state='*')
async def get_chat_link(message: types.Message) -> None:
    if await es.check_in_consumers_index(field="tg_id", value=int(message.from_user.id)):
        await message.answer(text=glossary.get_phrase("chat_link"), reply_markup=chat_link_kb)
    else:
        await message.answer(text=glossary.get_phrase("non_register_user"), reply_markup=kb_registration)


# ================= БЛОК РЕГИСТРАЦИИ НОВОГО CONSUMER-a ==============================
@dp.callback_query_handler(IsDirect(), text=["registration"], state=None)
async def start_registration(call: types.CallbackQuery) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=glossary.get_phrase("get_fio"))
    await TraderStates.get_fio.set()


@dp.message_handler(IsDirect(), content_types=types.ContentType.TEXT, state=TraderStates.get_fio)
async def get_fio_finish_registration(message: types.Message, state: FSMContext) -> None:
    fio = message.text
    # if await utl.is_valid_name(name=fio):
    tg_id = message.from_user.id
    await es.save_consumer(tg_id=tg_id, fio=fio)
    await message.answer(
        text=glossary.get_phrase(
            "reg_finish",
            fio=fio,
            url=config.bot.channel_url,
        ),
        reply_markup=consumer_panel_main,
    )
    await state.finish()
    # else:
    #     await message.answer(text=glossary.get_phrase("bad_fio"))


@dp.message_handler(IsDirect(), content_types=types.ContentType.ANY, state=None)
async def unknown_event(message: types.Message) -> None:
    await message.answer(text=glossary.get_phrase("unknown_event"))
