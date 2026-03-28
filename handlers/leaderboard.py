from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db.queries import get_leaderboard
from aiogram.filters import Command

router = Router()

def build_keyboard(current: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="[📬 Получено]" if current == "points" else "📬 Получено",
            callback_data="lb:points"
        ),
        InlineKeyboardButton(
            text="[📣 Отправлено]" if current == "sent" else "📣 Отправлено",
            callback_data="lb:sent"
        ),
    ]])

def build_text(rows: list, mode: str) -> str:
    title = "🏆 Топ по <b>полученным</b> приветам 🏆" if mode == "points" else "🏆 Топ по <b>отправленным</b> приветам 🏆"

    if not rows:
        return f"{title}\n\nТаблица лидеров пуста ❗"

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, row in enumerate(rows):
        name, value = row
        prefix = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{prefix} {name} — {value}")

    return f"{title}\n\n" + "\n".join(lines)


@router.message(Command("leaderboard"))
async def leaderboard_handler(message: Message):
    rows = await get_leaderboard(message.chat.id, "points")
    await message.answer(
        build_text(rows, "points"),
        parse_mode="HTML",
        reply_markup=build_keyboard("points")
    )


@router.callback_query(F.data.startswith("lb:"))
async def leaderboard_callback(callback: CallbackQuery):
    mode = callback.data.split(":")[1]  # "points" или "sent"
    rows = await get_leaderboard(callback.message.chat.id, mode)
    text = build_text(rows, mode)

    # Не редактируем если текст не изменился (например, двойной тап)
    if callback.message.text == text:
        await callback.answer()
        return

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=build_keyboard(mode)
    )
    await callback.answer()