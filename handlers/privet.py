import time
import logging

from aiogram import Router
from aiogram.types import Message
from handlers.greet_check import is_greeting

from db.queries import (
    create_user_if_not_exists,
    add_point,
    add_sent,
    get_cooldown,
    update_cooldown
)

router = Router()
logger = logging.getLogger(__name__)

# Время перерыва для отправки привета
COOLDOWN_SECONDS = 120


@router.message()
async def handle_reply_privet(message: Message):
    if not message.reply_to_message:
        return

    if not is_greeting(message):
        return

    from_user = message.frogitm_user
    target = message.reply_to_message.from_user

    if not from_user or not target:
        return

    if target.id == from_user.id:
        await message.answer("Нельзя отправлять привет самому себе ❗️")
        return

    chat_id = message.chat.id
    now = int(time.time())

    last = await get_cooldown(chat_id, from_user.id, target.id)
    if last and now - last < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last)
        await message.answer(
            f"Вы недавно передавали привет {target.first_name} 📌.\n"
            f"Подождите {remaining} сек ⏳"
        )
        return

    try:
        await create_user_if_not_exists(chat_id, from_user.id)
        await create_user_if_not_exists(chat_id, target.id)

        await add_point(chat_id, target.id)
        await add_sent(chat_id, from_user.id)

        await update_cooldown(chat_id, from_user.id, target.id, now)

        await message.reply(
            f"<b>{from_user.first_name}</b> приветствует <b>{target.first_name}</b> 👋", parse_mode="HTML"
        )

    except Exception:
        logger.exception("Error in creating user or adding point")
        await message.answer("❌ Что-то пошло не так, попробуй позже")