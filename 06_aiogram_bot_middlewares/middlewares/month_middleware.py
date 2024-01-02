# Передача данных из мидлвари
# Как мы уже выяснили ранее, при обработке очередного апдейта мидлварям доступен словарь data,
# в котором лежат различные полезные объекты: бот, автор апдейта (event_from_user) и т.д.
# Но также мы можем наполнять этот словарь чем угодно.
# Более того, позднее вызванные мидлвари могут видеть то, что туда положили ранее вызванные.
#
# Рассмотрим следующую ситуацию:
# первая мидлварь по Telegram ID юзера получает какой-то внутренний айдишник (например, из якобы стороннего сервиса),
# а вторая мидлварь по этому внутреннему айди вычисляет «счастливый месяц» пользователя (остаток от деления внутреннего айди на 12).
# Всё это кладётся в хэндлер, который радует или огорчает человека, вызвавшего команду.

from random import randint
from typing import Any, Callable, Dict, Awaitable
from datetime import datetime
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# Мидлварь, которая достаёт внутренний айди юзера из какого-то стороннего сервиса
class UserInternalIdMiddleware(BaseMiddleware):
    # Разумеется, никакого сервиса у нас в примере нет, а только суровый рандом:
    def get_internal_id(self, user_id: int) -> int:
        # return randint(100_000_000, 900_000_000) + user_id
        return user_id

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # получаем user из уже доступного словаря data
        user = data["event_from_user"]
        # print(f'{user=}')
        # создаём новый ключ со случайным id
        data["internal_id"] = self.get_internal_id(user.id)
        return await handler(event, data)


# Мидлварь, которая вычисляет "счастливый месяц" пользователя
class HappyMonthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Получаем значение из предыдущей мидлвари
        internal_id: int = data["internal_id"]
        # текущий месяц
        current_month: int = datetime.now().month
        is_happy_month: bool = (internal_id % 12) == current_month
        # Кладём True или False в data, чтобы забрать в хэндлере
        data["is_happy_month"] = is_happy_month
        return await handler(event, data)

