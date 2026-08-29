import asyncio
import os
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web
from groq import Groq

BOT_TOKEN = "8825793359:AAEhdeIINNpnfNTf2wspSYyFzMrbsjxbFXk"
GROQ_API_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = Groq(api_key=GROQ_API_KEY)
# Обновили модель на актуальную с поддержкой зрения
MODEL_NAME = "qwen/qwen3.6-27b"

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
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)
        
        image_bytes = file_bytes.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{base64_image}"
        
        user_prompt = message.caption if message.caption else "Сүрөттү талдап, тапшырманы чыгарып бер."

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0.3,
        )
        await message.answer(response.choices[0].message.content)
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
