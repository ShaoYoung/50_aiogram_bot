# Используем фреймворк aiogram

from config_reader import config
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from random import randint
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

# ЛС — личные сообщения, в контексте бота это диалог один-на-один с пользователем, а не группа/канал.
# Чат — общее название для ЛС, групп, супергрупп и каналов.
# Апдейт — любое событие из этого списка: сообщение, редактирование сообщения, колбэк, инлайн-запрос, платёж, добавление бота в группу и т.д.
# Хэндлер — асинхронная функция, которая получает от диспетчера/роутера очередной апдейт и обрабатывает его.
# Диспетчер — объект, занимающийся получением апдейтов от Telegram с последующим выбором хэндлера для обработки принятого апдейта.
# В aiogram хэндлерами управляет диспетчер
# Роутер — аналогично диспетчеру, но отвечает за подмножество множества хэндлеров. Можно сказать, что диспетчер — это корневой роутер.
# Фильтр — выражение, которое обычно возвращает True или False и влияет на то, будет вызван хэндлер или нет.
# Мидлварь — прослойка, которая вклинивается в обработку апдейтов.


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="a")
# Для записей с типом Secret* необходимо вызывать метод get_secret_value(), чтобы получить настоящее содержимое вместо '*******'
# Если в боте повсеместно используется определённое форматирование, то можно передать необходимый тип прямо в объект Bot,
# а если в каком-то конкретном случае нужно обойтись без разметок, то просто укажите parse_mode=None:
# например bot = Bot(token="123:abcxyz", parse_mode="HTML")
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode=None)
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Hello!")


# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")


# Хэндлер на команду /test2
@dp.message(Command("test2"))
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")


# Вместо bot.send_message(...) можно написать message.answer(...) или message.reply(...).
# В последних двух случаях не нужно подставлять chat_id, подразумевается, что он такой же, как и в исходном сообщении.
@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    # answer просто отправляет сообщение в тот же чат
    await message.answer("Это простой ответ")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    # reply делает "ответ" на сообщение из message
    await message.reply('Это ответ с "ответом"')


# Более того, для большинства типов сообщений есть вспомогательные методы вида "answer_{type}" или "reply_{type}", например:
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


# В aiogram 3.x по умолчанию обрабатываются сообщения любого типа. Исключительно текстовые сообщения принимаются через магический фильтр F. F.text
@dp.message(F.text, Command('test'))
# Если не указать фильтр F.text, то хэндлер сработает даже на картинку с подписью /test
async def any_message(message: Message):
    await message.answer("Hello, <b>world</b>!", parse_mode=ParseMode.HTML)
    await message.answer("Hello, *world*\!", parse_mode=ParseMode.MARKDOWN_V2)


# Можно заставить бота реагировать на команды с другими префиксами. Они не будут подсвечиваться и потребуют полностью ручной ввод.
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    await message.answer("Вижу команду!")


# Можно указать несколько префиксов....vv...
@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    await message.answer("И эту тоже вижу!")


# Отправка приветственного сообщения вошедшему участнику.
# У такого служебного сообщения будет content_type равный "new_chat_members", но вообще это объект Message, у которого заполнено одноимённое поле.
@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    for user in message.new_chat_members:
        # проперти full_name берёт сразу имя И фамилию
        await message.reply(f"Привет, {user.full_name}")


# КНОПКИ

# Обычные кнопки¶
# Этот вид кнопок представляет собой не что иное, как шаблоны сообщений (за исключением нескольких особых случаев).
# Принцип простой: что написано на кнопке, то и будет отправлено в текущий чат.
# Соответственно, чтобы обработать нажатие такой кнопки, бот должен распознавать входящие текстовые сообщения.
# Хэндлер, который будет при нажатии на команду /ReplyKeyboard отправлять сообщение с двумя кнопками:
@dp.message(Command("ReplyKeyboard"))
async def cmd_start(message: types.Message):
    # С точки зрения Bot API, клавиатура — это массив массивов кнопок, а если говорить проще, массив рядов.
    kb = [
        [types.KeyboardButton(text="С пюрешкой"), types.KeyboardButton(text="Без пюрешки")]
    ]
    # Для уменьшения кнопок к объекту клавиатуры надо указать дополнительный параметр resize_keyboard=True
    # Параметр input_field_placeholder, который заменит текст в пустой строке ввода, когда активна обычная клавиатура:
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='ПисАть надо ЗДЕСЬ')
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)


@dp.message(F.text.lower() == "с пюрешкой")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!")
    # Чтобы удалить кнопки, необходимо отправить новое сообщение со специальной «удаляющей» клавиатурой типа ReplyKeyboardRemove.
    # Например:
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


