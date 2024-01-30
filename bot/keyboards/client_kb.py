from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton

kb_registration = InlineKeyboardMarkup()
kb_registration.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'))


product_list = KeyboardButton(text="Список позиций 📋", command='show_product_list')
add_product = KeyboardButton(text="Добавить 1 позицию", command='add_product')
edit_product = KeyboardButton(text="Изменить позицию", command='edit_product')
delete_product = KeyboardButton(text="Удалить позицию", command='delete_product')
btn_help = KeyboardButton(text="Помощь 🆘", command='help')
btn_add_file = KeyboardButton(text="Загрузить файлом", command="file")
btn_add_big_message = KeyboardButton(text="Загрузить прайс", command="price")
admin_panel_main = ReplyKeyboardMarkup(resize_keyboard=True).add(product_list, add_product).add(edit_product, delete_product).add(btn_add_file, btn_add_big_message).add(btn_help)


btn_cancel = KeyboardButton(text="Отмена", command='cancel')
kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_cancel)


btn_edit_price = KeyboardButton(text="Изменить цену", command='edit_price')
btn_edit_count = KeyboardButton(text="Изменить количество", command='edit_count')
kb_parameter_selection = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_edit_price, btn_edit_count).add(btn_cancel)


async def pagination(total_pages: int, page: int = 0):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="⬅", callback_data=f"previous:{page}"),
        InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="None"),
        InlineKeyboardButton(text="➡", callback_data=f"next:{page}"),
    )
