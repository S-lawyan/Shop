from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from bot.config import config

kb_registration = InlineKeyboardMarkup()
kb_registration.add(InlineKeyboardButton(text="Погнали!", callback_data='registration'))


edit_name = KeyboardButton(text="Изменить имя 👤", command='edit_name')
get_chat = KeyboardButton(text="Чат 💬", command='get_chat')
btn_help = KeyboardButton(text="Помощь 🆘", command='help')
consumer_panel_main = ReplyKeyboardMarkup(resize_keyboard=True).add(edit_name, get_chat, btn_help)


chat_link_kb = InlineKeyboardMarkup()
chat_link_kb.add(InlineKeyboardButton(text="Чат для заявок 💬", url=config.bot.channel_url))


# btn_cancel = KeyboardButton(text="Отмена", command='cancel')
# kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel)
#
#
# btn_edit_price = KeyboardButton(text="Изменить цену", command='edit_price')
# btn_edit_count = KeyboardButton(text="Изменить количество", command='edit_count')
# kb_parameter_selection = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_edit_price, btn_edit_count).add(btn_cancel)
#
#
async def pagination(total_pages: int, page: int = 0):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="⬅", callback_data=f"previous:{page}"),
        InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="None"),
        InlineKeyboardButton(text="➡", callback_data=f"next:{page}"),
    )
