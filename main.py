import asyncio
import threading
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router
from web_server import start_web

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=start_web, daemon=True)
    web_thread.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())