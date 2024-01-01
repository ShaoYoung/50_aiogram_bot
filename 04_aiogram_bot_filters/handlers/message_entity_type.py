from aiogram import Router, F
from aiogram.types import Message, PhotoSize, Chat
from aiogram.enums import MessageEntityType

router = Router()


# Ещё более сложный пример. При помощи magic-filter можно проверить элементы списка на соответствие какому-нибудь признаку:
@router.message(F.entities[:].type == MessageEntityType.EMAIL)
async def all_emails(message: Message):
    await message.answer("All entities are emails")


@router.message(F.entities[...].type == MessageEntityType.EMAIL)
async def any_emails(message: Message):
    await message.answer("At least one email!")


@router.message(F.entities[...].type == MessageEntityType.PHONE_NUMBER)
async def phone_number(message: Message):
    # for item in message.entities:
    #     print(item.type)
    found_phone_numbers = [item.extract_from(message.text) for item in message.entities if item.type == "phone_number"]
    await message.answer(f'Founded phone numbers: {", ".join(found_phone_numbers)}!')

