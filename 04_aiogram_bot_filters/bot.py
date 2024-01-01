import asyncio
import logging

import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import group_games
from handlers import usernames
from handlers import photo_message
from handlers import message_entity_type



def get_token():
    # Хранение TOKEN в отдельном файле .env. Он добавляется в исключения .gitignore и не выгружается на GitHub
    load_dotenv()
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    TOKEN = os.getenv("BOT_TOKEN")
    # print(TOKEN)
    return TOKEN


async def main():
    # bot
    bot = Bot(token=get_token(), parse_mode=None)
    # Диспетчер
    dp = Dispatcher()
    # Подключаем обработчики.
    dp.include_routers(group_games.router)
    dp.include_routers(usernames.router)
    dp.include_routers(message_entity_type.router)
    dp.include_routers(photo_message.router)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a", format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
    # точка входа, асинхронный запуск
    asyncio.run(main())