# Keyboard Builder
# ================
# Для более динамической генерации кнопок можно воспользоваться сборщиком клавиатур. Нам пригодятся следующие методы:
# add(<KeyboardButton>) — добавляет кнопку в память сборщика;
# adjust(int1, int2, int3...) — делает строки по int1, int2, int3... кнопок;
# as_markup() — возвращает готовый объект клавиатуры;
# button(<params>) — добавляет кнопку с заданными параметрами, тип кнопки (Reply или Inline) определяется автоматически.
# Создадим пронумерованную клавиатуру размером 4×4:
@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # добавляем кнопки
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    # делим кнопки по строкам
    builder.adjust(4, 6, 2, 4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
    )

# Специальные обычные кнопки¶
# В Telegram существует шесть специальных видов обычных кнопок, не являющихся обычными шаблонами сообщений.
# Они предназначены для:
# отправки текущей геолокации;
# отправки своего контакта с номером телефона;
# создания опроса/викторины;
# выбора и отправки боту данных пользователя с нужными критериями;
# выбора и отправки боту данных (супер)группы или канала с нужными критериями;
# запуска веб-приложения (WebApp).
@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # метод row позволяет явным образом сформировать ряд
    # из одной или нескольких кнопок. Например, первый ряд
    # будет состоять из двух кнопок...
    builder.row(
        types.KeyboardButton(text="Запросить геолокацию", request_location=True),
        types.KeyboardButton(text="Запросить контакт", request_contact=True)
    )
    # ... второй из одной ...
    builder.row(types.KeyboardButton(
        text="Создать викторину",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    # ... а третий снова из двух
    builder.row(
        types.KeyboardButton(
            text="Выбрать премиум пользователя",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="Выбрать супергруппу с форумами",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )
    # WebApp-ов пока нет, сорри :(

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )



# Инлайн-кнопки
# =============
# В отличие от обычных кнопок, инлайновые цепляются не к низу экрана, а к сообщению, с которым были отправлены.
# В этой главе мы рассмотрим два типа таких кнопок: URL и Callback.
# Ещё один — Switch — будет рассмотрен в главе про инлайн-режим.

# URL-кнопки
# Самые простые инлайн-кнопки относятся к типу URL, т.е. «ссылка». Поддерживаются только протоколы HTTP(S) и tg://
@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Оф. канал Telegram",
        url="tg://resolve?domain=telegram")
    )

    # Чтобы иметь возможность показать ID-кнопку,
    # У юзера должен быть False флаг has_private_forwards
    # user_id = 1234567890
    # chat_info = await bot.get_chat(user_id)
    # if not chat_info.has_private_forwards:
    #     builder.row(types.InlineKeyboardButton(
    #         text="Какой-то пользователь",
    #         url=f"tg://user?id={user_id}")
    #     )

    await message.answer(
        'Выберите ссылку',
        reply_markup=builder.as_markup(),
    )


# Колбэки¶
# Callback-кнопки. Это очень мощная штука, которую вы можете встретить практически везде.
# Суть в чём: у колбэк-кнопок есть специальное значение (data), по которому ваше приложение опознаёт,
# что нажато и что надо сделать. И выбор правильного data очень важен!
# Стоит также отметить, что, в отличие от обычных кнопок, нажатие на колбэк-кнопку позволяет сделать практически что угодно,
# от заказа пиццы до запуска вычислений на кластере суперкомпьютеров.
# Обработка нажатия производится с использованием хэндлера на callback_query для обработки колбэков.
# Ориентироваться надо на «значение» кнопки, т.е. на её data:
# Если сообщение отправлено из инлайн-режима, то поле message у колбэка будет пустым.
# У вас не будет возможности получить содержимое такого сообщения, если только заранее где-то его не сохранить.
@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )


@dp.message(Command("InlineKeyboardBuilder"))
async def inline_keyboard_builder(message: types.Message):
    builder = InlineKeyboardBuilder()
    # # добавляем кнопки
    for i in range(1, 17):
        builder.add(types.InlineKeyboardButton(text=str(i), callback_data=str(i)))
    # делим кнопки по строкам
    builder.adjust(4, 6, 2, 4)
    # Можно по рядам
    # builder.row(types.InlineKeyboardButton(text="Верхняя кнопка", callback_data="Верхняя кнопка"), types.InlineKeyboardButton(text="Верхняя кнопка", callback_data="Верхняя кнопка"))
    # builder.row(types.InlineKeyboardButton(text="Нижняя кнопка", callback_data="Нижняя кнопка"))
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(),
    )


# @router.message(
#     OrderFood.choosing_food_name,
#     F.text.in_(available_food_names)    -----  в списке
# )

