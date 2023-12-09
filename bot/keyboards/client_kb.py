from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

kb_registration = InlineKeyboardMarkup()
kb_registration.add(InlineKeyboardButton(text="Зарегистрироваться", callback_data='registration'))




# btn_add = InlineKeyboardButton(text="Добавить позицию", callback_data='add_position')
# btn_cancel = InlineKeyboardButton(text="Отмена", callback_data='cancel')
# btn_password = InlineKeyboardButton(text="Ввести пароль", callback_data='password')
#
# kb_password = InlineKeyboardMarkup()
# kb_password.add(btn_password)
