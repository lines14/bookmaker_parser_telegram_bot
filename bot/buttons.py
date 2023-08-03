from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Начать')
b2 = KeyboardButton('Отмена')
b3 = KeyboardButton('Сгенерировать!')
b4 = KeyboardButton('Добавить/изменить короткие названия')

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(b1).add(b4)

cancellation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancellation_keyboard.add(b2)

generation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
generation_keyboard.add(b3).insert(b2).add(b4)