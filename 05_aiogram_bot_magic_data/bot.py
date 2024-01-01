import os
from pathlib import Path
from dotenv import load_dotenv

import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import maintenance_router
from handlers import regular_router


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

    # Подключаем обработчики. Maintenance-роутер должен быть первый
    dp.include_routers(maintenance_router.maintenance_router)
    dp.include_routers(regular_router.regular_router)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a",
                        format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
    # точка входа, асинхронный запуск, бот в режиме обслуживания
    asyncio.run(main(maintenance_mode=True))

# MagicData
# Наконец, слегка затронем MagicData.
# Этот фильтр позволяет подняться на уровень выше в плане фильтров, и оперировать значениями, которые передаются через мидлвари или в диспетчер/поллинг/вебхук.
# Предположим, у вас есть популярный бот.
# И вот настало время провести тех.обслуживание: забэкапить базу данных, почистить логи и т.д.
# Но при этом не хочется затыкать бота, чтобы не терять новую аудиторию: пусть он отвечает пользователям, мол, подождите немного.
#
# Одно из возможных решений — сделать специальный роутер, который будет перехватывать сообщения, колбэки и др.,
# если каким-либо образом в бота передано булево значение maintenance_mode, равное True.
# Простенький однофайловый пример для понимания этой логики доступен ниже:

# Magic-filter предоставляет довольно мощный инструмент для фильтрации и порой позволяет компактно описать сложную логику,
# но это не панацея и не универсальное средство.
# Если вы не можете сходу написать красивый магический фильтр, не нужно переживать; просто сделайте класс-фильтр.
# Никто вас за это не осудит.
