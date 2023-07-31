from aiogram import types, Dispatcher
from bot.bot_base import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.buttons import main_menu_keyboard
import typing
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import exceptions

# Машины состояний бота

# Машины состояний генератора

class Generator(StatesGroup):
    appeal_mobilization1 = State()
    appeal_mobilization2 = State()

# Хэндлеры бота
# Диалог приветствия и главное меню

async def start_command(message: types.Message):
    fullname = message.from_user.full_name
    await bot.send_message(chat_id = message.from_user.id, text=f'{fullname}, добрый день!\nВ этом боте ты можешь автоматически генерировать баннеры', reply_markup=intro_inline_keyboard)

async def start_inline_keyboard_callback_redirect(callback: types.CallbackQuery):
    await bot.send_message(chat_id = callback.from_user.id, text='Вы можете выбрать интересующий вас раздел в меню ниже:', reply_markup=main_menu_keyboard)
    await bot.answer_callback_query(callback.id)

async def restart_command(message: types.Message):
    # await bot.delete_message(chat_id = message.from_user.id, message_id=message.message_id)
    await bot.send_message(chat_id = message.from_user.id, text='Выберите то, что вас интересует:', reply_markup=main_menu_keyboard)

async def restart_command_inline(callback: types.CallbackQuery):
    # await bot.delete_message(chat_id = message.from_user.id, message_id=message.message_id)
    await bot.send_message(chat_id = callback.from_user.id, text='Выберите то, что вас интересует:', reply_markup=main_menu_keyboard)
    await bot.answer_callback_query(callback.id)

async def restart_command_for_all_FSM(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Выберите то, что вас интересует:', reply_markup=main_menu_keyboard)

# Стартовый диалог на тему консультации со сборщиками данных

async def start_inline_keyboard_callback_pick(callback: types.CallbackQuery):
    global reminder_state
    global aioschedule_task
    global reminder_id
    reminder_id = callback.from_user.id
    if reminder_state == 0:
        aioschedule_task = asyncio.create_task(scheduler())
        reminder_state = 1
    await bot.send_message(chat_id = callback.from_user.id, text='Какая тема вас интересует?', reply_markup=consultation_inline_keyboard)
    await bot.answer_callback_query(callback.id)

async def restart_inline_keyboard_callback_pick_without_delete_markup(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await bot.send_message(chat_id = callback.from_user.id, text='Какая тема вас интересует?', reply_markup=consultation_inline_keyboard)
    await bot.answer_callback_query(callback.id)

async def restart_inline_keyboard_callback_pick_delete_markup(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    msg = await bot.send_message(chat_id = callback.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id = callback.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
    await bot.send_message(chat_id = callback.from_user.id, text='Какая тема вас интересует?', reply_markup=consultation_inline_keyboard)
    await bot.answer_callback_query(callback.id)

async def recomendations_after_inline(callback: types.CallbackQuery):
    await bot.send_message(chat_id = callback.from_user.id, text='Все важные посты удобно разделены на хэштеги по ссылке ниже, заходите!')
    await bot.send_message(chat_id = callback.from_user.id, text='https://t.me/bettercallpavlukov/1087', reply_markup=consultation_keyboard_in_after_inline_recomendations)
    await bot.answer_callback_query(callback.id)

# Мобилизация

async def start_inline_keyboard_callback_mobilization(callback: types.CallbackQuery):
    await InlineAppealMobilization.inline_appeal_mobilization1.set()
    await bot.send_message(chat_id = callback.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_inline_keyboard_missclick)
    await bot.answer_callback_query(callback.id)

async def start_inline_keyboard_callback_mobilization_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Мобилизация'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await InlineAppealMobilization.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
    await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

async def start_inline_keyboard_callback_mobilization_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме мобилизации. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_mobilization)
        else:
            await InlineAppealMobilization.inline_appeal_mobilization2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме мобилизации. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_mobilization)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await InlineAppealMobilization.inline_appeal_mobilization2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

# Миграция

async def start_inline_keyboard_callback_migration(callback: types.CallbackQuery):
    await InlineAppealMigration.inline_appeal_migration1.set()
    await bot.send_message(chat_id = callback.from_user.id, text='Напишите, пожалуйста, ваш вопрос.\n\nВ следующем сообщении я попрошу вас оставить контакты, а сразу после вы получите от меня в подарок чек-лист "Переезд из России: деньги и документы"', reply_markup=consultation_inline_keyboard_missclick)
    await bot.answer_callback_query(callback.id)

async def start_inline_keyboard_callback_migration_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Миграция'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await InlineAppealMigration.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
    await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

async def start_inline_keyboard_callback_migration_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме миграции. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Как и обещал, рад презентовать вам свой чек-лист "Переезд из России: деньги и документы" по ссылке ниже:\nhttps://drive.google.com/file/d/1Y2rMo_GcgpF3ck2NzU0JPbQU2of3VQpT/view')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_migration)
        else:
            await InlineAppealMigration.inline_appeal_migration2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме миграции. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_migration)
            await bot.send_message(chat_id = message.from_user.id, text='Помимо этого, рад презентовать вам свой чек-лист "Переезд из России: деньги и документы" по ссылке ниже:\nhttps://drive.google.com/file/d/1Y2rMo_GcgpF3ck2NzU0JPbQU2of3VQpT/view')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await InlineAppealMigration.inline_appeal_migration2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

# Трудовые споры

async def start_inline_keyboard_callback_employment(callback: types.CallbackQuery):
    await InlineAppealEmployment.inline_appeal_employment1.set()
    await bot.send_message(chat_id = callback.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_inline_keyboard_missclick)
    await bot.answer_callback_query(callback.id)

async def start_inline_keyboard_callback_employment_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Трудовые споры'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await InlineAppealEmployment.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
    await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

async def start_inline_keyboard_callback_employment_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме трудовых споров. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_employment)
        else:
            await InlineAppealEmployment.inline_appeal_employment2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме трудовых споров. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_employment)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await InlineAppealEmployment.inline_appeal_employment2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

