# Фильтры как классы
# В отличие от aiogram 2.x, в «тройке» больше нет фильтра-класса ChatTypeFilter на конкретный тип чата (личка, группа, супергруппа или канал).
# Напишем его самостоятельно. Пусть у юзера будет возможность указать нужный тип либо строкой, либо списком (list).
# Последнее может пригодиться, когда нас интересуют одновременно несколько типов, например, группы и супергруппы.

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

# Вообще говоря, такой фильтр на тип чата можно сделать чуть иначе.
# Несмотря на то, что типов чатов у нас четыре (ЛС, группа, супергруппа, канал),
# апдейт типа message не может прилетать из каналов, т.к. у них свой апдейт channel_post.
# А когда мы фильтруем группы, обычно всё равно, обычная группа или супергруппа, лишь бы не личка.
# Таким образом, сам фильтр можно свести к условному ChatTypeFilter(is_group=True/False) и просто проверять, ЛС или не ЛС.

# фильтры наследуются от базового класса BaseFilter
class ChatTypeFilter(BaseFilter):  # [1]
    # В конструкторе класса можно задать будущие аргументы фильтра.
    # В данном случае мы заявляем о наличии одного аргумента chat_type, который может быть как строкой (str), так и списком (list)
    def __init__(self, chat_type: Union[str, list]): # [2]
        self.chat_type = chat_type

    # метод __call__() срабатывает, когда экземпляр класса ChatTypeFilter() вызывают как функцию
    async def __call__(self, message: Message) -> bool:  # [3]
        # Проверяем тип переданного объекта и вызываем соответствующую проверку.
        # Мы стремимся к тому, чтобы фильтр вернул булево значение, поскольку далее выполнится только тот хэндлер, все фильтры которого вернули True.
        # print(message.text, message.chat.type, self.chat_type)
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type