from typing import Union, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message


# Помимо True/False, фильтры могут что-то передавать в хэндлеры, прошедшие фильтр.
# Это может пригодиться, когда мы не хотим в хэндлере обрабатывать сообщение, поскольку уже это сделали в фильтре.
# Чтобы стало понятнее, напишем фильтр, который пропустит сообщение, если в нём есть юзернеймы, а заодно «протолкнёт» в хэндлеры найденные значения.

class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Если entities вообще нет, вернётся None,
        # в этом случае считаем, что это пустой список
        entities = message.entities or []

        # Проверяем любые юзернеймы и извлекаем их из текста
        # методом extract_from(). Подробнее см. главу
        # про работу с сообщениями
        found_usernames = [
            item.extract_from(message.text) for item in entities
            if item.type == "mention"
        ]

        # Если юзернеймы есть, то "проталкиваем" их в хэндлер
        # по имени "usernames"
        if len(found_usernames) > 0:
            return {"usernames": found_usernames}
        # Если не нашли ни одного юзернейма, вернём False
        return False