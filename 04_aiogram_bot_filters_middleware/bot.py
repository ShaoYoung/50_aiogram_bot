import asyncio
import logging

import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from handlers import questions, different_types
from handlers import group_games


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
    # Подключаем обработчики. Порядок регистрации обработчиков имеет значение.
    # Если обработчики обрабатывают одинаковые типы, то работать будет тот, что объявлен раньше
    dp.include_routers(group_games.router, questions.router, different_types.router)
    # dp.include_routers(different_types.router, questions.router)
    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)
    # dp.include_routers(group_games.router)

    # - удаляет все обновления, которые произошли после последнего завершения работы бота
    # Этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)

    # - запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a", format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
    # точка входа, асинхронный запуск
    asyncio.run(main())
