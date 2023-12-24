from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.enums import ParseMode
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
# from aiogram.methods.forward_message import ForwardMessage
# from aiogram.fsm.context import FSMContext
# from aiogram.types.callback_query import CallbackQuery

import sys
sys.path.append('../')
import core_functions as cf

router = Router()


# генератор inline_keyboard
def get_inline_keyboard(text_callback: dict) -> types.InlineKeyboardMarkup:
    buttons = []
    for keys, value in text_callback.items():
        buttons.append([types.InlineKeyboardButton(text=keys, callback_data=value)])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


# обработчик команды "старт"
@router.message(Command("старт"))
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Клавиатура — массив рядов.
    kb = [
        [types.KeyboardButton(text="Категории")]
    ]
    # Для уменьшения кнопок к объекту клавиатуры надо указать дополнительный параметр resize_keyboard=True
    # Параметр input_field_placeholder, который заменит текст в пустой строке ввода, когда активна обычная клавиатура:
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='Напишите сообщение')
    await message.answer("Я помогу вам выбрать товар", reply_markup=keyboard)


# обработчик текста "категории" или нажатия кнопки "Категории"
@router.message(F.text.lower() == "категории")
async def text_one(message: types.Message):
    categories = cf.get_categories_from_warehouse()
    text_callback = {}
    for category in categories:
        text_callback.update({category: f'cat_{category}'})
    await message.answer("Выберите категорию", reply_markup=get_inline_keyboard(text_callback))


# обработчик категории
@router.callback_query(F.data.startswith("cat_"))
async def send_vendors(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    vendors = cf.get_vendors_by_category(category)
    text_callback = {}
    for vendor in vendors:
        text_callback.update({vendor: f'ven_{vendor}_{category}'})
    await callback.message.answer(f"Категория {category}\nВыберите вендора", reply_markup=get_inline_keyboard(text_callback))


# обработчик вендора
@router.callback_query(F.data.startswith("ven_"))
async def send_descriptions(callback: types.CallbackQuery):
    vendor = callback.data.split("_")[1]
    category = callback.data.split("_")[2]
    descr_list = cf.get_description_by_category_vendor(category, vendor)
    descr_list.insert(0, f'<b>Категория "{category}", вендор "{vendor}"</b>')
    # print(descr_list)
    answer_messages_list = []
    answer_message = ''
    temp = ''
    for product in descr_list:
        temp += product
        temp += '\n'
        if len(temp) > 4096:
            temp = f"{product}\n"
            answer_messages_list.append(answer_message)
            answer_message = ''
        else:
            answer_message = temp
    answer_messages_list.append(answer_message)
    for answer_message in answer_messages_list:
        # print(len(answer_message))
        await callback.message.answer(answer_message, parse_mode=ParseMode.HTML)


# Обработчик всего остального
@router.message(F.text.startswith(""))
async def cmd_incorrectly(message: types.Message):
    await message.reply(f'Я не знаю команду "{message.text}"')
    await message.answer('Пожалуйста, повторите ввод или нажмите кнопку')


