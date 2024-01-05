# В документации по aiogram используется config_reader, а не dotenv
from config_reader import config

import os
from pathlib import Path
from dotenv import load_dotenv

import asyncio
import logging

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from handlers import common, ordering_food


# получение токена напрямую через .env
def get_token():
    # Хранение TOKEN в отдельном файле .env. Он добавляется в исключения .gitignore и не выгружается на GitHub
    load_dotenv()
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    TOKEN = os.getenv("BOT_TOKEN")
    # print(TOKEN)
    return TOKEN


async def main(maintenance_mode: bool = False):
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")

    # bot
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=None)
    # Диспетчер
    # В реальной жизни значение maintenance_mode будет взято из стороннего источника (например, конфиг или через API)
    # Помните, что т.к. bool тип является иммутабельным, его смена в рантайме ни на что не повлияет
    # dp = Dispatcher(maintenance_mode=True)
    # Если не указать storage, то по умолчанию всё равно будет MemoryStorage
    dp = Dispatcher(maintenance_mode=maintenance_mode, storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(ordering_food.router)
    # сюда импортируйте ваш собственный роутер для напитков
    # СЮДА !!!

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # точка входа, асинхронный запуск
    asyncio.run(main())



# Различные стратегии FSM
# Aiogram 3.x привнёс необычное, но интересное нововведение в механизм конечных автоматов — стратегии FSM.
# Они позволяют переопределить логику формирования пар для стейтов и данных. Всего стратегий четыре, вот они:
#
# USER_IN_CHAT — стратегия по умолчанию. Стейт и данные разные у каждого юзера в каждом чате. То есть, у юзера будут разные состояния и данные в разных группах, а также в ЛС с ботом.
# CHAT — стейт и данные общие для всего чата целиком. В ЛС разница незаметна, но в группе у всех участников будет один стейт и общие данные.
# GLOBAL_USER — во всех чатах у одного и того же юзера будет один и тот же стейт и данные.
# USER_IN_TOPIC — у юзера могут быть разные стейты в зависимости от топика в супергруппе-форуме.

# Тогда надо:
# # новый импорт
# from aiogram.fsm.strategy import FSMStrategy
#
# async def main():
#     # тут код
#     dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
#     # тут тоже код


