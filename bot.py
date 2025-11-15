import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI

TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not TG_TOKEN or not OPENAI_KEY:
    raise ValueError("TG_TOKEN и OPENAI_KEY должны быть установлены!")

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = OpenAI(api_key=OPENAI_KEY)

user_histories = {}

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
    if message.from_user is None:
        return

    user_id = message.from_user.id
    user_text = message.text or ""

    history = user_histories.get(user_id, [])
    history.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=history
        )
        answer = str(response.choices[0].message.content)
    except Exception as e:
        answer = f"Ошибка OpenAI API: {e}"

    history.append({"role": "assistant", "content": answer})
    user_histories[user_id] = history[-50:]

    await message.reply(text=answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
