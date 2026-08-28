import asyncio
import io
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from openai import OpenAI
from PIL import Image

# Ваши токены
TELEGRAM_TOKEN = "8825793359:AAEkcmnUsetUPBq2qHzkNcU0u3dr1bePG7I"
OPENROUTER_API_KEY = "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"

# Инициализация клиента OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Маршрутизатор, автоматически подбирающий рабочие бесплатные модели
MODEL_NAME = "openrouter/free"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Системный промт
SYSTEM_PROMPT = (
    "Ты — «ДЗ Брат», умный, прошаренный и одушевленный ИИ-помощник по учебе, который отлично разбирается в школьной и университетской программе, задачах и мемах. "
    "Твой стиль: обращайся к пользователю уважительно и на 'Вы', будь вежливым, поддерживающим, используй уместный юмор и объясняй сложные темы доступно и понятно. "
    "Языки: Ты свободно владеешь русским, кыргызским и английским языками (English). Если вам пишут на кыргызском или английском — отвечайте на соответствующем языке. "
    "При общении на русском можете добавлять легкий местный колорит (Салам, Рахмат и т.д.).\n"
    "Правила относительно создателя:\n"
    "Твой создатель — **Байсын Мырзакеев**.\n"
    "Называй имя своего создателя (Байсын Мырзакеев) ТОЛЬКО тогда, когда пользователь напрямую спросит 'Кто тебя создал?', 'Кто твой создатель?' или аналогичный вопрос об авторе.\n"
    "Во всех остальных случаях не упоминай создателя и сразу отвечай на вопрос по существу."
)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Салам! Я ваш ДЗ Брат 🤙\n\n"
        "Отправляйте любой вопрос, формулу, текст или фото задачи на русском, кыргызском или английском языке — во всём разберемся!"
    )

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, action="typing")
        
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        
        img_bytes = downloaded_file.read()
        base64_image = encode_image(img_bytes)
        caption = message.caption if message.caption else "Посмотри на изображение, объясни что там и помоги решить."

        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": caption},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer("Произошла ошибка при обработке фото. Попробуйте еще раз.")
        print(f"Ошибка: {e}")

@dp.message(F.text)
async def handle_text(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, action="typing")
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer("Произошла ошибка при обработке запроса. Попробуйте еще раз.")
        print(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())