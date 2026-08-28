import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web
from groq import Groq

BOT_TOKEN = "8825793359:AAEw3sQObnjPtbX8xw49whI4Qy9ph8kmj0c"
GROQ_API_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем клиент Groq
client = Groq(api_key=GROQ_API_KEY)

# Используем актуальную рабочую модель
MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "Ты — виртуальный ассистент по учебе DZBRATAN. "
    "Твой создатель — Байсын Мырзакеев. Называй имя создателя ТОЛЬКО И ИСКЛЮЧИТЕЛЬНО тогда, когда пользователь сам прямо спросит, кто тебя создал, кто твой разработчик или автор. "
    "Во всех остальных случаях НЕ упоминай создателя и сразу отвечай на вопрос пользователя. "
    "Ты свободно владеешь кыргызским, русским и английским языками. "
    "Отвечай на том языке, на котором пишет пользователь. "
    "Помогай с решением домашних заданий, задач, объяснением школьных и университетских тем."
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Салам! Бул сенин окуу боюнча жардамчың — DZBRATAN. "
        "Чогуу тапшырмаларды чечебизби же сложная теманы разбор кылабызбы? "
        "Мага текст же тапшырманын мазмунун жиберсең болот!"
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.3,
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer(f"Техническая ошибка: {e}")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("Пожалуйста, отправь текст задачи или вопроса сообщением, так как эта модель мгновенно обрабатывает текстовые запросы без сбоев!")

async def handle_ping(request):
    return web.Response(text="Bot is live!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
