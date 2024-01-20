from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.keyboards.client_kb import *
from database.storage import es
from bot.utils import utilities as utl
from aiogram.dispatcher.filters import Text, ChatTypeFilter


class TraderStates(StatesGroup):
    get_fio = State()


# ================= БЛОК ОСНОВНЫХ КОМАНД БОТА ==============================
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


async def command_help_message(message: types.Message) -> None:
    await message.answer(text=glossary.get_phrase("help"))


# ================= БЛОК РЕГИСТРАЦИИ НОВОГО CONSUMER-a ==============================
async def start_registration(call: types.CallbackQuery) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=glossary.get_phrase("get_fio"))
    await TraderStates.get_fio.set()


async def get_fio_finish_registration(message: types.Message, state: FSMContext) -> None:
    fio = message.text
    if await utl.is_valid_name(name=fio):
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
    else:
        await message.answer(text=glossary.get_phrase("bad_fio"))


async def get_chat_link(message: types.Message) -> None:
    await message.answer(text=glossary.get_phrase("chat_link"), reply_markup=chat_link_kb)


def register_handlers_client(dp: Dispatcher):
    # start
    dp.register_message_handler(command_start, ChatTypeFilter(types.ChatType.PRIVATE), commands=["start"], state=None)
    # help
    dp.register_message_handler(
        command_help_message,
        ChatTypeFilter(types.ChatType.PRIVATE),
        commands=["help"],
        state='*'
    )
    dp.register_message_handler(
        command_help_message,
        ChatTypeFilter(types.ChatType.PRIVATE),
        Text(startswith='помощь',
             ignore_case=True),
        state='*'
    )
    # registration new consumer
    dp.register_callback_query_handler(
        start_registration,
        ChatTypeFilter(types.ChatType.PRIVATE),
        text=["registration"],
        state=None
    )
    dp.register_message_handler(get_fio_finish_registration, ChatTypeFilter(types.ChatType.PRIVATE), content_types=types.ContentType.TEXT,
                                state=TraderStates.get_fio)
    # get chat
    dp.register_message_handler(get_chat_link, ChatTypeFilter(types.ChatType.PRIVATE), text=["chat"], state='*')
    dp.register_message_handler(get_chat_link, ChatTypeFilter(types.ChatType.PRIVATE), Text(startswith='чат', ignore_case=True), state='*')
