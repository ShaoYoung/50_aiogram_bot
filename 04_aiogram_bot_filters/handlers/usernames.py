from typing import List

from aiogram import Router, F
from aiogram.types import Message

from filters.find_usernames import HasUsernamesFilter

router = Router()

# В случае нахождения хотя бы одного юзернейма фильтр HasUsernamesFilter вернёт не просто True, а словарь,
# где извлечённые юзернеймы будут лежать под ключом usernames.
# Соответственно, в хэндлере, на который навешан этот фильтр, можно добавить аргумент с точно таким же названием в функцию-обработчик.
# Вуаля! Теперь нет нужды ещё раз парсить всё сообщение и снова вытаскивать список юзернеймов:
@router.message(F.text, HasUsernamesFilter())
async def message_with_usernames(message: Message, usernames: List[str]):
    await message.reply(f'Спасибо! Обязательно подпишусь на {", ".join(usernames)}')
