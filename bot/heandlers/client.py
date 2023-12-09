from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from bot.glossaries.glossary import glossary
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.utils.models import Trader
from bot.keyboards.client_kb import *


class TraderStates(StatesGroup):
    get_product_name = State()
    get_price = State()
    get_quantity = State()
    get_article = State()
    get_shop_name = State()
    get_fio = State()


# @dp.message_handler(commands=['start'])
async def command_start(message: types.Message) -> None:
    await message.answer(
        text=glossary.get_phrase(
            "start_greeting",
            username=message.from_user.first_name
        ),
        reply_markup=kb_registration,
    )


async def command_help(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(text=glossary.get_phrase("help"))


async def start_registration(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(text=glossary.get_phrase("get_shop_name"))
    await TraderStates.get_shop_name.set()


async def get_shop_name_to_fio(call: types.CallbackQuery, state: FSMContext) -> None:
    trader: Trader
    shop_name = call.message.text
    trader.shop_name = shop_name
    # TODO ПРОВЕРКУ НА КОРРЕКТНОСТЬ ВВОДА НАЗВАНИЯ МАГАЗИНА
    # TODO проверка на дубликат в БД
    await call.message.answer(text=glossary.get_phrase("get_shop_name"))
    await TraderStates.get_fio.set()


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start"], state=None)
    dp.register_callback_query_handler(command_help, text=["help"], state='*')
    dp.register_callback_query_handler(start_registration, text=["registration"], state=None)