# Защита прав потребителей

async def start_inline_keyboard_callback_consumer(callback: types.CallbackQuery):
    await InlineAppealConsumer.inline_appeal_consumer1.set()
    await bot.send_message(chat_id = callback.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_inline_keyboard_missclick)
    await bot.answer_callback_query(callback.id)

async def start_inline_keyboard_callback_consumer_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Защита прав потребителей'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await InlineAppealConsumer.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
    await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

async def start_inline_keyboard_callback_consumer_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме защиты прав потребителей. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_consumer)
        else:
            await InlineAppealConsumer.inline_appeal_consumer2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме защиты прав потребителей. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_after_inline_consumer)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await InlineAppealConsumer.inline_appeal_consumer2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

# Другая тема

async def start_inline_keyboard_callback_another(callback: types.CallbackQuery):
    await InlineAppealAnother.inline_appeal_another1.set()
    await bot.send_message(chat_id = callback.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_inline_keyboard_missclick)
    await bot.answer_callback_query(callback.id)

async def start_inline_keyboard_callback_another_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Другая тема'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await InlineAppealAnother.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
    await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

async def start_inline_keyboard_callback_another_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по произвольной теме. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные.\nВы также можете почитать мои посты на различные юридические темы:', reply_markup=consultation_keyboard_in_after_inline_another)
        else:
            await InlineAppealAnother.inline_appeal_another2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по произвольной теме. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            msg = await bot.send_message(chat_id = message.from_user.id, text='ㅤ', reply_markup=ReplyKeyboardRemove())
            await bot.delete_message(chat_id = message.from_user.id, message_id=msg["message_id"]) # chat_id = message.from_user.id
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные.\nВы можете почитать мои посты на различные юридические темы:', reply_markup=consultation_keyboard_in_after_inline_another)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await InlineAppealAnother.inline_appeal_another2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире.', reply_markup=consultation_inline_keyboard_phone_keeper)
            await bot.send_message(chat_id = message.from_user.id, text='Вы также можете отправить свой контакт Telegram, нажав кнопку внизу', reply_markup=consultation_inline_keyboard_missclick_markup)

