from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import FSInputFile, URLInputFile

import os
import json

from keyboards.keyboards import get_reply_keyboard
from keyboards.keyboards import get_inline_keyboard

# from bot import bot

router = Router()

# имя файла в пользователями
bot_users_file = 'bot_users.json'
# список id пользователей (глобальный, хранится в памяти во время работы бота)
registered_users_id = list()


async def set_registered_users_id() -> None:
    """
    Заполнение списка registered_users_id из файла
    :return: None
    """
    global registered_users_id
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            registered_users = json.load(json_file)
            registered_users_id.clear()
            for user in registered_users:
                registered_users_id.append(user.get('id'))


async def add_new_user(user: dict) -> bool:
    """
    Регистрация нового пользователя бота. Добавляет пользователя в файл, добавляет id пользователя в список
    :param user: пользователь (словарь{id, full_name})
    :return: bool
    """
    global registered_users_id
    registered_users_id.append(user.get('id'))
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            registered_users = json.load(json_file)
        with open(bot_users_file, 'w') as json_file:
            registered_users.append(user)
            json.dump(registered_users, json_file)
    else:
        with open(bot_users_file, 'w') as json_file:
            json.dump([user], json_file)
    return True


async def get_bot_users() -> list[dict]:
    """
    Получить пользователей бота из файла
    :return: список пользователей (словари)
    """
    if os.path.exists(bot_users_file):
        with open(bot_users_file, 'r') as json_file:
            return json.load(json_file)
    return [{}]
    # return [{"id": 5107502329, "full_name": "Nikita Shaverin"}]


async def main_menu(message: Message):
    """
    Основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    keyboard = get_reply_keyboard(['Возврат в основное меню'], [1])
    await message.answer(text='Я тестовый бот.', reply_markup=keyboard)

    buttons = {
        'Время': 'time',
        'Доброе утро': 'good_morning',
        'Пора спать': 'time_to_sleep',
        'Спокойной ночи': 'good_night',
        'Пользователи бота': 'bot_users'
    }
    keyboard = get_inline_keyboard(buttons, [1])
    await message.answer(text='Выберите, что будем отправлять:', reply_markup=keyboard)


@router.message(Command(commands=['start', 'Start', 'старт', 'Старт']))
async def cmd_start(message: Message, state: FSMContext):
    """
    Команда 'Start'. State не установлен.
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    global registered_users_id
    if not registered_users_id:
        await set_registered_users_id()

    # print(registered_users_id)
    if message.chat.id not in registered_users_id:
        if await add_new_user({'id': message.chat.id, 'full_name': message.from_user.full_name}):
            await message.answer(text='Вы у меня первый раз.\nЯ вас зарегистрировал, можете работать.')
        else:
            await message.answer(text='Вы у меня первый раз.\nЗарегистрировать вас у меня не получилось.')
    await main_menu(message)


@router.message(F.text == 'Возврат в основное меню')
async def return_in_main_menu(message: Message):
    """
    Возврат в основное меню
    :param message: сообщение
    :param state: текущий статус
    :return: None
    """
    await main_menu(message)


@router.message(Command(commands='log'))
async def cmd_log(message: Message):
    """
    Отправка файла с логами в чат пользователю
    :param message:
    :return:
    """
    await message.answer(text='Файл с логами:')
    file_from_pc = FSInputFile('log.log')
    await message.answer_document(file_from_pc)


@router.message(Command(commands='get_bot_users'))
async def cmd_get_bot_users(message: Message):
    """
    Получить пользователей бота
    :param message:
    :return:
    """
    registered_users = await get_bot_users()
    if registered_users:
        text_answer = ''
        for user in registered_users:
            text_answer += str(user).replace('{', '').replace('}', '') + '\n'
        await message.answer(text=f'Пользователи бота:\n{text_answer}')
    else:
        await message.answer(text='У бота пока нет пользователей.')


@router.message(F.text.startswith(''))
async def cmd_incorrectly(message: Message):
    """
    Обработчик всех неизвестных команд (если ни один из обработчиков этого роутера не сработал и пришёл текст
    :param message: текстовое сообщение
    :return: None
    """
    await message.reply(f'Я не знаю команду <b>"{message.text}"</b>')
    await message.answer('Пожалуйста, попробуйте ещё раз.')


@router.message(F.animation)
@router.message(F.photo)
@router.message(F.sticker)
@router.message(F.contact)
async def unknown_message(message: Message):
    """
    Обработчик неизвестных сообщений
    :param message: сообщение типа (из списка выше)
    :return: None
    """
    await message.reply(f'Я не знаю <b> что с этим делать </b>')




