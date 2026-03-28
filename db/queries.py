import aiosqlite
from db.database import DB_PATH


async def create_user_if_not_exists(chat_id: int, user_id: int, first_name: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_stats (chat_id, user_id, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET first_name = excluded.first_name
        """, (chat_id, user_id, first_name))
        await db.commit()


async def add_point(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_stats
            SET points = points + 1
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        await db.commit()


async def add_sent(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_stats
            SET sent = sent + 1
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id))
        await db.commit()


async def get_user_full(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT points, level, sent
            FROM user_stats
            WHERE chat_id = ? AND user_id = ?
        """, (chat_id, user_id)) as cursor:
            return await cursor.fetchone()


async def get_cooldown(chat_id: int, from_id: int, to_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT last_sent FROM privet_cooldowns
            WHERE chat_id = ? AND from_user_id = ? AND to_user_id = ?
        """, (chat_id, from_id, to_id)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def update_cooldown(chat_id: int, from_id: int, to_id: int, timestamp: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO privet_cooldowns
            (chat_id, from_user_id, to_user_id, last_sent)
            VALUES (?, ?, ?, ?)
        """, (chat_id, from_id, to_id, timestamp))
        await db.commit()


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