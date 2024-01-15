from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from bot import bot
from .common import get_bot_users

router = Router()


@router.callback_query(F.data == 'time')
async def send_time(callback: CallbackQuery):
    count = 0
    for count, tg_user in enumerate(await get_bot_users(), start=1):
        # print(tg_user, count)
        await bot.send_message(chat_id=tg_user.get('id'), text=f'{tg_user.get("full_name")}, сейчас <b>{datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}.</b>')
    await callback.answer(text=f'Отправлено {count} сообщений пользователям бота')
    await callback.answer()


@router.callback_query(F.data == 'good_morning')
async def send_good_morning(callback: CallbackQuery):
    count = 0
    for count, tg_user in enumerate(await get_bot_users(), start=1):
        # print(tg_user, count)
        await bot.send_message(chat_id=tg_user.get('id'), text=f'{tg_user.get("full_name")}, <b>доброе утро!</b>')
    await callback.answer(text=f'Отправлено {count} сообщений пользователям бота')
    await callback.answer()


@router.callback_query(F.data == 'time_to_sleep')
async def send_time_to_sleep(callback: CallbackQuery):
    count = 0
    for count, tg_user in enumerate(await get_bot_users(), start=1):
        # print(tg_user, count)
        await bot.send_message(chat_id=tg_user.get('id'), text=f'{tg_user.get("full_name")}, <b>пора спать!</b>')
    await callback.answer(text=f'Отправлено {count} сообщений пользователям бота')
    await callback.answer()


@router.callback_query(F.data == 'good_night')
async def send_good_night(callback: CallbackQuery):
    count = 0
    for count, tg_user in enumerate(await get_bot_users(), start=1):
        # print(tg_user, count)
        await bot.send_message(chat_id=tg_user.get('id'), text=f'{tg_user.get("full_name")}, <b>спокойной ночи!</b>')
    await callback.answer(text=f'Отправлено {count} сообщений пользователям бота')
    await callback.answer()


@router.callback_query(F.data == 'bot_users')
async def send_bot_users(callback: CallbackQuery):
    registered_users = await get_bot_users()
    if registered_users:
        text_answer = ''
        for count, user in enumerate(registered_users, start=1):
            text_answer += f"\n{count}. {str(user).replace('{', '').replace('}', '')}"
    else:
        text_answer = f'\nУ бота пока нет пользователей.'
    await callback.message.answer(text=f'Пользователи бота:{text_answer}')
    await callback.answer()


