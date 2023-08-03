from main.utils.DB.database_utils import DatabaseUtils
from aiogram.utils import executor
from bot.bot_base import dp
from bot import handlers

async def on_startup(_):
    DatabaseUtils.sql_start()
    print('Бот успешно запущен!')

handlers.register_handler_client(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, timeout=200)