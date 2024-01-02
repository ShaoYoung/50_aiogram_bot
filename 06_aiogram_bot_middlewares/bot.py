import os
from pathlib import Path
from dotenv import load_dotenv

import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import example_router
from handlers import happy_month_router
from handlers import check_router
from middlewares.month_middleware import UserInternalIdMiddleware
from middlewares.callback_middleware import WeekendCallbackMiddleware
from middlewares.chat_action_middleware import ChatActionMiddleware


def get_token():
    # Хранение TOKEN в отдельном файле .env. Он добавляется в исключения .gitignore и не выгружается на GitHub
    load_dotenv()
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    TOKEN = os.getenv("BOT_TOKEN")
    # print(TOKEN)
    return TOKEN


async def main(maintenance_mode: bool = False):
    # bot
    bot = Bot(token=get_token(), parse_mode=None)
    # Диспетчер
    # В реальной жизни значение maintenance_mode будет взято из стороннего источника (например, конфиг или через API)
    # Помните, что т.к. bool тип является иммутабельным, его смена в рантайме ни на что не повлияет
    # dp = Dispatcher(maintenance_mode=True)
    dp = Dispatcher(maintenance_mode=maintenance_mode)

    dp.include_router(example_router.router)
    dp.include_router(happy_month_router.router)
    dp.include_router(check_router.router)
    # Первую мидлварь повесим как outer на диспетчер, потому что (по задумке) этот внутренний айди нужен всегда и везде.
    dp.update.outer_middleware(UserInternalIdMiddleware())
    # А вторую мидлварь повесим как inner на конкретный роутер, поскольку вычисление счастливого месяца нужно только в нём.
    # в модуле конкретного роутера

    # вешаем outer мидлварь (коллбэк) на диспетчер
    dp.callback_query.outer_middleware(WeekendCallbackMiddleware())

    # # вешаем outer мидлварь (проверка флага "long_operation") на диспетчер
    # не видит флаги хэндлеров
    # dp.update.outer_middleware(ChatActionMiddleware(bot))


    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
    # точка входа, асинхронный запуск
    asyncio.run(main())


# Оказывается, мидлварей два вида: внешние (outer) и внутренние (inner или просто «мидлвари»).
# В чём разница? Outer выполняются до начала проверки фильтрами, а inner — после.
# На практике это значит, что сообщение/колбэк/инлайн-запрос, проходящий через outer-мидлварь,
# может так ни в один хэндлер и не попасть, но если он попал в inner, то дальше 100% будет какой-то хэндлер.

