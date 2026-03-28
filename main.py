import asyncio

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, privet, stats, leaderboard
from db.database import init_db

async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(stats.router)
    dp.include_router(leaderboard.router)
    dp.include_router(privet.router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())