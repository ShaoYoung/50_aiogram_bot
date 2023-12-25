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
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.markdown import hide_link


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
    await message.reply("Hello, <b>world</b>!")
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

# Помимо обычных текстовых сообщений Telegram позволяет обмениваться медиафайлами различных типов: фото, видео, гифки, геолокации, стикеры и т.д.
# У большинства медиафайлов есть свойства file_id и file_unique_id.
# Первый можно использовать для повторной отправки одного и того же файла много раз, причём отправка будет мгновенной, т.к. сам файл уже лежит на серверах Telegram
# Следующий код заставит бота моментально ответить пользователю той же гифкой, что была прислана:
@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)

# В отличие от file_id, идентификатор file_unique_id нельзя использовать для повторной отправки или скачивания медиафайла,
# но зато он одинаковый у всех ботов для конкретного медиа.
# Нужен file_unique_id обычно тогда, когда нескольким ботам требуется знать, что их собственные file_id односятся к одному и тому же файлу.
# Если файл ещё не существует на сервере Telegram, бот может загрузить его тремя различными способами:
# как файл в файловой системе, по ссылке и напрямую набор байтов.
# Для ускорения отправки и в целом для более бережного отношения к серверам мессенджера, загрузку (upload) файлов Telegram правильнее производить один раз,
# а в дальнейшем использовать file_id, который будет доступен после первой загрузки медиа.
# В aiogram 3.x присутствуют 3 класса для отправки изображений - FSInputFile, BufferedInputFile, URLInputFile
# Пример отправки изображений всеми различными способами
@dp.message(Command('images'))
async def upload_photo(message: Message):
    # Сюда будем помещать file_id отправленных файлов, чтобы потом ими воспользоваться
    file_ids = []

    # Чтобы продемонстрировать BufferedInputFile, воспользуемся "классическим" открытием файла через `open()`. Но, вообще говоря, этот способ
    # лучше всего подходит для отправки байтов из оперативной памяти после проведения каких-либо манипуляций, например, редактированием через Pillow
    # with open("buffer_emulation.jpg", "rb") as image_from_buffer:
    #     result = await message.answer_photo(BufferedInputFile(image_from_buffer.read(), filename="image from buffer.jpg"), caption="Изображение из буфера")
    #     file_ids.append(result.photo[-1].file_id)
    #
    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("photo_ball.jpg")
    result = await message.answer_photo(image_from_pc, caption="Изображение из файла на компьютере")
    file_ids.append(result.photo[-1].file_id)

    # Отправка файла по ссылке
    image_from_url = URLInputFile('https://media.istockphoto.com/id/91712739/ru/%D1%84%D0%BE%D1%82%D0%BE/%D1%84%D1%83%D1%82%D0%B1%D0%BE%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9-%D0%BC%D1%8F%D1%87.jpg?s=612x612&w=0&k=20&c=NhkXGyEMd-Vg1tWBn1DnhPCwEzoP5YDwAqlGRBmhmqQ=')
    result = await message.answer_photo(image_from_url, caption="Изображение по ссылке")
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))


# Скачивание файлов
# Помимо переиспользования для отправки, бот может скачать медиа к себе на компьютер/сервер.
# Для этого у объекта типа Bot есть метод download().
# В примерах ниже файлы скачиваются сразу в файловую систему, но никто не мешает вместо этого сохранить в объект BytesIO в памяти, чтобы передать в какое-то приложение дальше (например, pillow).
# В случае с изображениями мы использовали не message.photo, а message.photo[-1], почему?
# Фотографии в Telegram в сообщении приходят сразу в нескольких экземплярах; это одно и то же изображение с разным размером.
# Соответственно, если мы берём последний элемент (индекс -1), то работаем с максимально доступным размером фото.
@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    print(message.photo[-1], '===', message.photo[-1].file_id)
    await bot.download(message.photo[-1], destination=f"photos/{message.photo[-1].file_id}.jpg")


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(message.sticker, destination=f"photos/{message.sticker.file_id}.webp")


