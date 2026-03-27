from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я помогаю передавать твои приветы 👋\n"
        "Отправь 'Привет' ответом на сообщение другого человека 💌"
    )