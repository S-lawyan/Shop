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

# btn_add = InlineKeyboardButton(text="Добавить позицию", callback_data='add_position')
# btn_cancel = InlineKeyboardButton(text="Отмена", callback_data='cancel')
# btn_password = InlineKeyboardButton(text="Ввести пароль", callback_data='password')
#
# kb_password = InlineKeyboardMarkup()
# kb_password.add(btn_password)
