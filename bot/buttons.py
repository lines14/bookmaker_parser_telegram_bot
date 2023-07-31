from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Начать')
b2 = KeyboardButton('Отмена')
main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(b1)

cancellation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancellation_keyboard.add(b2)