from aiogram import types, Dispatcher
from bot.bot_base import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.buttons import main_menu_keyboard, cancellation_keyboard, generation_keyboard, check_keyboard
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import exceptions
from bot.parser import Parser
from pathlib import Path
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from selenium import common
destination = Path(__file__).resolve().parent.parent

# Машины состояний бота

class Generator(StatesGroup):
    generator1 = State()
    generator2 = State()
    generator3 = State()
    generator4 = State()
    generator5 = State()
    generator6 = State()
    generator7 = State()

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
        data['links'] = []
        data['tournament_name'] = message.text
    await Generator.next()
    await input_first_link(message)

async def input_first_link(message: types.Message):
    await Generator.next()
    await bot.send_message(chat_id = message.from_user.id, text='Добавь ссылку на матч или список ссылок на матчи:', reply_markup=cancellation_keyboard)

async def input_links(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if DataUtils.links_processing(message.text):
            if message.text.count('fonbet.kz') == 1:
                data['links'].append(DataUtils.links_processing(message.text))
                await bot.send_message(chat_id = message.from_user.id, text='Добавь ещё одну ссылку на матч или проверь названия без неё:', reply_markup=check_keyboard)
            else:
                data['links'] = DataUtils.links_processing(message.text)
                await bot.send_message(chat_id = message.from_user.id, text='Проверь названия кнопкой внизу:', reply_markup=check_keyboard)
            await Generator.next()
        else:
            if data['links']:
                await bot.send_message(chat_id = message.from_user.id, text='Добавь ещё одну ссылку на матч или проверь названия без неё:', reply_markup=check_keyboard)
                await Generator.next()
            else:
                await bot.send_message(chat_id = message.from_user.id, text='Бот принимает только ссылки на сайт fonbet.kz, попробуй ещё раз =)', reply_markup=cancellation_keyboard)
                await Generator.generator2.set()
                await input_first_link(message)

async def check_names(message: types.Message, state: FSMContext):
    global long_names_list
    global template_set
    if DataUtils.links_processing(message.text):
        if message.text != 'Проверить названия!':
            await Generator.generator3.set()
            await input_links(message, state)
        else:
            await Parser.get_pair_info(state)
            long_names_list = await Parser.check_original_names()
            template_set = set(long_names_list)
            if long_names_list:
                await Generator.generator6.set()
                await input_short_name(message)
            else:
                await Generator.next()
                await bot.send_message(chat_id = message.from_user.id, text='Начни генерацию кнопкой внизу:', reply_markup=generation_keyboard)

async def generate(message: types.Message, state: FSMContext):
    await Parser.add_short_names(state)
    await Parser.generate_picture()
    await message.reply_document(open(f'{destination}/index.jpg', 'rb'), reply_markup=main_menu_keyboard)
    await state.finish()

async def input_short_name(message: types.Message):
    global long_name
    long_name = long_names_list.pop()
    await Generator.next()
    await bot.send_message(chat_id = message.from_user.id, text=f'Добавь короткое название для "{long_name}"', reply_markup=cancellation_keyboard)

async def save_short_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data[long_name] = message.text
        if set((list(data.keys()))[2:]) != template_set:
            await Generator.generator6.set()
            await input_short_name(message)
        else:
            await Generator.generator5.set()
            await bot.send_message(chat_id = message.from_user.id, text='Начни генерацию кнопкой внизу:', reply_markup=generation_keyboard)
    

# Обработчики ошибок

async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    await bot.send_message(chat_id = update.message.from_user.id, text='Сервера telegram перегружены, попробуй позже =)', reply_markup=main_menu_keyboard)
    return True

async def selenium_timeout_exception_handler(update: types.Update, exception: common.exceptions.TimeoutException):
    BrowserUtils.quit_driver()
    await bot.send_message(chat_id = update.message.from_user.id, text='Проблемы с интернетом или одна из ссылок некорректна, попробуй ещё раз =)', reply_markup=cancellation_keyboard)
    return True

# Регистратура хэндлеров бота

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(restart_command_for_all_FSM, state='*', text=['Отмена', '/start'])

    dp.register_message_handler(start_creation, text='Начать', state=None)
    dp.register_message_handler(input_tournament_name, state=Generator.generator1)
    dp.register_message_handler(input_first_link, state=Generator.generator2)
    dp.register_message_handler(input_links, state=Generator.generator3)
    dp.register_message_handler(check_names, state=Generator.generator4)
    dp.register_message_handler(generate, text='Сгенерировать!', state=Generator.generator5)
    dp.register_message_handler(input_short_name, state=Generator.generator6)
    dp.register_message_handler(save_short_name, state=Generator.generator7)

    dp.register_errors_handler(exception_handler, exception=exceptions.RetryAfter)
    dp.register_errors_handler(selenium_timeout_exception_handler, exception=common.exceptions.TimeoutException)