# Меню консультации со сборщиками данных

async def consultation_start_command(message: types.Message):
    global reminder_state
    global aioschedule_task
    global reminder_id
    reminder_id = message.from_user.id
    if reminder_state == 0:
        aioschedule_task = asyncio.create_task(scheduler())
        reminder_state = 1
    await bot.send_message(chat_id = message.from_user.id, text='Какая тема вас интересует?', reply_markup=consultation_keyboard)

async def consultation_back_for_consultation_FSM(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Вы можете обратиться и по другой теме:', reply_markup=consultation_keyboard)

async def recomendations_after(message: types.Message):
    await bot.send_message(chat_id = message.from_user.id, text='Все важные посты удобно разделены на хэштеги по ссылке ниже, заходите!')
    await bot.send_message(chat_id = message.from_user.id, text='https://t.me/bettercallpavlukov/1087', reply_markup=to_the_main_menu_keyboard)

# Мобилизация

async def consultation_mobilization(message: types.Message):
    await AppealMobilization.appeal_mobilization1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_keyboard_in_abort)

async def consultation_mobilization_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Мобилизация'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealMobilization.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

async def consultation_mobilization_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме мобилизации. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_mobilization)
        else:
            await AppealMobilization.appeal_mobilization2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме мобилизации. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_mobilization)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await AppealMobilization.appeal_mobilization2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

# Миграция

async def consultation_migration(message: types.Message):
    await AppealMigration.appeal_migration1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваш вопрос.\n\nВ следующем сообщении я попрошу вас оставить контакты, а сразу после вы получите от меня в подарок чек-лист "Переезд из России: деньги и документы"', reply_markup=consultation_keyboard_in_abort)

async def consultation_migration_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Миграция'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealMigration.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

async def consultation_migration_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме миграции. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_message(chat_id = message.from_user.id, text='Как и обещал, рад презентовать вам свой чек-лист "Переезд из России: деньги и документы" по ссылке ниже:\nhttps://drive.google.com/file/d/1Y2rMo_GcgpF3ck2NzU0JPbQU2of3VQpT/view')
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_migration)
        else:
            await AppealMigration.appeal_migration2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме миграции. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_migration)
            await bot.send_message(chat_id = message.from_user.id, text='Помимо этого, рад презентовать вам свой чек-лист "Переезд из России: деньги и документы" по ссылке ниже:\nhttps://drive.google.com/file/d/1Y2rMo_GcgpF3ck2NzU0JPbQU2of3VQpT/view')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await AppealMigration.appeal_migration2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

# Трудовые споры

async def consultation_employment(message: types.Message):
    await AppealEmployment.appeal_employment1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_keyboard_in_abort)

async def consultation_employment_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Трудовые споры'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealEmployment.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

async def consultation_employment_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме трудовых споров. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_employment)
        else:
            await AppealEmployment.appeal_employment2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме трудовых споров. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_employment)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await AppealEmployment.appeal_employment2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

# Защита прав потребителей

async def consultation_consumer(message: types.Message):
    await AppealConsumer.appeal_consumer1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_keyboard_in_abort)

async def consultation_consumer_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Защита прав потребителей'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealConsumer.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

async def consultation_consumer_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме защиты прав потребителей. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_consumer)
        else:
            await AppealConsumer.appeal_consumer2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по теме защиты прав потребителей. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=consultation_keyboard_in_consumer)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await AppealConsumer.appeal_consumer2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

# Другая тема

