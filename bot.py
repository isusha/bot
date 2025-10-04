import logging
import subprocess
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот прогноза воздуха.\nНапиши /forecast <город> чтобы получить прогноз.")

@dp.message_handler(commands=["forecast"])
async def forecast(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Напиши так: /forecast <город>\nНапример: /forecast Алматы")
        return

    city = parts[1]
    # запускаем forecast.py с аргументом города
    subprocess.run(["python", "forecast.py", city])

    # Отправляем текст
    if os.path.exists("forecast.txt"):
        with open("forecast.txt", "r", encoding="utf-8") as f:
            text = f.read()
        await message.reply(text)

    # Отправляем картинку
    if os.path.exists("forecast.png"):
        with open("forecast.png", "rb") as photo:
            await message.reply_photo(photo, caption="Прогноз AQI на 24 часа")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
