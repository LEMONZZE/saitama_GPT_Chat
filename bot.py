import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
import openai

# Токены из переменных окружения Railway
TG_TOKEN = os.environ.get("TG_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_KEY")

if not TG_TOKEN or not OPENAI_KEY:
    raise ValueError(
        "TG_TOKEN и OPENAI_KEY должны быть установлены в переменных окружения Railway!"
    )

# Инициализация Telegram бота
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Инициализация OpenAI
openai.api_key = OPENAI_KEY

# Хранилище истории чата
user_histories = {}

@dp.message(commands=["start"])
async def start(message: types.Message):
    await message.reply("Привет! Я ChatGPT-бот. Пиши сообщение, а я отвечу.\n/reset — сбросить историю.")

@dp.message(commands=["reset"])
async def reset(message: types.Message):
    if message.from_user is None:
        return
    user_id = message.from_user.id
    user_histories[user_id] = []
    await message.reply("История чата сброшена.")

@dp.message()
async def handle_message(message: types.Message):
    if message.from_user is None:
        return

    user_id = message.from_user.id
    user_text = message.text or ""

    # Получаем историю или создаём новую
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "content": user_text})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        answer = str(response.choices[0].message["content"])
    except Exception as e:
        answer = f"Ошибка OpenAI API: {e}"

    history.append({"role": "assistant", "content": answer})
    user_histories[user_id] = history[-50:]

    await message.reply(text=answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
