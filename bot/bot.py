import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers_sender import sender_router
from bot.handlers_parse import parse_router
from bot.start_hanlder import start_router
from bot.profile_handler import profile_router

import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def main():
    bot_token = os.getenv('BOT_TOKEN')
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(profile_router)
    dp.include_router(start_router)
    dp.include_router(sender_router)
    dp.include_router(parse_router)
   

    await dp.start_polling(bot)  # bot здесь!

if __name__ == "__main__":
    asyncio.run(main())
