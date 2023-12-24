import asyncio
import logging

import os
import re
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.enums import ParseMode
from aiogram import html
from aiogram.utils.formatting import Text, Bold, as_list, as_marked_section, as_key_value, HashTag
from datetime import datetime

# Диспетчер
dp = Dispatcher()


def get_token():
    # Хранение TOKEN в отдельном файле .env. Он добавляется в исключения .gitignore и не выгружается на GitHub
    load_dotenv()
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    TOKEN = os.getenv("BOT_TOKEN")
    # print(TOKEN)
    return TOKEN


# Если не указать фильтр F.text, то хэндлер сработает даже на картинку с подписью /test
@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    # await message.answer("Hello, <b>world</b>!", parse_mode=ParseMode.HTML)
    await message.answer("Hello, <b>world</b>!")
    await message.answer("Hello, *world*\!", parse_mode=ParseMode.MARKDOWN_V2)

# Экранирование передаваемых значений
@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    await message.answer(f"Hello, {html.bold(html.quote(message.from_user.full_name))}", parse_mode=ParseMode.HTML)


# Специальный инструмент, который будет собирать отдельно текст и отдельно информацию о том, какие его куски должны быть отформатированы.
@dp.message(Command("привет"))
async def cmd_hello(message: Message):
    content = Text("Hello, you wrote ", Bold(message.text))
    # Конструкция **content.as_kwargs() вернёт аргументы text, entities, parse_mode и подставит их в вызов answer().
    await message.answer(**content.as_kwargs())


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    content = as_list(
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",
        ),
        HashTag("#test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())


# Форматирование исходного сообщения по умолчанию сбивается.
# Это происходит из-за того, что message.text возвращает просто текст, без каких-либо оформлений.
# Чтобы получить текст в исходном форматировании, воспользуемся альтернативными свойствами: message.html_text или message.md_text.
# Сейчас нам нужен первый вариант. Заменяем в примере выше message.text на message.html_text и получаем корректный результат:
@dp.message(F.text.startswith("1"))
async def echo_with_time(message: Message):
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Создано в {time_now}")
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(f"{message.html_text}\n\n{added_text}", parse_mode="HTML")


# Работа с entities
# Некоторые сущности, типа e-mail, номера телефона, юзернейма и др. можно не доставать регулярными выражениями,
# а извлечь напрямую из объекта Message и поля entities, содержащего массив объектов типа MessageEntity.
# В качестве примера напишем хэндлер, который извлекает ссылку, e-mail и моноширинный текст из сообщения (по одной штуке).
@dp.message(F.text.startswith("2"))
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    print(message.entities)
    entities = message.entities or []
    for item in entities:
        print(item.type)
        if item.type in data.keys():
            # Неправильно
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            # Правильно
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )


# Команды и их аргументы
# Иногда бот может быть спроектирован так, чтобы ожидать после самой команды какие-то аргументы, вроде /ban 2d или /settimer 20h This is delayed
@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    print(message, '\n', command.args)
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )


# Префиксы в командах
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    await message.answer("Вижу команду с префиксом %!")


# Можно указать несколько префиксов....vv...
@dp.message(Command("custom2", prefix="_!"))
async def cmd_custom2(message: Message):
    await message.answer("Вижу команду с префиксом _ или !")


# Диплинки
# Существует одна команда в Telegram, у которой есть чуть больше возможностей. Это /start.
# Дело в том, что можно сформировать ссылку вида t.me/bot?start=xxx и при переходе по такой ссылке пользователю покажут
# кнопку «Начать», при нажатии которой бот получит сообщение /start xxx.
# Т.е. в ссылке зашивается некий дополнительный параметр, не требующий ручного ввода.
# Это называется диплинк и может использоваться для кучи разных вещей: шорткаты для активации различных команд, реферальная система, быстрая конфигурация бота и т.д.
# Диплинки через start отправляют пользователя в личку с ботом.
# Чтобы выбрать группу и отправить диплинк туда, замените start на startgroup.
# Также у aiogram существует удобная функция для создания диплинков прямо из вашего кода.
@dp.message(Command("help"))
@dp.message(CommandStart(deep_link=True, magic=F.args == "help"))
async def cmd_start_help(message: Message):
    await message.answer("Это сообщение со справкой")


@dp.message(CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'book_(\d+)'))))
async def cmd_start_book(message: Message, command: CommandObject):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")


@dp.message(CommandStart(deep_link=True, magic=F.args == "hello"))
async def cmd_start_help(message: Message):
    await message.answer(f"И тебе, {message.from_user.full_name}, привет!")



# Медиафайлы







async def main():
    # С parse_mode='html' надо быть аккуратнее, т.к. где-нибудь может встретиться что-то типа <текст> и бот повиснет, т.к. тег <текст> ему неизвестен
    # Выхода два:
    # 1. Экранирование
    # 2. Воспользоваться специальным инструментом, который будет собирать отдельно текст и отдельно информацию о том, какие его куски должны быть отформатированы.
    # В aiogram можно передать необходимый тип прямо в объект Bot, а если в каком-то конкретном случае нужно обойтись без разметок, то просто укажите parse_mode=None:
    # bot
    bot = Bot(token=get_token(), parse_mode=None)
    # bot = Bot(token=get_token(), parse_mode='html')
    # Подключаем обработчики. Порядок регистрации обработчиков имеет значение.
    # Если обработчики обрабатывают одинаковые типы, то работать будет тот, что объявлен раньше
    # dp.include_routers(questions.router, different_types.router)
    # dp.include_routers(different_types.router, questions.router)
    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # - удаляет все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    # - запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)


if __name__ == "__main__":
    # включаем логирование
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
    # точка входа, асинхронный запуск
    asyncio.run(main())
