import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from handlers.rar_handler import router as rar_router

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    dp.include_router(rar_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
