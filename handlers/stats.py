from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from db.queries import create_user_if_not_exists, get_user_full

router = Router()


@router.message(Command("stats"))
async def stats_handler(message: Message):
    chat_id = message.chat.id
    user = message.from_user

    if not user:
        return

    try:
        await create_user_if_not_exists(chat_id, user.id)
        data = await get_user_full(chat_id, user.id)

        if not data:
            await message.answer("❌ Что-то пошло не так, попробуй позже")
            return

        points, level, sent = data
        name = user.first_name

        await message.answer(
            f"📊 Статистика <b>{name}</b>:\n\n"
            f"📣 Отправлено: {sent}\n"
            f"📬 Получено: {points}\n",
            parse_mode="HTML"
        )

    except Exception:
        await message.answer("❌ Что-то пошло не так, попробуй позже")
