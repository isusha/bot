import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import get_forecast  # импортируем нашу функцию

API_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот прогноза воздуха.\nНапиши /forecast <город> чтобы получить AQI в реальном времени.")

@dp.message_handler(commands=["forecast"])
async def forecast_cmd(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Напиши так: /forecast <город>\nНапример: /forecast Almaty")
        return

    city = parts[1]
    text, image_path = get_forecast(city)

    if image_path:
        with open(image_path, "rb") as photo:
            await message.reply_photo(photo, caption=text)
    else:
        await message.reply(text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
