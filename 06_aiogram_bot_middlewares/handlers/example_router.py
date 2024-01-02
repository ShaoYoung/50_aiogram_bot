from aiogram import Router, F
from aiogram.types import Message
from middlewares.slowpoke_middleware import SlowpokeMiddleware
from middlewares.chat_action_middleware import ChatActionMiddleware


router = Router()
# вешаем мидлварь на роутер
router.message.middleware(SlowpokeMiddleware(sleep_sec=5))
# вешаем outer мидлварь (проверка флага "long_operation") на диспетчер
router.message.middleware(ChatActionMiddleware())


@router.message(F.text.startswith('777'), flags={'long_operation': 'sleep some seconds'})
async def any_text(message: Message):
    await message.answer(f'Привет, {message.from_user.full_name}')
    # return 'Router worked'


# Обработчик всего остального. Осторожнее, после его подключения остальные хэндлеры могут не сработать
@router.message(F.text.startswith(''))
async def cmd_incorrectly(message: Message):
    await message.reply(f'Я не знаю команду "{message.text}"')
    await message.answer('Пожалуйста, повторите ввод или нажмите кнопку')

