# Теперь создадим ещё один роутер, под которым будут два хэндлера, реагирующие на добавление бота в группу или супергруппу в роли администратора и обычного участника.
# При добавлении будем отправлять в чат сводную информацию о том, куда добавили бота:

from aiogram import F, Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

chats_variants = {
    "group": "группу",
    "supergroup": "супергруппу"
}


# Не удалось воспроизвести случай добавления бота как Restricted, поэтому примера с ним не будет


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated):
    # Самый простой случай: бот добавлен как админ.
    # Легко можем отправить сообщение
    await event.answer(
        text=f"Привет! Спасибо, что добавили меня в "
             f'{chats_variants[event.chat.type]} "{event.chat.title}" '
             f"как администратора. ID чата: {event.chat.id}"
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def bot_added_as_member(event: ChatMemberUpdated):
    # Вариант посложнее: бота добавили как обычного участника.
    # Но может отсутствовать право написания сообщений, поэтому заранее проверим.
    # chat_info = await bot.get_chat(event.chat.id)
    # if chat_info.permissions.can_send_messages:
    await event.answer(
        text=f"Привет! Спасибо, что добавили меня в "
             f'{chats_variants[event.chat.type]} "{event.chat.title}" '
             f"как обычного участника. ID чата: {event.chat.id}"
    )
    # else:
    #     print("Как-нибудь логируем эту ситуацию")


# Конвертация группы в супергруппу для бота выглядит как добавление в новый чат.
# К счастью, в этом случае боту также приходит Message с непустыми полями migrate_from_chat_id и migrate_to_chat_id.
# А дальше дело за малым: при срабатывании события my_chat_member на добавление в супергруппу проверять,
# что за последнее время (скажем, за пару секунд) не было сообщений с непустым полем migrate_to_chat_id.





