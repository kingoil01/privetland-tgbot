import aiosqlite

DB_PATH = "data/bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # таблица статистики пользователей в чатах
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                chat_id INTEGER,
                user_id INTEGER,
                first_name TEXT DEFAULT '',
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                sent INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """)

        # таблица кулдаунов (кто кому отправлял привет)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS privet_cooldowns (
                chat_id INTEGER,
                from_user_id INTEGER,
                to_user_id INTEGER,
                last_sent INTEGER,
                PRIMARY KEY (chat_id, from_user_id, to_user_id)
            )
        """)

        await db.commit()