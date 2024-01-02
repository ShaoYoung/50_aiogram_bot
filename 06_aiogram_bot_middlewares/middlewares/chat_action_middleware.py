# Флаги
# Ещё одна интересная фича aiogram 3.x — флаги.
# По сути, это некие «маркеры» хэндлеров, которые можно читать в мидлварях и не только.
# С помощью флагов можно пометить хэндлеры, не влезая в их внутреннюю структуру, чтобы затем что-то сделать в мидлварях, например, троттлинг.
#
# Предположим, в вашем боте много хэндлеров, которые занимаются отправкой медиафайлов или подготовкой текста для последующей отправки.
# Если такие действия выполняются долго, то хорошим тоном считается показать статус печатает или отправляет фото при помощи метода sendChatAction.
# По умолчанию, такое событие отправляется всего на 5 секунд, но автоматически закончится, если сообщение будет отправлено раньше.
# У aiogram есть вспомогательный класс ChatActionSender, который позволяет отправлять выбранный статус до тех пор, пока не выполнится отправка сообщения.
#
# Мы также не хотим внутрь каждого хэндлера запихивать работу с ChatActionSender,
# пусть это делает мидлварь с теми хэндлерами, у которых выставлен флаг long_operation со значением статуса (например, typing, choose_sticker...)

from aiogram.dispatcher.flags import get_flag
from aiogram.utils.chat_action import ChatActionSender
from aiogram import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable
from aiogram.types import Message, TelegramObject


class ChatActionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # получаем флаг из словаря data
        long_operation_type = get_flag(data, "long_operation")
        print(f'{long_operation_type=}')

        # Если такого флага на хэндлере нет
        if not long_operation_type:
            return await handler(event, data)

        await event.answer('Надо немного подождать')

        # # Если флаг есть
        # async with ChatActionSender(
        #         # нужен bot
        #         action=long_operation_type,
        #         chat_id=event.chat.id
        # ):
        #     return await handler(event, data)




