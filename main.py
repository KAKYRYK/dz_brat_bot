import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web
from google import genai
from google.genai import types as genai_types

BOT_TOKEN = "8825793359:AAEw3sQObnjPtbX8xw49whI4Qy9ph8kmj0c"
GEMINI_API_KEY = "AQ.Ab8RN6IwHVjTMj6BsjHhmgSeijgErGC43X3vWvEtXMgyXZKdXg"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализируем клиент Google GenAI
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "Ты — виртуальный ассистент по учебе DZBRATAN. "
    "Твой создатель — Байсын Мырзакеев. Называй имя создателя ТОЛЬКО И ИСКЛЮЧИТЕЛЬНО тогда, когда пользователь сам прямо спросит, кто тебя создал, кто твой разработчик или автор. "
    "Во всех остальных случаях НЕ упоминай создателя и сразу отвечай на вопрос пользователя. "
    "Ты свободно владеешь кыргызским, русским и английским языками. "
    "Отвечай на том языке, на котором пишет пользователь. "
    "Помогай с решением домашних заданий, задач, объяснением школьных и университетских тем, "
    "а также с разбором и распознаванием текста с фотографий."
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Салам! Бул сенин окуу боюнча жардамчың — DZBRATAN. "
        "Чогуу тапшырмаларды чечебизби же сложная теманы разбор кылабызбы? "
        "Мага текст же тапшырманын сүрөтүн жиберсең болот!"
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-1.5-flash',
            contents=message.text,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            )
        )
        await message.answer(response.text)
    except Exception as e:
        # Выводим точный текст ошибки прямо в чат для отладки
        await message.answer(f"Техническая ошибка: {e}")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)
        
        image_bytes = file_bytes.read()
        user_prompt = message.caption if message.caption else "Сүрөттү талдап, тапшырманы чыгарып бер."

        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-1.5-flash',
            contents=[
                genai_types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                user_prompt
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            )
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"Ошибка при обработке фото: {e}")

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