async def consultation_another(message: types.Message):
    await AppealAnother.appeal_another1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваш вопрос', reply_markup=consultation_keyboard_in_abort)

async def consultation_another_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Другая тема'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealAnother.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

async def consultation_another_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    global reminder_state
    global aioschedule_task
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по произвольной теме. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение! Добавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные.\nВы также можете почитать мои посты на различные юридические темы:', reply_markup=consultation_keyboard_in_another)
        else:
            await AppealAnother.appeal_another2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на консультацию по произвольной теме. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные.\nВы можете почитать мои посты на различные юридические темы:', reply_markup=consultation_keyboard_in_another)
            aioschedule_task.cancel()
            reminder_state = 0
            await state.finish()
        else:
            await AppealAnother.appeal_another2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=consultation_keyboard_in_only_telegram)

# Меню отзывов

async def feedback(message: types.Message):
    await AppealFeedback.appeal_feedback1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Здесь вы можете оставить отзыв о работе со мной. Мы опубликуем его анонимно.\nЕсли у вас есть замечания или предложения, буду рад вашей обратной связи', reply_markup=to_the_main_menu_keyboard)

async def feedback_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Отзывы'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
        data['status'] = ''
        data['phone'] = ''
    await data_base.sql_add_appeal(state)
    admins_list = await data_base.sql_get_admin()
    for id in admins_list:
        await bot.send_message(chat_id = int(id), text='Поступил отзыв. Авторизуйтесь в админ-панели бота, чтобы его проверить')
    await bot.send_message(chat_id = message.from_user.id, text='Спасибо! Я ценю вашу обратную связь', reply_markup=to_the_main_menu_keyboard)
    await state.finish()

# Меню предложений

async def suggestion(message: types.Message):
    await AppealSuggestion.appeal_suggestion1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Вы можете почитать мои посты, разделённые хэштэгами, по ссылке ниже. А если они пока-что не затронули сферу ваших интересов, можете обратиться ко мне за индивидуальной консультацией из главного меню или предложить тему для нового поста ответным сообщением', reply_markup=to_the_main_menu_keyboard)
    await bot.send_message(chat_id = message.from_user.id, text='https://t.me/bettercallpavlukov/1087')

async def suggestion_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Предложения тем для публикаций'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
        data['status'] = ''
        data['phone'] = ''
    await data_base.sql_add_appeal(state)
    admins_list = await data_base.sql_get_admin()
    for id in admins_list:
        await bot.send_message(chat_id = int(id), text='Поступило предложение темы для публикации. Авторизуйтесь в админ-панели бота, чтобы его проверить')
    await bot.send_message(chat_id = message.from_user.id, text='Ваше предложение принято, спасибо!', reply_markup=to_the_main_menu_keyboard)
    await state.finish()

# Меню сотрудничества

async def cooperation(message: types.Message):
    await AppealCooperation.appeal_cooperation1.set()
    await bot.send_message(chat_id = message.from_user.id, text='Напишите, пожалуйста, ваше предложение', reply_markup=to_the_main_menu_keyboard)

