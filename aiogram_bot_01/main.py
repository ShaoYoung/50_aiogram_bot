import asyncio
import logging

from config_reader import config
from aiogram import Bot, Dispatcher
# from aiogram.enums.parse_mode import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router


async def main():
    # bot
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=None)
    # Диспетчер
    dp = Dispatcher()
    # подключаем обработчики
    dp.include_router(router)

    # - удаляет все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # - запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
    asyncio.run(main())
