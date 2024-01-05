# Опишем по-быстрому простую функцию, которая будет генерировать обычную клавиатуру с кнопками в один ряд:


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str], add_button: str = '') -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param add_button: Дополнительная кнопка. По умолчанию отсутствует.
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    if add_button:
        row = [row, [KeyboardButton(text=add_button)]]
    else:
        row = [row]
    return ReplyKeyboardMarkup(keyboard=row, resize_keyboard=True)

    # Или можно так:
    # builder = ReplyKeyboardBuilder()
    # for item in items:
    #     builder.add(KeyboardButton(text=item))
    # if add_button:
    #     builder.add(KeyboardButton(text=add)button))
    # builder.adjust(3)
    # return builder.as_markup(resize_keyboard=True)


