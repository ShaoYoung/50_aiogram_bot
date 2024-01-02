# Никаких колбэков по выходным!
# Представим, что у некоторого завода есть Telegram-бот и каждое утро заводчане должны нажимать на инлайн-кнопку,
# чтобы подтвердить своё наличие и дееспособность.
# Завод работает 5/2 и мы хотим, чтобы в субботу и воскресенье нажатия не учитывались.
# Поскольку на нажатие на кнопку завязана сложная логика (отправка данных в СКД), то в выходные будем просто «дропать» апдейт и выводить окошко с ошибкой.
from datetime import datetime
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject


# Это будет outer-мидлварь на любые колбэки
class WeekendCallbackMiddleware(BaseMiddleware):
    def is_weekend(self) -> bool:
        # 5 - суббота, 6 - воскресенье
        return datetime.now().weekday() in (5, 6)
        # return datetime.now().weekday() in (1, 5, 6)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Можно подстраховаться и игнорировать мидлварь, если она установлена по ошибке НЕ на колбэки
        if not isinstance(event, CallbackQuery):
            # тут как-нибудь залогировать
            return await handler(event, data)
        # Если сегодня не суббота и не воскресенье,
        # то продолжаем обработку.
        if not self.is_weekend():
            return await handler(event, data)
        # В противном случае отвечаем на колбэк самостоятельно и прекращаем дальнейшую обработку
        await event.answer("Какая работа? Завод остановлен до понедельника!", show_alert=True)
        # await event.message.answer("Какая работа? Завод остановлен до понедельника!")
        # await event.answer()


