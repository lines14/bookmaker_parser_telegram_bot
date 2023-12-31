from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Начать')
b2 = KeyboardButton('Отмена')
b3 = KeyboardButton('Проверить названия!')
b4 = KeyboardButton('Сгенерировать!')
b5 = KeyboardButton('Изменить короткое название')
b6 = KeyboardButton('Изменить требуемую длину коротких названий')

main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(b1).insert(b5).add(b6)

cancellation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancellation_keyboard.add(b2)

check_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
check_keyboard.add(b3).insert(b2)

generation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
generation_keyboard.add(b4).insert(b2)