# Хэндлер. F.data - фильтр
@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    # для скрытия "часиков", иначе 30 секунд будет демонстрироваться специальная иконка
    # можно вызвать всплывающее окно с сообщением
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )
    # но я рекомендую ставить вызов answer() в самом конце
    # или просто await callback.answer()




# Здесь хранятся пользовательские данные.
# Т.к. это словарь в памяти, то при перезапуске он очистится
user_data = {}

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



# async def update_num_text(message: types.Message, new_value: int):
#     await message.edit_text(
#         f"Укажите число: {new_value}",
#         reply_markup=get_keyboard()
#     )
# Если возникает исключение, бот его игнорирует
async def update_num_text(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard()
        )

@dp.message(Command("numbers"))
async def cmd_numbers(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard())


# фильтр callback (начало с ...). Удобно!
@dp.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: types.CallbackQuery):
    user_value = user_data.get(callback.from_user.id, 0)
    # разбор callback
    action = callback.data.split("_")[1]
    if action == "incr":
        user_data[callback.from_user.id] = user_value+1
        await update_num_text(callback.message, user_value+1)
    elif action == "decr":
        user_data[callback.from_user.id] = user_value-1
        await update_num_text(callback.message, user_value-1)
    elif action == "finish":
        await callback.message.edit_text(f"Итого: {user_value}")

    await callback.answer()




# Фабрика колбэков
# ================
# В какой-то момент возникает необходимость структурировать содержимое таких callback data, и в aiogram есть решение!
# Вы создаёте объекты типа CallbackData, указываете префикс, описываете структуру, а дальше фреймворк самостоятельно
# собирает строку с данными колбэка и, что важнее, корректно разбирает входящее значение.
# Снова разберёмся на конкретном примере; создадим класс NumbersCallbackFactory с префиксом fabnum и двумя полями action и value.
# Поле action определяет, что делать, менять значение (change) или зафиксировать (finish), а поле value показывает, на сколько изменять значение.
# По умолчанию оно будет None, т.к. для действия "finish" дельта изменения не требуется.
# Наш класс обязательно должен наследоваться от CallbackData и принимать значение префикса.
# Префикс — это общая подстрока в начале, по которой фреймворк будет определять, какая структура лежит в колбэке.
class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    # можно задавать тип value (str, int, float)
    value: Optional[int] = None

# Функция генерации клавиатуры.
# Здесь нам пригодится метод button(), который автоматически будет создавать кнопку с нужным типом,
# а от нас требуется только передать аргументы.
# В качестве аргумента callback_data вместо строки будем указывать экземпляр нашего класса NumbersCallbackFactory:
def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change", value=None)
    )
    builder.button(
        text="Подтвердить", callback_data=NumbersCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()


@dp.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    await message.answer("Укажите число", reply_markup=get_keyboard_fab())


# Наконец, переходим к главному — обработке колбэков.
# Для этого в декоратор надо передать класс, колбэки с которым мы ловим, с вызванным методом filter().
# Также появляется дополнительный аргумент с названием callback_data (имя должно быть именно таким!), и имеющим тот же тип, что и фильтруемый класс:
# обработчик всех action callback_data класса NumbersCallbackFactory (фильтрация внутри обработчика)
# @dp.callback_query(NumbersCallbackFactory.filter())
# async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: NumbersCallbackFactory):
#     # Если число нужно изменить
#     if callback_data.action == "change":
#         await callback.message.answer(f'{callback_data.action=} _ {callback_data.value=}')
#     # Если число нужно зафиксировать
#     else:
#         await callback.message.edit_text(f'{callback_data.action=} _ no value')
#     await callback.answer()


# Ещё немного конкретизируем наши хэндлеры и сделаем отдельный обработчик для числовых кнопок и для кнопки «Подтвердить».
# Фильтровать будем по значению action и в этом нам помогут Magic Filter aiogram 3.x.
# Нажатие на одну из кнопок: -2, -1, +1, +2
# обработчик action по фильтру callback_data класса NumbersCallbackFactory (фильтрация внутри обработчика)
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    await callback.message.answer(f'{callback_data.action=} _ {callback_data.value=}')
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@dp.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # Текущее значение
    await callback.message.edit_text(f'Finish')
    await callback.answer()


# Автоответ на колбэки
# Если у вас очень много колбэк-хэндлеров, на которые нужно либо просто отвечать, либо отвечать однотипно, можно немного упростить себе жизнь, воспользовавшись специальной мидлварью.
# В целом про такое мы поговорим отдельно, а сейчас просто познакомимся.
# Итак, самый простой вариант — это добавить вот такую строчку после создания диспетчера:
# dp.callback_query.middleware(CallbackAnswerMiddleware(pre=True, text="Готово!", show_alert=True))

# Увы, ситуации, когда на все колбэк-хэндлеры одинаковый ответ, довольно редки.
# К счастью, переопределить поведение мидлвари в конкретном обработчике довольно просто: достаточно пробросить аргумент callback_answer и выставить ему новые значения:



# =======================================================
# Роутеры, многофайловость и структура бота










# Для Горбушки

# TODO Бот должен реагировать только на команду /start или на нажатие кнопки Категории (текст "категории")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # С точки зрения Bot API, клавиатура — это массив массивов кнопок, а если говорить проще, массив рядов.
    kb = [
        [types.KeyboardButton(text="Категории")]
    ]
    # Для уменьшения кнопок к объекту клавиатуры надо указать дополнительный параметр resize_keyboard=True
    # Параметр input_field_placeholder, который заменит текст в пустой строке ввода, когда активна обычная клавиатура:
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='ПисАть надо ЗДЕСЬ')
    await message.answer("Я помогу вам выбрать товар", reply_markup=keyboard)


