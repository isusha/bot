import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import get_aqi   # импортируем функцию из forecast.py

API_TOKEN = os.getenv("BOT_TOKEN")  # токен бота из Railway Variables

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот прогноза воздуха 🌍\n"
        "Напиши /forecast <город>, чтобы узнать качество воздуха.\n"
        "Например: /forecast London"
    )


@dp.message_handler(commands=["forecast"])
async def forecast_cmd(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Напиши так: /forecast <город>\nНапример: /forecast Алматы")
        return

    city = parts[1]
    text = get_aqi(city)   # вызываем функцию, которая идёт в OpenAQ
    await message.reply(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
