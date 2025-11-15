import os
import asyncio
from typing import Dict, List
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI

# Переменные окружения
TG_TOKEN = os.environ.get("TG_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_KEY")

if not TG_TOKEN or not OPENAI_KEY:
    raise ValueError("TG_TOKEN и OPENAI_KEY должны быть установлены!")

# Telegram
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# OpenAI
client = OpenAI(api_key=OPENAI_KEY)

# История пользователя
user_histories: Dict[int, List[Dict[str, str]]] = {}

@dp.message(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "Привет! Я ChatGPT-бот. Пиши сообщение, а я отвечу.\n/reset — сбросить историю."
    )

@dp.message(commands=["reset"])
async def reset(message: types.Message):
    if message.from_user is None:
        return
    user_id = message.from_user.id
    user_histories[user_id] = []
    await message.reply("История чата сброшена.")

@dp.message()
async def handle_message(message: types.Message):
    if message.from_user is None or not message.text:
        return

    user_id = message.from_user.id
    user_text = message.text

    # Получаем историю пользователя или создаем новую
    history = user_histories.get(user_id, [])
    history.append({"role": "user", "content": user_text})

    try:
        # type: ignore → игнорируем предупреждение Pylance
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history  # type: ignore
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Ошибка OpenAI API: {e}"

    answer_text = str(answer or "Пустой ответ")
    history.append({"role": "assistant", "content": answer_text})
    user_histories[user_id] = history[-50:]

    await message.reply(answer_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