def get_inline_keyboard(text_callback: dict) -> types.InlineKeyboardMarkup:
    buttons = []
    for keys, value in text_callback.items():
        buttons.append([types.InlineKeyboardButton(text=keys, callback_data=value)])
        # print(keys, value)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@dp.message(F.text.lower() == "категории")
async def text_one(message: types.Message):
    # TODO Запрос в базу по списку категорий. Потом собрать словарь.
    text_callback = {
        "Телефоны": "cat_phone",
        "Планшеты": "cat_laptop",
        "Телевизоры": "cat_tv"
    }
    await message.answer("Категории:", reply_markup=get_inline_keyboard(text_callback))


# Хэндлер. F.data - фильтр
# @dp.callback_query(F.data == "cat_phone")
# async def send_cat_phone(callback: types.CallbackQuery):
#     await callback.message.answer(callback.data)



# Хэндлер. F.data - фильтр
@dp.callback_query(F.data.startswith("cat_"))
async def send_vendors(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    if category == "phone":
        # TODO запрос в базу по определенной категории - action (список vendor). Потом собрать словарь.
        text_callback = {
            "Apple": f"ven_apple_{category}",
            "Samsung": f"ven_samsung_{category}",
            "Xiaomi": f"ven_xiaomi_{category}"
        }
    elif category == "laptop":
        text_callback = {
            "Планшет_1": f"ven_pl1_{category}",
            "Планшет_2": f"ven_pl2_{category}",
            "Планшет_3": f"ven_pl3_{category}",
        }
    elif category == "tv":
        text_callback = {
            "ТВ_1": f"ven_tv1_{category}",
            "ТВ_2": f"ven_tv2_{category}",
            "ТВ_3": f"ven_tv3_{category}",
        }

    # print(text_callback)

    await callback.message.answer("Вендоры:", reply_markup=get_inline_keyboard(text_callback))

    # для скрытия "часиков", иначе 30 секунд будет демонстрироваться специальная иконка
    # можно вызвать всплывающее окно с сообщением
    # await callback.answer(
    #     text="Спасибо, что воспользовались ботом!",
    #     show_alert=True
    # )


# Хэндлер. F.data - фильтр
@dp.callback_query(F.data.startswith("ven_"))
async def send_descriptions(callback: types.CallbackQuery):
    vendor = callback.data.split("_")[1]
    category = callback.data.split("_")[2]
    # TODO запрос в базу по определенному vendor - action и category (список descriptions и цен). Потом собрать список строк.
    descr_list = [f"{category} {vendor}"]
    if vendor == "apple":
        descr_list.append("apple_1")
        descr_list.append("apple_2")
        descr_list.append("apple_3")
    elif vendor == "samsung":
        descr_list.append("samsung_1")
        descr_list.append("samsung_2")
        descr_list.append("samsung_3")
    elif vendor == "xiaomi":
        descr_list.append("xiaomi_1")
        descr_list.append("xiaomi_2")
        descr_list.append("xiaomi_3")
    answer_message = "\n".join(descr_list)

    await callback.message.answer(answer_message)


# Запуск процесса поллинга новых апдейтов
async def main():
# Иногда при запуске бота может потребоваться передать одно или несколько дополнительных значений.
# Это может быть какая-нибудь переменная, объект конфигурации, список чего-то, отметка времени и что угодно ещё.
# Для этого достаточно передать эти данные как именованные (kwargs) аргументы в диспетчер, либо присвоить значения, как если бы вы работали со словарём.
# Например:
# dp = Dispatcher()
# dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
# или:
# await dp.start_polling(bot, mylist=[1, 2, 3])
# Теперь переменную started_at и список mylist можно читать и писать в разных хэндлерах.
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


