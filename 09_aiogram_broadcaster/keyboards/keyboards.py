from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup


def get_reply_keyboard(buttons_text: list, adjust: list, resize_keyboard: bool = True, one_time_keyboard: bool = False) -> ReplyKeyboardMarkup:
    """
    Создаёт ReplyKeyboard
    :param buttons_text: текст на кнопках
    :param adjust: количество кнопок по рядам
    :param resize_keyboard: автоматическое изменение клавиатуры под экран
    :param one_time_keyboard: автоматическое скрытие клавиатуры после нажатия кнопки
    :return: ReplyKeyboardMarkup
    """
    builder = ReplyKeyboardBuilder()
    for button_text in buttons_text:
        builder.button(text=button_text)
    builder.adjust(*adjust)
    return builder.as_markup(resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard)


def get_inline_keyboard(buttons: dict, adjust: list) -> InlineKeyboardMarkup:
    """
    Создаёт InlineKeyboard
    :param buttons: кнопки с коллбэком
    :param adjust: количество кнопок по рядам
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for key, value in buttons.items():
        builder.button(text=key, callback_data=value)
    builder.adjust(*adjust)
    return builder.as_markup()


# Клава от Артура
# from __future__ import annotations
#
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
#     KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
# import items
#
# builder = InlineKeyboardBuilder()
#
#
# # Функция для генерации инлайн-клавиатур "на лету"
# def create_inline_kb(width: int,
#                      *args: str,
#                      exit_btn: bool = False,
#                      **kwargs: str) -> InlineKeyboardMarkup:
#     # Инициализируем билдер
#     kb_builder = InlineKeyboardBuilder()
#     # Инициализируем список для кнопок
#     buttons: list[InlineKeyboardButton] = []
#
#     # Заполняем список кнопками из аргументов args и kwargs
#     if args:
#         for button in args:
#             buttons.append(InlineKeyboardButton(
#                 text=button, callback_data=button))
#     if kwargs:
#         for button, text in kwargs.items():
#             buttons.append(InlineKeyboardButton(
#                 text=text,
#                 callback_data=button))
#
#     # Распаковываем список с кнопками в билдер методом row c параметром width
#     kb_builder.row(*buttons, width=width)
#     # Добавляем в билдер последнюю кнопку, если она передана в функцию
#     if exit_btn:
#         kb_builder.row(InlineKeyboardButton(
#             text="◀️ Выйти в меню",
#             callback_data='exit_menu'
#         ))
#
#     # Возвращаем объект инлайн-клавиатуры
#     return kb_builder.as_markup()
#
#
# exit_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
#
# # iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])


