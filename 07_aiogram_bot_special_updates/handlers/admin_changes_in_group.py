# Актуализация списка админов в группах
# Частая проблема ботов-модераторов: как на вызываемые команды наложить проверку прав доступа.
# К примеру, как сделать так, чтобы банить участников по команде /ban могли только администраторы группы.
#
# Первая и наивная мысль — каждый раз вызывать getChatMember, чтобы определить статус вызывающего юзера в группе.
# Вторая мысль — закэшировать это знание на короткое время.
# Третья и более правильная идея — при старте бота получить список админов, а дальше слушать апдейты chat_member об изменении их состава и редактировать список самостоятельно. Бот перезапустился? Не беда, снова получили актуальный список и работаем с ним.
#
# Напишем роутер, в котором будем следить за изменением состава админов и обновлять переданный извне список (точнее, в терминах python это будет множество, оно же Set):

from aiogram import F, Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, LEFT, RESTRICTED, MEMBER, ADMINISTRATOR, CREATOR
from aiogram.types import ChatMemberUpdated

# from config_reader import config

router = Router()
# router.chat_member.filter(F.chat.id == config.main_chat_id)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) >> (ADMINISTRATOR | CREATOR)))
async def admin_promoted(event: ChatMemberUpdated, admins: set[int]):
    admins.add(event.new_chat_member.user.id)
    await event.answer(f"{event.new_chat_member.user.first_name} был(а) повышен(а) до Администратора!")


# Обратите внимание на направление стрелок. Или можно было поменять местами объекты в скобках
@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) << (ADMINISTRATOR | CREATOR)))
async def admin_demoted(event: ChatMemberUpdated, admins: set[int]):
    admins.discard(event.new_chat_member.user.id)
    await event.answer(f"{event.new_chat_member.user.first_name} был(а) понижен(а) до обычного юзера!")



