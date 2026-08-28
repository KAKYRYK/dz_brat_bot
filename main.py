import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiohttp import web

# Токен бота
BOT_TOKEN = "8825793359:AAEO2mPBbgCm07DGTVcSN1r7qEvLc0EGocA"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я работаю 24/7!")

# Фиктивный веб-сервер для прохождения проверки портов на Render
async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def main():
    # Поднятие минимального HTTP-сервера для Render
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Запуск поллинга Telegram
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
