from aiogram import types, Dispatcher
from bot.bot_base import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.buttons import main_menu_keyboard, cancellation_keyboard, generation_keyboard
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import exceptions
from bot.get_pair_info import get_pair_info
from pathlib import Path
from main.driver.browser_utils import BrowserUtils
from selenium import common
destination = Path(__file__).resolve().parent.parent

# Машины состояний бота

class Generator(StatesGroup):
    generator1 = State()
    generator2 = State()
    generator3 = State()

# Хэндлеры бота

async def start_command(message: types.Message):
    fullname = message.from_user.full_name
    await bot.send_message(chat_id=message.from_user.id, text=f'{fullname}, привет!\nВ этом боте ты можешь автоматически генерировать баннеры.\nДля того, чтобы это сделать, тебе достаточно нажать кнопку внизу:', reply_markup=main_menu_keyboard)

async def restart_command_for_all_FSM(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=message.from_user.id, text='Для того, чтобы сгенерировать баннер, нажми кнопку внизу:', reply_markup=main_menu_keyboard)

async def start_creation(message: types.Message):
    await Generator.generator1.set()
    await bot.send_message(chat_id=message.from_user.id, text='Введи название турнира:', reply_markup=cancellation_keyboard)

async def input_tournament_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['games'] = []
        data['tournament_name'] = message.text
    await Generator.next()
    await bot.send_message(chat_id = message.from_user.id, text='Добавь ссылку на матч:', reply_markup=cancellation_keyboard)

async def input_links(message: types.Message, state: FSMContext):
    await Generator.generator2.set()
    async with state.proxy() as data:
        data['games'].append(message.text)
    await Generator.next()
    await bot.send_message(chat_id = message.from_user.id, text='Добавь ещё одну ссылку на матч или начни генерацию:', reply_markup=generation_keyboard)

async def generate(message: types.Message, state: FSMContext):
    if message.text != 'Сгенерировать!':
        await input_links(message, state)
    else:
        await bot.send_message(chat_id = message.from_user.id, text='Ожидай баннер:', reply_markup=ReplyKeyboardRemove())
        await get_pair_info(state)
        await message.reply_document(open(f'{destination}/index.jpg', 'rb'), reply_markup=main_menu_keyboard)
        await state.finish()

# Обработчики ошибок

async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    await bot.send_message(chat_id = update.message.from_user.id, text='Сервера telegram перегружены, попробуй позже =)', reply_markup=main_menu_keyboard)
    return True

async def selenium_timeout_exception_handler(update: types.Update, exception: common.exceptions.TimeoutException):
    BrowserUtils.quit_driver()
    await bot.send_message(chat_id = update.message.from_user.id, text='Проблемы с интернетом или одна из ссылок некорректна, попробуй ещё раз =)', reply_markup=cancellation_keyboard)
    return True

# Регистратура хэндлеров бота

def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(restart_command_for_all_FSM, state='*', text=['Отмена', '/start'])

    dp.register_message_handler(start_creation, text='Начать', state=None)
    dp.register_message_handler(input_tournament_name, state=Generator.generator1)
    dp.register_message_handler(input_links, state=Generator.generator2)
    dp.register_message_handler(generate, state=Generator.generator3)

    dp.register_errors_handler(exception_handler, exception=exceptions.RetryAfter)
    dp.register_errors_handler(selenium_timeout_exception_handler, exception=common.exceptions.TimeoutException)