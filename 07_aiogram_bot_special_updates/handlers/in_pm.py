# Научимся реагировать на события блокировки/разблокировки бота через aiogram на простом примере:
# пусть у нас есть список из двух активных пользователей бота с айди 111 и 222.
# По команде /start добавим юзера в список рассылки, а по команде /users будем выводить айди тех,
# кто не заблокировал бота (другими словами, при блокировке бота будем убирать айди из списка, а при разблокировке снова добавим).
#
# Вот готовый роутер под вышеописанные условия:
from aiogram import F, Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.filters.command import CommandStart, Command
from aiogram.types import ChatMemberUpdated, Message

router = Router()
# фильтры на тип чата - private
router.my_chat_member.filter(F.chat.type == "private")
# Обратите внимание: для хэндлеров на апдейт my_chat_member мы используем фильтр ChatMemberUpdatedFilter
# с указанием отлавливаемого результата ПОСЛЕ (т.е. атрибут new_chat_member у апдейта).
# Т.е. в данном случае нас не интересует, в каком состоянии был юзер ДО.
router.message.filter(F.chat.type == "private")

# Исключительно для примера. Множество юзеров
# В реальной жизни используйте более надёжные источники id юзеров
users = {111, 222}


# Фильтр на ChatMemberUpdated (юзер заблокирован)
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    # удаляем id юзера из множества
    users.discard(event.from_user.id)


# Фильтр на ChatMemberUpdated (юзер разблокирован)
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    # добавляем id юзера в множество
    users.add(event.from_user.id)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello")
    users.add(message.from_user.id)


@router.message(Command("users"))
async def cmd_users(message: Message):
    # построчно выводим множество юзеров
    await message.answer("\n".join(f"• {user_id}" for user_id in users))


