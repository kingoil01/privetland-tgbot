import asyncio
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.queries import get_cooldown
from handlers.privet import COOLDOWN_SECONDS

router = Router()


@router.message(Command("cooldown"))
async def handle_cooldown(message: Message):
    from_user = message.from_user
    if not from_user:
        return

    chat_id = message.chat.id
    now = int(time.time())

    last = await get_cooldown(chat_id, from_user.id)
    if last and now - last < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last)
        hours, seconds = divmod(remaining, 3600)
        minutes = seconds // 60
        time_str = f"{hours} ч. {minutes} мин." if hours else f"{minutes} мин."
        await message.answer(f"До отправки следующего привета осталось {time_str} ⏳")
    else:
        await message.answer("Вы можете отправить привет прямо сейчас! ✅")