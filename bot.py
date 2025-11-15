import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

# Берём токен Telegram из переменных окружения Railway
TG_TOKEN = os.environ.get("TG_TOKEN")

if not TG_TOKEN:
    raise ValueError("TG_TOKEN должен быть установлен в переменных окружения!")

# Инициализация бота и диспетчера
bot = Bot(token=TG_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Ответ на сообщение "привет"
@dp.message()
async def echo(message: types.Message):
    if message.text == "привет":
        await message.reply("Привет!")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
