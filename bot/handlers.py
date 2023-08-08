from aiogram import types, Dispatcher
from bot.bot_base import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.buttons import main_menu_keyboard, cancellation_keyboard, generation_keyboard, check_keyboard
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import exceptions
from bot.parser import Parser
from bot.modifier import Modificator
from pathlib import Path
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from main.utils.data.config_manager import ConfigManager
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
    generator8 = State()

class Modifier(StatesGroup):
    modifier1 = State()
    modifier2 = State()

class Config(StatesGroup):
    config1 = State()

# Хэндлеры бота
# Приветствие и отмена

async def start_command(message: types.Message):
    fullname = message.from_user.full_name
    await bot.send_message(chat_id=message.from_user.id, text=f'{fullname}, привет!\nВ этом боте ты можешь автоматически генерировать баннеры.\nДля того, чтобы это сделать, тебе достаточно нажать кнопку внизу:', reply_markup=main_menu_keyboard)

async def restart_command_for_all_FSM(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id=message.from_user.id, text='Для того, чтобы сгенерировать баннер, нажми кнопку внизу:', reply_markup=main_menu_keyboard)

# Генератор

async def start_creation(message: types.Message):
    await Generator.generator1.set()
    await bot.send_message(chat_id=message.from_user.id, text='Введи вид спорта:', reply_markup=cancellation_keyboard)

async def input_competition_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['competition_type'] = message.text
    await Generator.next()
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
                await bot.send_message(chat_id = message.from_user.id, text='Бот принимает только ссылки на страницы с матчами сайта fonbet.kz, попробуй ещё раз =)', reply_markup=cancellation_keyboard)
                await Generator.generator3.set()
                await input_first_link(message)

async def check_names(message: types.Message, state: FSMContext):
    global long_names_list
    global template_set
    if DataUtils.links_processing(message.text):
        if message.text != 'Проверить названия!':
            await Generator.generator4.set()
            await input_links(message, state)
        else:
            await bot.send_message(chat_id = message.from_user.id, text='Ожидай...', reply_markup=ReplyKeyboardRemove())
            await Parser.get_pair_info(state)
            long_names_list = await Parser.check_names_length()
            if long_names_list:
                template_set = set(long_names_list)
                await Generator.generator7.set()
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
        if set((list(data.keys()))[3:]) != template_set:
            await Generator.generator7.set()
            await input_short_name(message)
        else:
            await Generator.generator6.set()
            await bot.send_message(chat_id = message.from_user.id, text='Начни генерацию кнопкой внизу:', reply_markup=generation_keyboard)
    
# Модификатор БД

async def start_modification(message: types.Message):
    await Modifier.modifier1.set()
    await bot.send_message(chat_id=message.from_user.id, text='Для корректировки уже добавленного короткого названия команды, введи полное название этой команды с сайта:', reply_markup=cancellation_keyboard)

async def check_original_name_exists(message: types.Message, state: FSMContext):
    if await Modificator.check_original_name(message.text):
        async with state.proxy() as data:
            data['original_name'] = message.text
        short_name = await Modificator.get_short_name(message.text)
        if short_name:
            await bot.send_message(chat_id=message.from_user.id, text=f'Короткое название команды: "{short_name}"\nЧтобы его перезаписать, введи новое короткое название команды:', reply_markup=cancellation_keyboard)
        else:
            await bot.send_message(chat_id=message.from_user.id, text=f'Короткое название команды отсутствует. Введи новое короткое название команды:', reply_markup=cancellation_keyboard)
        await Modifier.next()
    else:
        await bot.send_message(chat_id=message.from_user.id, text='Команда отсутствует в базе данных, начни генерацию из ссылки, чтобы добавить название:', reply_markup=main_menu_keyboard)
        await state.finish()

async def replace_short_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['short_name'] = message.text
    await Modificator.add_short_name(state)
    await bot.send_message(chat_id=message.from_user.id, text='Короткое название команды изменено', reply_markup=main_menu_keyboard)
    await state.finish()

# Конфигуратор требуемой длины названий

async def start_configuration(message: types.Message):
    await Config.config1.set()
    names_length = ConfigManager.get_config_data().names_length
    await bot.send_message(chat_id=message.from_user.id, text=f'Текущая требуемая длина коротких названий команд: {names_length}\nЧтобы изменить её, введи новое числовое значение больше нуля:', reply_markup=cancellation_keyboard)

async def set_configuration(message: types.Message, state: FSMContext):
    if message.text.isdecimal() and int(message.text) > 0:
        ConfigManager.set_names_length(int(message.text))
        await bot.send_message(chat_id=message.from_user.id, text='Требуемая длина коротких названий команд изменена', reply_markup=main_menu_keyboard)
        await state.finish()
    else:
        await bot.send_message(chat_id=message.from_user.id, text='Требуемая длина коротких названий команд должна вводиться цифрой больше нуля, попробуй ещё раз =)', reply_markup=main_menu_keyboard)
        await Config.config1.set()
        await start_configuration(message)

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

    # Приветствие и отмена

    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(restart_command_for_all_FSM, state='*', text=['Отмена', '/start'])

    # Генератор

    dp.register_message_handler(start_creation, text='Начать', state=None)
    dp.register_message_handler(input_competition_type, state=Generator.generator1)
    dp.register_message_handler(input_tournament_name, state=Generator.generator2)
    dp.register_message_handler(input_first_link, state=Generator.generator3)
    dp.register_message_handler(input_links, state=Generator.generator4)
    dp.register_message_handler(check_names, state=Generator.generator5)
    dp.register_message_handler(generate, text='Сгенерировать!', state=Generator.generator6)
    dp.register_message_handler(input_short_name, state=Generator.generator7)
    dp.register_message_handler(save_short_name, state=Generator.generator8)

    # Модификатор БД

    dp.register_message_handler(start_modification, text='Изменить короткое название', state=None)
    dp.register_message_handler(check_original_name_exists, state=Modifier.modifier1)
    dp.register_message_handler(replace_short_name, state=Modifier.modifier2)

    # Конфигуратор требуемой длины названий

    dp.register_message_handler(start_configuration, text='Изменить требуемую длину коротких названий', state=None)
    dp.register_message_handler(set_configuration, state=Config.config1)

    # Обработчики ошибок

    dp.register_errors_handler(exception_handler, exception=exceptions.RetryAfter)
    dp.register_errors_handler(selenium_timeout_exception_handler, exception=common.exceptions.TimeoutException)