from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command("checkin"))
async def cmd_checkin(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Я на работе!", callback_data="checkin")
    await message.answer(text="Нажимайте эту кнопку только по будним дням!", reply_markup=builder.as_markup())


@router.callback_query(F.data == "checkin")
async def callback_checkin(callback: CallbackQuery):
    # Тут может быть много всякого кода
    await callback.answer(text=f'Спасибо, {callback.from_user.full_name}, что подтвердили своё присутствие!', show_alert=True)
    # await callback.message.answer(text=f'Спасибо, {callback.from_user.full_name}, что подтвердили своё присутствие!')
    # await callback.answer()
