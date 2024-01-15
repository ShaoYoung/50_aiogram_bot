import asyncio
import logging

# В документации по aiogram используется config_reader, а не dotenv
from config_reader import config

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import aiocron
from datetime import datetime

from handlers import common
from handlers import users_choice

# # для импорта bot в обработчиках его можно сделать глобальным
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)


def get_broadcast_list() -> list:
    return [5107502329]


async def main(maintenance_mode: bool = False):
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")

    # bot
    # # для импорта bot в обработчиках его можно сделать глобальным
    # bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=ParseMode.HTML)
    # Диспетчер
    # В реальной жизни значение maintenance_mode будет взято из стороннего источника (например, конфиг или через API)
    # bool тип является иммутабельным, его смена в рантайме ни на что не повлияет
    # dp = Dispatcher(maintenance_mode=True)
    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher(maintenance_mode=maintenance_mode, storage=MemoryStorage())
    # подключаем обработчики
    dp.include_router(common.router)
    dp.include_router(users_choice.router)

    # Чтобы выполнить задачу в определенное время (с определенной периодичностью), можно использовать библиотеку aiocron для создания расписания:
    # pip install aiocron
    # Время можно удобно настроить на сайте: https://crontab.guru/
    # Импортируйте aiocron и добавьте cron-задачу для отправки рассылки:
    @aiocron.crontab("0 * * * *")
    async def notifications():
        for tg_user in get_broadcast_list():
            await bot.send_message(chat_id=tg_user, text=f'Сейчас {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}.')

        # print(datetime.now())

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # точка входа
    asyncio.run(main())





