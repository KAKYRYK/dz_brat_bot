import asyncio
import os
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web
from openai import AsyncOpenAI

# Конфигурация
BOT_TOKEN = "8825793359:AAEw3sQObnjPtbX8xw49whI4Qy9ph8kmj0c"
OPENAI_API_KEY = "ВАШ_OPENAI_API_KEY"  # Укажите ваш ключ OpenAI

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Инструкция для ИИ
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

# Обработка текстовых сообщений
@dp.message(F.text)
async def handle_text(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            timeout=60.0
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        await message.answer("Ката кетти же жооп өтө узак иштетилди. Кайра аракет кылып көрүңүз.")

# Обработка фотографий и изображений
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file_info.file_path)
        
        base64_image = base64.b64encode(file_bytes.read()).decode('utf-8')
        user_prompt = message.caption if message.caption else "Сүрөттү талдап, тапшырманы чыгарып бер."

        response = await ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            timeout=60.0
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
    except Exception as e:
        await message.answer("Сүрөттү иштетүүдө ката кетти. Сураныч, кайра жиберип көрүңүз.")

# Заглушка веб-сервера для Render
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

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
