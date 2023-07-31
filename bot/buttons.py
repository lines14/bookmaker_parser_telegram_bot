from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Сгенерировать')

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(b1)