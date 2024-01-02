# Передача аргументов в мидлварь
# Мы используем мидлвари-классы, соответственно, у них есть конструктор.
# Это позволяет кастомизировать поведение кода внутри, управляя им снаружи.
# Например, из файла конфигурации.
# Напишем бесполезную, но наглядную "замедляющую" мидлварь, которая будет тормозить обработку входящих сообщений на указанное количество секунд

import asyncio
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SlowpokeMiddleware(BaseMiddleware):
    def __init__(self, sleep_sec: int):
        self.sleep_sec = sleep_sec

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Ждём указанное количество секунд и передаём управление дальше по цепочке
        # (это может быть как хэндлер, так и следующая мидлварь)
        await asyncio.sleep(self.sleep_sec)
        result = await handler(event, data)
        # Если в хэндлере сделать return, то это значение попадёт в result
        print(f"Handler was delayed by {self.sleep_sec} seconds")
        print(result)
        return result


