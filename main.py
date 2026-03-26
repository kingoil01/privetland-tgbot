import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, privet, stats
from db.database import init_db

async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(stats.router)
    dp.include_router(privet.router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    handler = RotatingFileHandler(
        "bot.log",
        maxBytes=1_000_000,  # 1 MB
        backupCount=3
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    asyncio.run(main())