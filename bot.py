import logging
import subprocess
from aiogram import Bot, Dispatcher, types, executor
import os

API_TOKEN = os.getenv(8296435065:AAFCDjuerTbm8P6xRJd6-RD63H_Gzc29FQA)  # токен из Railway Variables

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот прогноза воздуха.\nНапиши /forecast чтобы получить прогноз.")


@dp.message_handler(commands=["forecast"])
async def forecast(message: types.Message):
    # Запускаем скрипт прогноза
    subprocess.run(["python", "forecast.py"])

    # Отправляем картинку прогноза
    with open("forecast.png", "rb") as photo:
        await message.reply_photo(photo, caption="Прогноз качества воздуха на 24 часа")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
