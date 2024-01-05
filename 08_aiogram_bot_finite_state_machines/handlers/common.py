# Общие команды
# Раз уж заговорили о сбросе состояний, давайте в файле handlers/common.py реализуем обработчики команды /start и действия «отмены».
# В первом случае должен показываться некий приветственный/справочный текст, а для отмены напишем два хэндлера:
# когда пользователь не находится ни в каком State, и когда находится в каком-либо.
#
# Все функции гарантируют отсутствие состояние и данных, убирают обычную клавиатуру, если вдруг она есть:

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    # Очистка state
    await state.clear()
    await message.answer(text="Выберите, что хотите заказать: блюда (/food) или напитки (/drink).", reply_markup=ReplyKeyboardRemove())


# Нетрудно догадаться, что следующие два хэндлера можно спокойно объединить в один, но для полноты картины оставим так

# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # State сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(text="Нечего отменять", reply_markup=ReplyKeyboardRemove())


# Отмена. Не зависимо от State
@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Действие отменено", reply_markup=ReplyKeyboardRemove())
