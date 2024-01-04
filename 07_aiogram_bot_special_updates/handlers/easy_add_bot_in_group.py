# Ещё частый вопрос от начинающих разработчиков: «как поймать событие добавления бота в группу?».
# Что ж, давайте разбираться. Но перед этим посмотрим, какие вообще могут быть «статусы» пользователя:
#
# creator (он же owner) — владелец чата. Судя по всему, бот не может иметь такой статус. Владелец безальтернативно имеет все возможные права в чате, кроме «анонимности», она переключается туда-сюда свободно.
# administrator — любой другой администратор. В интерфейсе приложений можно убрать ему вообще все права, но он всё равно останется администратором и сможет, например, читать Recent Actions и игнорировать slow mode.
# member — участник чата с правами по умолчанию. Узнать эти «права по умолчанию» в случае с группами можно, вызвав API-метод getChat и посмотрев поле permissions.
# restricted — пользователь, ограниченный в каких-то правах. Например, находящийся в т.н. "read-only". ВАЖНО: в состоянии restricted юзер может как находиться в группе, так и не находиться, поэтому у ChatMemberRestricted надо дополнительно проверять флаг is_member.
# left — «он улетел, но обещал вернуться», т.е. пользователь вышел из группы, но при желании может снова зайти. И на момент выхода он не был в состоянии restricted.
# banned — пользователь забанен и не может вернуться самостоятельно, пока его не разбанят.

# Имея под рукой вышеизложенную информацию, нетрудно догадаться, что событие «бота добавили в группу»
# — это переход из набора состояний {banned, left, restricted(is_member=False)} в набор {restricted(is_member=True), member, administrator}.
# Такой переход по-английски называется transition, и в aiogram 3.x уже есть заготовки.

from aiogram import F, Router
router = Router()

# Вариант №1: тупо перечислим все состояния ДО и ПОСЛЕ:
# Вертикальная черта означает "или", битовый оператор ">>" показывает направление перехода,
# а символы «плюс» и «минус» около RESTRICTED относятся к флагу is_member (плюс - True, минус - False).
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, RESTRICTED, ADMINISTRATOR, CREATOR
from aiogram.types import ChatMemberUpdated

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT | -RESTRICTED) >> (+RESTRICTED | MEMBER | ADMINISTRATOR | CREATOR)))
async def var_1(event: ChatMemberUpdated):
    await event.answer(text='Бот добавлен в группу. Вариант хэндлера №1')


# Но разработчик aiogram пошёл дальше и обернул эти два набора в отдельные состояния IS_NOT_MEMBER и IS_MEMBER соответственно.
# Упростим наш код в виде варианта №2:
# Немного другие импорты
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def var_2(event: ChatMemberUpdated):
    await event.answer(text='Бот добавлен в группу. Вариант хэндлера №2')


# Но поскольку, повторюсь, такой переход довольно часто используется в ботах,
# то разработчик пошёл ещё дальше и обернул такой переход в виде переменной JOIN_TRANSITION, получив вариант №3:
# И ещё меньше импортов
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def var_3(event: ChatMemberUpdated):
    await event.answer(text='Бот добавлен в группу. Вариант хэндлера №3')












