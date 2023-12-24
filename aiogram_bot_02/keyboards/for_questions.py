from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    # adjust(int1, int2, int3...) — делает строки по int1, int2, int3... кнопок;
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