# Альбомы
# То, что мы называем «альбомами» (медиагруппами) в Telegram, на самом деле отдельные сообщения с медиа,
# у которых есть общий media_group_id и которые визуально «склеиваются» на клиентах.
# Начиная с версии 3.1, в aiogram есть «сборщик» альбомов, работу с которым мы сейчас рассмотрим. Но прежде стоит упомянуть несколько особенностей медиагрупп:
# К ним нельзя прицепить инлайн-клавиатуру или отправить реплай-клавиатуру вместе с ними. Никак. Вообще никак.
# У каждого медиафайла в альбоме может быть своя подпись (caption). Если подпись есть только у одного медиа, то она будет выводиться как общая подпись ко всему альбому.
# Фотографии можно отправлять вперемешку с видео в одном альбоме, файлы (Document) и музыку (Audio) нельзя ни с чем смешивать, только с медиа того же типа.
# В альбоме может быть не больше 10 (десяти) медиафайлов.
# Теперь посмотрим, как это сделать в aiogram:
@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(caption="Общая подпись для будущего альбома")
    # album_builder = MediaGroupBuilder()
    album_builder.add(type="photo", media=FSInputFile("photos/photo_ball.jpg"))
        # caption="Подпись к конкретному медиа"

    # Если мы сразу знаем тип, то вместо общего add можно сразу вызывать add_<тип>
    # Для ссылок или file_id достаточно сразу указать значение
    # album_builder.add_photo(media="https://picsum.photos/seed/groosha/400/300")

    # album_builder.add_photo(media="<ваш file_id>")

    album_builder.add_photo(media=FSInputFile("photos/photo_ball.jpg"))
    await message.answer_media_group(
        # Не забудьте вызвать build()
        media=album_builder.build()
    )

# А вот со скачиванием альбомов всё сильно хуже...
# Как уже было сказано выше, альбомы — это просто сгруппированные отдельные сообщения, а это значит, что боту они прилетают тоже в разных апдейтах.
# Вряд ли существует 100% надёжный способ принять весь альбом одним куском, но можно попытаться сделать это с минимальными потерями. Обычно это делается через мидлвари,


# Сервисные (служебные) сообщения
# Сообщения в Telegram делятся на текстовые, медиафайлы и служебные (они же — сервисные).
# Несмотря на то, что они выглядят необычно и взаимодействие с ними ограничено, это всё ещё сообщения, у которых есть свои айдишники и даже владелец.
# Стоит отметить, что спектр применения сервисных сообщений с годами менялся и сейчас, скорее всего, ваш бот с ними работать не будет, либо только удалять.
# Пример: отправка приветственного сообщения вошедшему участнику.
# У такого служебного сообщения будет content_type равный "new_chat_members", но вообще это объект Message, у которого заполнено одноимённое поле.
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию
        # (на скриншоте выше у юзеров нет фамилии)
        await message.reply(f"Привет, {user.full_name}")
# Важно помнить, что message.new_chat_members является списком, потому что один пользователь может добавить сразу нескольких участников.
# Также не надо путать поля message.from_user и message.new_chat_members.
# Первое — это субъект, т.е. тот, кто совершил действие.
# Второе — это объекты действия. Т.е. если вы видите сообщение вида «Анна добавила Бориса и Виктора», то message.from_user — это информация об Анне, а список message.new_chat_members содержит информацию о Борисе с Виктором.
# Не стоит целиком полагаться на сервисные сообщения!


# Бонус: прячем ссылку в тексте
# Бывают ситуации, когда хочется отправить длинное сообщение с картинкой, но лимит на подписи к медиафайлам составляет всего 1024 символа против 4096 у обычного текстового, а вставлять внизу ссылку на медиа — выглядит некрасиво. Более того, когда Telegram делает предпросмотр ссылок, он берёт первую из них и считывает метатеги, в результате сообщение может отправиться не с тем превью, которое хочется увидеть.
# Для решения этой проблемы ещё много лет назад придумали подход со «скрытыми ссылками» в HTML-разметке. Суть в том, что можно поместить ссылку в пробел нулевой ширины и вставить всю эту конструкцию в начало сообщения. Для наблюдателя в сообщении никаких ссылок нет, а сервер Telegram всё видит и честно добавляет предпросмотр.
# Разработчики aiogram для этого даже сделали специальный вспомогательный метод hide_link():
# Странно работает. Ссылка отображается.
@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )














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
