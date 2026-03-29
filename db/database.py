import aiosqlite

DB_PATH = "data/bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                chat_id INTEGER,
                user_id INTEGER,
                first_name TEXT DEFAULT '',
                username TEXT DEFAULT '',
                points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                sent INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """)

        # Кулдаун теперь глобальный на отправителя, to_user_id убран
        await db.execute("""
            CREATE TABLE IF NOT EXISTS privet_cooldowns (
                chat_id INTEGER,
                from_user_id INTEGER,
                last_sent INTEGER,
                PRIMARY KEY (chat_id, from_user_id)
            )
        """)

        # Ожидающие ответа приветы
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pending_greets (
                chat_id INTEGER,
                message_id INTEGER,
                from_user_id INTEGER,
                to_user_id INTEGER,
                created_at INTEGER,
                is_answered INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, message_id)
            )
        """)

        await db.commit()
