import time
import logging

from aiogram import Router, F
from aiogram.types import Message

from db.queries import (
    create_user_if_not_exists,
    add_point,
    add_sent,
    get_cooldown,
    update_cooldown
)

router = Router()
logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 600  # 10 минут


@router.message(F.text & (F.text.lower() == "привет"))
async def handle_reply_privet(message: Message):
    if not message.reply_to_message:
        return

    from_user = message.from_user
    target = message.reply_to_message.from_user

    if not from_user or not target:
        return

    if target.id == from_user.id:
        await message.answer("Нельзя отправлять привет самому себе")
        return

    chat_id = message.chat.id
    now = int(time.time())

    try:
        # проверка кулдауна
        last = await get_cooldown(chat_id, from_user.id, target.id)

        if last and now - last < COOLDOWN_SECONDS:
            remaining = COOLDOWN_SECONDS - (now - last)
            await message.answer(f"Вы уже передавали привет {target.first_name}.\nПодожди {remaining} сек ⏳")
            return

        # создаём пользователей
        await create_user_if_not_exists(chat_id, from_user.id)
        await create_user_if_not_exists(chat_id, target.id)

        # начисляем
        await add_point(chat_id, target.id)
        await add_sent(chat_id, from_user.id)

        # обновляем кулдаун
        await update_cooldown(chat_id, from_user.id, target.id, now)

        from_name = from_user.first_name
        target_name = target.first_name

        await message.answer(
            f"{from_name} передал привет {target_name} (+1)"
        )

    except Exception:
        logger.exception("Error in creating user or adding point")
        await message.answer("Произошла ошибка")