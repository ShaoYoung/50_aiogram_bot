# В документации по aiogram используется config_reader, а не dotenv
from config_reader import config

import os
from pathlib import Path
from dotenv import load_dotenv

import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import in_pm, bot_in_group, admin_changes_in_group, events_in_group

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
                        format="%(asctime)s %(levelname)s %(funcName)s %(message)s")

    # bot
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=None)
    # Диспетчер
    # В реальной жизни значение maintenance_mode будет взято из стороннего источника (например, конфиг или через API)
    # Помните, что т.к. bool тип является иммутабельным, его смена в рантайме ни на что не повлияет
    # dp = Dispatcher(maintenance_mode=True)
    dp = Dispatcher(maintenance_mode=maintenance_mode)

    dp.include_routers(in_pm.router, events_in_group.router, bot_in_group.router, admin_changes_in_group.router)

    # Подгрузка списка админов чата
    # Нет атрибута config.main_chat_id в приватном чате
    # Проверка не получилась

    admins = await bot.get_chat_administrators(config.main_chat_id)

    print(f'{admins=}')
    admin_ids = {admin.user.id for admin in admins}

    # await dp.start_polling(bot, admins=admin_ids)

    # Удаляем все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Поллинг новых апдейтов
    # await dp.start_polling(bot)

    # Следующий особый тип апдейтов chat_member — хитрый.
    # Дело в том, что он по умолчанию не отправляется Телеграмом, и чтобы Bot API его присылал,
    # необходимо при вызове getUpdates или setWebhook передать список нужных типов событий. Например:
    await dp.start_polling(bot, allowed_updates=["message", "inline_query", "chat_member"], admins=admin_ids)
    # Тогда после запуска бота телега начнёт присылать три указанных типа событий, но без всех остальных.
    # Разработчики aiogram подошли к теме изящно:
    # если явным образом не указывать allowed_updates, то фреймворк рекурсивно пройдёт по всем роутерам,
    # начиная с диспетчера, просмотрит хэндлеры и самостоятельно соберёт список желаемых для получения апдейтов.
    # Хотите переопределить это поведение? Передавайте allowed_updates явно.

# В профильных чатах регулярно спрашивают: «Мой код не работает, не реагирует на событие, почему?»
#
# Первое, что стоит сделать — убедиться, что нужный апдейт вообще приходит боту. Иными словами, проверить, с каким allowed_updates был вызван поллинг/вебхуки в последний раз. Проще всего это сделать прямо в браузере:
#
# Взять токен бота, назовём его AAAAA
# Сформировать ссылку вида https://api.telegram.org/botAAAAA/getWebhookInfo
# Перейти по ней
# Далее внимательно изучить JSON в ответе. Если ключ allowed_updates присутствует, то убедиться, что желаемый тип апдейтов есть в списке. Если ключа нет, это равнозначно «приходит всё, кроме chat_member»



if __name__ == "__main__":
    # точка входа, асинхронный запуск
    asyncio.run(main())


# Два новых типа апдейтов: my_chat_member и chat_member.
# Оба апдейта внутри содержат объект одного и того же типа ChatMemberUpdated.
# Разница между этими двумя событиями следующая:
# my_chat_member. Здесь всё, что касается непосредственно бота, либо ЛС юзера с ботом:
#   (раз)блокировки бота юзером в ЛС, добавление бота в группу или канал, удаление оттуда, изменение прав бота и его статуса в разных чатах и т.д.
# chat_member. Содержит все изменения состояния пользователей в группах и каналах, где бот состоит в качестве администратора:
# приход/уход юзеров в группы, подписки/отписки в каналах, изменение прав и статусов пользователей, назначение/снятие админов и многое другое.






