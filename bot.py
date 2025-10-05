import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import get_air_quality

API_TOKEN = os.getenv("BOT_TOKEN")   # Токен бота
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("👋 Привет! Я бот качества воздуха.\nНапиши /forecast <город>\nНапример: /forecast London")

@dp.message_handler(commands=["forecast"])
async def forecast_cmd(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠️ Напиши так: /forecast <город>\nНапример: /forecast London")
        return

    city = parts[1]
    text = get_air_quality(city)
    await message.reply(text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
