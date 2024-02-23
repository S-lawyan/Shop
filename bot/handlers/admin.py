from aiogram import types
from aiogram import Dispatcher


# @dp.message_handler(commands=['start'])
async def command_start(message: types.Message) -> None:
    if message.from_user.id != 514665692:
        return
    await message.answer("Привет АДМИН!")


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=["start"], state=None)