import time

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from handlers.greet_check import is_greeting
from db.queries import (
    create_user_if_not_exists,
    add_point,
    add_sent,
    get_cooldown,
    update_cooldown,
    create_pending_greet,
    get_pending_greet,
    mark_greet_answered
)

router = Router()

COOLDOWN_SECONDS = 2 * 60 * 60  # 2 часа


def answer_keyboard(from_user_id: int, to_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Ответить",
            callback_data=f"greet_reply:{from_user_id}:{to_user_id}"
        )
    ]])


async def _send_greet(
    message: Message,
    from_user_id: int,
    from_name: str,
    from_username: str,
    target_user_id: int,
    target_name: str,
    target_username: str,
    chat_id: int,
):
    now = int(time.time())

    last = await get_cooldown(chat_id, from_user_id)
    if last and now - last < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last)
        hours, seconds = divmod(remaining, 3600)
        minutes = seconds // 60
        time_str = f"{hours} ч. {minutes} мин." if hours else f"{minutes} мин."
        sent = await message.answer(
            f"Вы недавно уже отправляли привет 📌\nПодождите ещё {time_str} ⏳"
        )
        await asyncio.sleep(3)
        await sent.delete()
        return

    try:
        await create_user_if_not_exists(chat_id, from_user_id, from_name, from_username)
        await create_user_if_not_exists(chat_id, target_user_id, target_name, target_username)

        await add_point(chat_id, target_user_id)
        await add_sent(chat_id, from_user_id)
        await update_cooldown(chat_id, from_user_id, now)

        sent = await message.reply(
            f"<b>{from_name}</b> приветствует <b>{target_name}</b> 👋",
            parse_mode="HTML",
            reply_markup=answer_keyboard(from_user_id, target_user_id)
        )

        await create_pending_greet(chat_id, sent.message_id, from_user_id, target_user_id, now)

    except Exception:
        await message.answer("❌ Что-то пошло не так, попробуй позже")


@router.message(F.reply_to_message)
async def handle_reply_privet(message: Message, bot: Bot):

    if not is_greeting(message):
        return

    from_user = message.from_user
    target = message.reply_to_message.from_user

    if not from_user or not target:
        return

    if target.is_bot:
        await message.answer("❗Нельзя передавать привет боту 🤖")
        return

    if target.id == from_user.id:
        await message.answer("❗Нельзя передавать привет самому себе 😐")
        return

    await _send_greet(
        message=message,
        from_user_id=from_user.id,
        from_name=from_user.first_name,
        from_username=from_user.username or "",
        target_user_id=target.id,
        target_name=target.first_name,
        target_username=target.username or "",
        chat_id=message.chat.id,
    )


@router.callback_query(F.data.startswith("greet_reply:"))
async def handle_greet_reply(callback: CallbackQuery, bot: Bot):
    _, from_user_id_str, to_user_id_str = callback.data.split(":")
    from_user_id = int(from_user_id_str)
    to_user_id = int(to_user_id_str)

    presser = callback.from_user
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if presser.id != to_user_id:
        await callback.answer()
        return

    row = await get_pending_greet(chat_id, message_id)
    if not row or row[3]:  # не найден или уже отвечен
        await callback.answer()
        return

    await mark_greet_answered(chat_id, message_id)

    try:
        from_member = await bot.get_chat_member(chat_id, from_user_id)
        from_name = from_member.user.first_name
    except Exception:
        from_name = "пользователю"

    await add_sent(chat_id, to_user_id)
    await add_point(chat_id, from_user_id)

    await callback.message.edit_text(
        f"<b>{from_name}</b> приветствует <b>{presser.first_name}</b> 👋"
        f"\n✅ <b>{presser.first_name}</b> ответил на привет!",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()
