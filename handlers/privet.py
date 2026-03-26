import time
import logging

from aiogram import Router
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

# Время перерыва для отправки привета
COOLDOWN_SECONDS = 600

# Список разрешённых наборов стикеров
ALLOWED_STICKER_SETS = ("Privet4956")

# Список разрешённых конкретных стикеров (по file_unique_id)
ALLOWED_STICKERS = ()


@router.message()
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

    is_text_privet = bool(message.text and message.text.lower() == "привет")
    is_sticker_privet = False
    if message.sticker:
        if message.sticker.set_name in ALLOWED_STICKER_SETS:
            is_sticker_privet = True
        elif message.sticker.file_unique_id in ALLOWED_STICKERS:
            is_sticker_privet = True

    if not (is_text_privet or is_sticker_privet):
        return

    chat_id = message.chat.id
    now = int(time.time())

    last = await get_cooldown(chat_id, from_user.id, target.id)
    if last and now - last < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last)
        await message.answer(f"Вы уже передавали привет {target.first_name}.\nПодожди {remaining} сек ⏳")
        return

    try:
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