async def cooperation_add_appeal(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['stage'] = '🟢Новое'
        data['user_id'] = message.chat.id
        if message.from_user.username == None:
            data['nickname'] = ''
        else:
            data['nickname'] = message.from_user.username
        data['fullname'] = message.from_user.full_name
        data['section'] = 'Сотрудничество'
        current_datetime = datetime.now()
        data['datetime'] = str(current_datetime)[0:-7]
        data['appeal'] = message.text
    await AppealCooperation.next()
    await bot.send_message(chat_id = message.from_user.id, text='Чтобы я мог связаться с вами, оставьте ваш номер телефона без пробелов и тире', reply_markup=cooperation_keyboard_in_only_telegram)

async def cooperation_phone_processing(message: typing.Union[types.Contact, types.Message], state: FSMContext):
    if not message.text:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на тему сотрудничества. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await state.finish()
            await bot.send_contact(chat_id = message.from_user.id, phone_number = '+79933393746', first_name = 'Ярослав', last_name = 'Павлюков')
            await bot.send_message(chat_id = message.from_user.id, text='Я рассмотрю ваше предложение на тему сотрудничества.\nДобавьте меня в контакты в Telegram, чтобы я смог с вами связаться.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=to_the_main_menu_keyboard)
        else:
            await AppealCooperation.appeal_cooperation2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=cooperation_keyboard_in_only_telegram)
    else:
        async with state.proxy() as data:
            if not message.text:
                data['status'] = 'Свяжитесь со мной в Telegram'
                data['phone'] = message.contact.phone_number
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            else:
                data['status'] = 'Позвоните мне'
                data['phone'] = message.text
                phone_checked = await phone_checker(data['phone'])
                data['phone'] = await phone_checker(data['phone'])
            
        if phone_checked != 'fail':
            await data_base.sql_add_appeal(state)
            admins_list = await data_base.sql_get_admin()
            for id in admins_list:
                await bot.send_message(chat_id = int(id), text='Поступила заявка на тему сотрудничества. Авторизуйтесь в админ-панели бота, чтобы её проверить')
            await bot.send_message(chat_id = message.from_user.id, text='Я рассмотрю ваше предложение на тему сотрудничества.\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные', reply_markup=to_the_main_menu_keyboard)
            await state.finish()
        else:
            await AppealCooperation.appeal_cooperation2.set()
            await bot.send_message(chat_id = message.from_user.id, text='Некорректно введён номер телефона. Пожалуйста, введите его ещё раз без пробелов и тире', reply_markup=cooperation_keyboard_in_only_telegram)

# Обо мне

async def about_me_start_command(message: types.Message):
    await bot.send_photo(chat_id=message.chat.id, photo=open('/home/lines14/projects/judicial_telegram_bot/documents/about_me.jpg', 'rb'))
    await bot.send_message(chat_id = message.from_user.id, text='Обо мне:\n\nОбразование: Бакалавриат МГУ им. Ломоносова (2015) и магистратура ВШЭ (2017)\n\nСпециализация: трудовое и миграционное право, поддержка бизнеса, защита прав потребителей, судебные споры\n\nОпыт: 5 лет судебной практики, более 120 дел\n\n95% успешных кейсов\n\nВзыскал более 4 млн рублей для обратившихся ко мне физлиц\nОтменил более 15 выговоров\nПомог вернуться на работу десяткам клиентов\n\nБолее подробную информацию можете посмотреть на моём сайте:\nhttp://yaroslaw.org')
    await bot.send_message(chat_id = message.from_user.id, text='Подписывайтесь на мои социальные сети, чтобы быть в курсе всех юридических новостей:', reply_markup=socials_inline_keyboard)

# async def about_me_telegram(message: types.Message):
#     await bot.send_message(chat_id = message.from_user.id, text='https://t.me/bettercallpavlukov', reply_markup=about_me_keyboard)

# async def about_me_instagram(message: types.Message):
#     await bot.send_message(chat_id = message.from_user.id, text='https://www.instagram.com/bettercallpavlukov/', reply_markup=about_me_keyboard)

# async def about_me_vk(message: types.Message):
#     await bot.send_message(chat_id = message.from_user.id, text='https://vk.com/yaroslaw_org', reply_markup=about_me_keyboard)

# Автоответчик

async def scheduler():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def reminder():
    global reminder_id
    await bot.send_message(chat_id = reminder_id, text='Вы хотели получить консультацию? Буду рад помочь вам!')

# Антифлуд

async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    await bot.send_message(chat_id = update.message.from_user.id, text='Спасибо за ваше обращение, я скоро вам отвечу!\nМы работаем по будням с 10:00 до 20:00 (МСК). Сб и Вс - выходные.\nВы можете почитать мои посты на различные юридические темы:', reply_markup=consultation_keyboard_in_another)
    return True

# Меню генератора документов:

# async def generator_start_command(message: types.Message):
#     await bot.send_message(chat_id = message.from_user.id, text='Добро пожаловать в сервис генерации судебных документов. Нажмите кнопку "Создать", а затем введите требуемые данные, чтобы сформировать документ. Или можете посмотреть пример готового документа, нажав кнопку "Пример"', reply_markup=doc_generator_start_keyboard)

# async def get_example(message: types.Message):
#     await message.reply_document(open('/home/lines14/projects/judicial_telegram_bot/example/document_example.docx', 'rb'))

# async def add_data(message: types.Message):
#     await DocGenerator.doc_generator1.set()
#     await message.reply('Введите название инстанции для обращения:', reply_markup=cancel_generator_keyboard)

# async def cancel_handlers_pick_data(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return
#     await state.finish()
#     await message.reply('Вы можете начать заново с нажатия кнопки "Создать"', reply_markup=doc_generator_start_keyboard)

# async def doc_generator1(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data1'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите адрес инстанции для обращения:')

# async def doc_generator2(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data2'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите ФИО истца:')

# async def doc_generator3(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data3'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите адрес истца:')

# async def doc_generator4(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data4'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите адрес истца для корреспонденции при необходимости:')

# async def doc_generator5(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data5'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите представителя истца при необходимости:')

# async def doc_generator6(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data6'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите контактные данные представителя истца:')

# async def doc_generator7(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data7'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите ответчика:')

# async def doc_generator8(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data8'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите адрес ответчика:')

# async def doc_generator9(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data9'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите номер дела:')

# async def doc_generator10(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data10'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите дату подачи Вашего обращения:')

# async def doc_generator11(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data11'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Сформулируйте текст Вашего обращения:')

# async def doc_generator12(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data12'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Укажите процессуальный статус обращающегося:')

# async def doc_generator13(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data13'] = message.text
#     await DocGenerator.next()
#     await bot.send_message(chat_id = message.from_user.id, text='Введите инициалы обращающегося:')

# async def doc_generator14(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['user_data14'] = message.text
#     await data_print(state)
#     await bot.send_message(chat_id = message.from_user.id, text='Указанные Вами данные приняты, нажмите кнопку "Получить", чтобы выгрузить готовый документ', reply_markup=doc_generator_finish_keyboard)
#     await state.finish()

# async def get_file(message: types.Message):
#     await message.reply_document(open('/home/lines14/projects/judicial_telegram_bot/documents/your_document.docx', 'rb'))

# Регистратура хэндлеров бота

def register_handler_client(dp: Dispatcher):

    # Регистраторы диалога приветствия и главного меню со сборщиками данных

    dp.register_message_handler(start_command, commands=['start'])
    dp.register_callback_query_handler(start_inline_keyboard_callback_pick, text='yes')
    dp.register_callback_query_handler(start_inline_keyboard_callback_redirect, text=['no', 'nope'])
    dp.register_message_handler(restart_command, text=['Главное меню', 'Спасибо, буду ждать'])
    dp.register_callback_query_handler(restart_command_inline, text=['To main menu', 'Thank you'])
    dp.register_message_handler(recomendations_after, text=['Хочу почитать посты на тему мобилизации', 'Хочу почитать посты на тему миграции', 'Хочу почитать посты на тему трудовых споров', 'Хочу почитать посты на тему защиты прав потребителей', 'Хочу почитать посты'])
    dp.register_callback_query_handler(recomendations_after_inline, text=['Read mobilization', 'Read migration', 'Read employment', 'Read consumer', 'Read another'])
    dp.register_message_handler(restart_command_for_all_FSM, state='*', text=['Главное меню', '/start'])
    dp.register_message_handler(consultation_start_command, text='Получить консультацию')
    # dp.register_message_handler(generator_start_command, text='Генератор судебных документов')
    dp.register_message_handler(about_me_start_command, text='Обо мне')
    dp.register_message_handler(feedback, text='Оставить отзыв или замечание', state=None)
    dp.register_message_handler(feedback_add_appeal, state=AppealFeedback.appeal_feedback1)
    dp.register_message_handler(suggestion, text='Предложить тему для публикации', state=None)
    dp.register_message_handler(suggestion_add_appeal, state=AppealSuggestion.appeal_suggestion1)

    # Регистраторы стартового диалога на тему консультаций со сборщиками данных

    #Мобилизация

    dp.register_callback_query_handler(start_inline_keyboard_callback_mobilization, text='mobilization', state=None)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_without_delete_markup, state=InlineAppealMobilization.inline_appeal_mobilization1, text='missclick')
    dp.register_message_handler(start_inline_keyboard_callback_mobilization_add_appeal, state=InlineAppealMobilization.inline_appeal_mobilization1)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_delete_markup, state='*', text='missclick_markup')
    dp.register_message_handler(start_inline_keyboard_callback_mobilization_phone_processing, content_types=['contact', 'text'], state=InlineAppealMobilization.inline_appeal_mobilization2)

    # Миграция

    dp.register_callback_query_handler(start_inline_keyboard_callback_migration, text='migration', state=None)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_without_delete_markup, state='*', text='missclick')
    dp.register_message_handler(start_inline_keyboard_callback_migration_add_appeal, state=InlineAppealMigration.inline_appeal_migration1)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_delete_markup, state='*', text='missclick_markup')
    dp.register_message_handler(start_inline_keyboard_callback_migration_phone_processing, content_types=['contact', 'text'], state=InlineAppealMigration.inline_appeal_migration2)

    # Трудовые споры

    dp.register_callback_query_handler(start_inline_keyboard_callback_employment, text='employment', state=None)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_without_delete_markup, state='*', text='missclick')
    dp.register_message_handler(start_inline_keyboard_callback_employment_add_appeal, state=InlineAppealEmployment.inline_appeal_employment1)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_delete_markup, state='*', text='missclick_markup')
    dp.register_message_handler(start_inline_keyboard_callback_employment_phone_processing, content_types=['contact', 'text'], state=InlineAppealEmployment.inline_appeal_employment2)

    # Защита прав потребителей

    dp.register_callback_query_handler(start_inline_keyboard_callback_consumer, text='consumer', state=None)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_without_delete_markup, state='*', text='missclick')
    dp.register_message_handler(start_inline_keyboard_callback_consumer_add_appeal, state=InlineAppealConsumer.inline_appeal_consumer1)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_delete_markup, state='*', text='missclick_markup')
    dp.register_message_handler(start_inline_keyboard_callback_consumer_phone_processing, content_types=['contact', 'text'], state=InlineAppealConsumer.inline_appeal_consumer2)

    # Другая тема

    dp.register_callback_query_handler(start_inline_keyboard_callback_another, text='another', state=None)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_without_delete_markup, state='*', text='missclick')
    dp.register_message_handler(start_inline_keyboard_callback_another_add_appeal, state=InlineAppealAnother.inline_appeal_another1)
    dp.register_callback_query_handler(restart_inline_keyboard_callback_pick_delete_markup, state='*', text='missclick_markup')
    dp.register_message_handler(start_inline_keyboard_callback_another_phone_processing, content_types=['contact', 'text'], state=InlineAppealAnother.inline_appeal_another2)
    
    # Регистраторы меню консультаций со сборщиками данных

    dp.register_message_handler(consultation_back_for_consultation_FSM, state='*', text='Назад')

    # Мобилизация

    dp.register_message_handler(consultation_mobilization, text='Мобилизация', state=None)
    dp.register_message_handler(consultation_mobilization_add_appeal, state=AppealMobilization.appeal_mobilization1)
    dp.register_message_handler(consultation_mobilization_phone_processing, content_types=['contact', 'text'], state=AppealMobilization.appeal_mobilization2)

    # Миграция

    dp.register_message_handler(consultation_migration, text='Миграция', state=None)
    dp.register_message_handler(consultation_migration_add_appeal, state=AppealMigration.appeal_migration1)
    dp.register_message_handler(consultation_migration_phone_processing, content_types=['contact', 'text'], state=AppealMigration.appeal_migration2)

    # Трудовые споры

    dp.register_message_handler(consultation_employment, text='Трудовые споры', state=None)
    dp.register_message_handler(consultation_employment_add_appeal, state=AppealEmployment.appeal_employment1)
    dp.register_message_handler(consultation_employment_phone_processing, content_types=['contact', 'text'], state=AppealEmployment.appeal_employment2)

    # Защита прав потребителей

    dp.register_message_handler(consultation_consumer, text='Защита прав потребителей', state=None)
    dp.register_message_handler(consultation_consumer_add_appeal, state=AppealConsumer.appeal_consumer1)
    dp.register_message_handler(consultation_consumer_phone_processing, content_types=['contact', 'text'], state=AppealConsumer.appeal_consumer2)

    # Другая тема

    dp.register_message_handler(consultation_another, text='Задать вопрос', state=None)
    dp.register_message_handler(consultation_another_add_appeal, state=AppealAnother.appeal_another1)
    dp.register_message_handler(consultation_another_phone_processing, content_types=['contact', 'text'], state=AppealAnother.appeal_another2)

    # Регистраторы меню обо мне

    # dp.register_message_handler(about_me_telegram, text='Моя группа в Telegram')
    # dp.register_message_handler(about_me_instagram, text='Мой Instagram')
    # dp.register_message_handler(about_me_vk, text='Мой VK')

    # Регистраторы меню сотрудничества

    dp.register_message_handler(cooperation, text='Сотрудничество', state=None)
    dp.register_message_handler(cooperation_add_appeal, state=AppealCooperation.appeal_cooperation1)
    dp.register_message_handler(cooperation_phone_processing, content_types=['contact', 'text'], state=AppealCooperation.appeal_cooperation2)

    # Регистраторы генератора документов

    # dp.register_message_handler(get_example, text='Пример')
    # dp.register_message_handler(add_data, text='Создать', state=None)
    # dp.register_message_handler(cancel_handlers_pick_data, state='*', text='Отмена')
    # dp.register_message_handler(doc_generator1, state=DocGenerator.doc_generator1)
    # dp.register_message_handler(doc_generator2, state=DocGenerator.doc_generator2)
    # dp.register_message_handler(doc_generator3, state=DocGenerator.doc_generator3)
    # dp.register_message_handler(doc_generator4, state=DocGenerator.doc_generator4)
    # dp.register_message_handler(doc_generator5, state=DocGenerator.doc_generator5)
    # dp.register_message_handler(doc_generator6, state=DocGenerator.doc_generator6)
    # dp.register_message_handler(doc_generator7, state=DocGenerator.doc_generator7)
    # dp.register_message_handler(doc_generator8, state=DocGenerator.doc_generator8)
    # dp.register_message_handler(doc_generator9, state=DocGenerator.doc_generator9)
    # dp.register_message_handler(doc_generator10, state=DocGenerator.doc_generator10)
    # dp.register_message_handler(doc_generator11, state=DocGenerator.doc_generator11)
    # dp.register_message_handler(doc_generator12, state=DocGenerator.doc_generator12)
    # dp.register_message_handler(doc_generator13, state=DocGenerator.doc_generator13)
    # dp.register_message_handler(doc_generator14, state=DocGenerator.doc_generator14)
    # dp.register_message_handler(get_file, text='Получить')

    # Антифлуд

    dp.register_errors_handler(exception_handler, exception=exceptions.RetryAfter)