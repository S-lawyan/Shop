from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

kb_registration = InlineKeyboardMarkup()
kb_registration.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'))


product_list = KeyboardButton(text="Список позиций 📋", command='show_product_list')
add_product = KeyboardButton(text="Добавить позицию", command='add_product')
edit_product = KeyboardButton(text="Изменить позицию", command='edit_product')
delete_product = KeyboardButton(text="Удалить позицию", command='delete_product')
btn_help = KeyboardButton(text="Помощь 🆘", command='help')
admin_panel_main = ReplyKeyboardMarkup(resize_keyboard=True).add(product_list, add_product).add(edit_product, delete_product).add(btn_help) #, one_time_keyboard=True


btn_cancel = KeyboardButton(text="Отмена", command='cancel')
kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel)


async def pagination(total_pages: int, page: int = 0):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="⬅", callback_data=f"previous:{page}"),
        InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="None"),
        InlineKeyboardButton(text="➡", callback_data=f"next:{page}"),
    )


# kb_registration = InlineKeyboardMarkup()
# kb_registration.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'))
#
# kb_open_admin_panel = InlineKeyboardMarkup()
# kb_open_admin_panel.add(InlineKeyboardButton(text="Панель администратора", callback_data='open_admin_panel'))
#
# admin_panel_main = InlineKeyboardMarkup()
# product_list = InlineKeyboardButton(text="Список позиций 📋", callback_data='show_product_list')
# add_product = InlineKeyboardButton(text="Добавить позицию ➕", callback_data='add_product')
# delete_product = InlineKeyboardButton(text="Удалить позицию ➖", callback_data='delete_product')
# btn_help = InlineKeyboardButton(text="Помощь 🆘", callback_data='help')
# admin_panel_main.add(product_list).add(add_product).add(delete_product).add(btn_help)
#
# kb_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))