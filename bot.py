import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Инициализация бота и Dispatcher с MemoryStorage
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# OpenAI клиент
client = OpenAI(api_key=OPENAI_KEY)

# Хранилище истории для каждого пользователя
user_histories = {}

@dp.message()
async def handle_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_text = message.text

    # Получаем историю пользователя, если нет — создаём
    history = user_histories.get(user_id, [])

    # Добавляем сообщение пользователя в историю
    history.append({"role": "user", "content": user_text})

    # Отправляем запрос в ChatGPT
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=history
    )

    # Получаем ответ
    answer = response.choices[0].message.content

    # Добавляем ответ ChatGPT в историю
    history.append({"role": "assistant", "content": answer})

    # Сохраняем историю
    user_histories[user_id] = history[-20:]  # храним последние 20 сообщений

    await message.reply(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
