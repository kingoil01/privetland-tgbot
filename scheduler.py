import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from db.queries import get_expired_greets, delete_pending_greet

GREET_EXPIRE_SECONDS = 24 * 60 * 60  # 24 часа


async def expire_pending_greets(bot: Bot):
    expire_before = int(time.time()) - GREET_EXPIRE_SECONDS
    rows = await get_expired_greets(expire_before)

    for chat_id, message_id in rows:
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=None
            )
        except Exception:
            pass  # Сообщение могло быть удалено

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="⌛ <i>Время ответа на привет истекло</i>",
            parse_mode="HTML",
            reply_markup=None
        )

        await delete_pending_greet(chat_id, message_id)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        expire_pending_greets,
        trigger="interval",
        minutes=30,
        kwargs={"bot": bot},
        id="expire_greets",
        replace_existing=True,
    )
    return scheduler