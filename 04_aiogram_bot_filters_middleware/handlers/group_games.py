from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.types import Message
from aiogram.filters import Command

from filters.chat_type import ChatTypeFilter

router = Router()
# Фильтры можно цеплять прямо на роутеры!
# В этом случае проверка будет выполнена ровно один раз, когда апдейт долетит до этого роутера.
# Это может быть полезно, если в фильтре вы делаете разные «тяжелые» задачи, типа обращения к Bot API
router.message.filter(ChatTypeFilter(chat_type=["group", "supergroup"]), ChatTypeFilter(chat_type=["private"]))

# Во-первых, мы импортировали встроенный фильтр Command и наш свеженаписанный ChatTypeFilter.
# Во-вторых, мы передали наш фильтр как позиционный аргумент в декоратор, указав в качестве аргументов желаемые тип(ы) чатов.
# По команде /dice будем отправлять дайс соответствующего типа, но только в группу
# @router.message(ChatTypeFilter(chat_type=["group", "supergroup"]), Command(commands=["dice"]),)
@router.message(Command(commands=["dice"]))
async def cmd_dice_in_group(message: Message):
    await message.answer_dice(emoji=DiceEmoji.DICE)


#  По командам /basketball или /football будем отправлять дайс соответствующего типа, но только в группу
# @router.message(ChatTypeFilter(chat_type=["private"]), Command(commands=["basketball", "football"]),)
@router.message(Command(commands=["basketball", "football"]))
async def cmd_basketball_in_private(message: Message):
    await message.answer_dice(emoji=DiceEmoji.BASKETBALL)