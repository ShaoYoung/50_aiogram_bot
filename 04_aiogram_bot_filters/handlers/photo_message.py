from aiogram import Router, F
from aiogram.types import Message, PhotoSize, Chat


router = Router()

# Более того, даже проверку на контент-тайпы можно представить в виде магического фильтра:
# F.content_type.in_({'text', 'sticker', 'photo'}) или F.photo | F.text | F.sticker
router.message.filter(F.chat.type.in_({"group", "supergroup", "private"}))
router.message.filter(F.photo | F.text | F.sticker)


# Вместо старого варианта ContentTypesFilter(content_types="photo") новый F.photo.
# Здесь F - это message
# @router.message(F.photo)
# async def photo_msg(message: Message):
#     await message.answer("Это точно какое-то изображение!")


# Посмотрим на ту самую «эксклюзивную» фичу magic-filter в составе aiogram 3.x.
# Речь про метод as_(<some text>), позволяющий получить результат фильтра в качестве аргумента хэндлера.
# Короткий пример, чтобы стало понятно: у сообщений с фото эти изображения прилетают массивом, который обычно отсортирован в порядке увеличения качества.
# Соответственно, можно сразу в хэндлер получить объект фотки с максимальным размером:
@router.message(F.photo[-1].as_("largest_photo"))
async def forward_from_channel_handler(message: Message, largest_photo: PhotoSize) -> None:
    print(f'{largest_photo.width=}, {largest_photo.height=}')
    await message.answer("Это точно какое-то изображение!")



# Здесь F - это message
@router.message(F.text)
async def photo_msg(message: Message):
    await message.answer("Это текстовое сообщение!")


# Пример посложнее.
# Если сообщение переслано от анонимных администраторов группы или из какого-либо канала, то в объекте Message будет
# непустым поле forward_from_chat с объектом типа Chat внутри.
# Вот как будет выглядеть пример, который сработает только если поле forward_from_chat непустое,
# а в объекте Chat поле type будет равно channel (другими словами, отсекаем форварды от анонимных админов, реагируя только на форварды из каналов):
@router.message(F.forward_from_chat[F.type == "channel"].as_("channel"))
async def forwarded_from_channel(message: Message, channel: Chat):
    await message.answer(f"This channel's ID is {channel.id}")






