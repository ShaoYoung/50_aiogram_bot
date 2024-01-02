from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from middlewares.month_middleware import HappyMonthMiddleware

router = Router()
# А вторую мидлварь повесим как inner на конкретный роутер, поскольку вычисление счастливого месяца нужно только в нём.
# в модуле конкретного роутера
router.message.middleware(HappyMonthMiddleware())


@router.message(Command("happymonth"))
async def cmd_happymonth(
        message: Message,
        # значение из первой мидлвари
        internal_id: int,
        # значение из второй мидлвари
        is_happy_month: bool
):
    phrases = [f"Ваш ID в нашем сервисе: {internal_id}"]
    if is_happy_month:
        phrases.append("Сейчас ваш счастливый месяц!")
    else:
        phrases.append("В этом месяце будьте осторожнее...")
    await message.answer(". ".join(phrases))
