from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

kb_registration = InlineKeyboardMarkup()
kb_registration.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'))

kb_open_admin_panel = InlineKeyboardMarkup()
kb_open_admin_panel.add(InlineKeyboardButton(text="Панель администратора", callback_data='open_admin_panel'))

admin_panel_main = InlineKeyboardMarkup()
product_list = InlineKeyboardButton(text="Список позиций 📋", callback_data='show_product_list')
add_product = InlineKeyboardButton(text="Добавить позицию ➕", callback_data='add_product')
delete_product = InlineKeyboardButton(text="Удалить позицию ➖", callback_data='delete_product')
btn_help = InlineKeyboardButton(text="Помощь 🆘", callback_data='help')
admin_panel_main.add(product_list).add(add_product).add(delete_product).add(btn_help)

kb_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data='cancel'))


async def pagination(total_pages: int, page: int = 0):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(text="⬅", callback_data=f"previous:{page}"),
        InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="None"),
        InlineKeyboardButton(text="➡", callback_data=f"next:{page}"),
    )