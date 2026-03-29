import aiosqlite
from db.database import DB_PATH


async def create_user_if_not_exists(chat_id: int, user_id: int, first_name: str = "", username: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_stats (chat_id, user_id, first_name, username)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                first_name = excluded.first_name,
                username = excluded.username
        """, (chat_id, user_id, first_name, username or ""))
        await db.commit()


async def get_user_full(chat_id: int, user_id: int) -> tuple | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT points, level, sent FROM user_stats
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        return await cursor.fetchone()


async def add_point(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_stats SET points = points + 1
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        await db.commit()


async def add_sent(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_stats SET sent = sent + 1
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        await db.commit()


# Кулдаун (глобальный на отправителя)
async def get_cooldown(chat_id: int, from_user_id: int) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT last_sent FROM privet_cooldowns
            WHERE chat_id = ? AND from_user_id = ?
        """, (chat_id, from_user_id))
        row = await cursor.fetchone()
        return row[0] if row else None


async def update_cooldown(chat_id: int, from_user_id: int, now: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO privet_cooldowns (chat_id, from_user_id, last_sent)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, from_user_id) DO UPDATE SET last_sent = excluded.last_sent
        """, (chat_id, from_user_id, now))
        await db.commit()


# Pending greets
async def create_pending_greet(chat_id: int, message_id: int, from_user_id: int, to_user_id: int, created_at: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO pending_greets (chat_id, message_id, from_user_id, to_user_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, message_id, from_user_id, to_user_id, created_at))
        await db.commit()


async def get_pending_greet(chat_id: int, message_id: int) -> tuple | None:
    """Возвращает (from_user_id, to_user_id, created_at, is_answered)"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT from_user_id, to_user_id, created_at, is_answered
            FROM pending_greets
            WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id))
        return await cursor.fetchone()


async def mark_greet_answered(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE pending_greets SET is_answered = 1
            WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id))
        await db.commit()


async def get_expired_greets(expire_before: int) -> list[tuple]:
    """Возвращает список (chat_id, message_id) истёкших и неотвеченных приветов"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT chat_id, message_id FROM pending_greets
            WHERE is_answered = 0 AND created_at < ?
        """, (expire_before,))
        return await cursor.fetchall()


async def delete_pending_greet(chat_id: int, message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM pending_greets
            WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id))
        await db.commit()


# Лидерборд
async def get_leaderboard(chat_id: int, mode: str, limit: int = 10) -> list:
    field = "points" if mode == "points" else "sent"
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(f"""
            SELECT first_name, {field}
            FROM user_stats
            WHERE chat_id = ?
            ORDER BY {field} DESC
            LIMIT ?
        """, (chat_id, limit))
        return await cursor.fetchall()
