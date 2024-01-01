from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаём роутер для режима обслуживания и ставим ему фильтры на типы
maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))


# Хэндлеры этого роутера перехватят все сообщения и колбэки, если maintenance_mode у dispatcher равен True
@maintenance_router.message()
async def any_message(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="Нажми меня", callback_data="anything")
    await message.answer(text="Бот в режиме обслуживания.\nПока можете просто потыкать в кнопку", reply_markup=builder.as_markup())


@maintenance_router.callback_query()
async def any_callback(callback: CallbackQuery):
    await callback.answer(text="Бот в режиме обслуживания. Пожалуйста, подождите.", show_alert=True)