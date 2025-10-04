import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import get_forecast  # импортируем функцию

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот прогноза воздуха 🌍\n"
        "Напиши /forecast <город>, например: /forecast Алматы"
    )


@dp.message_handler(commands=["forecast"])
async def forecast_cmd(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Напиши так: /forecast <город>\nНапример: /forecast Алматы")
        return

    city = parts[1]
    await message.reply(f"Запрашиваю прогноз для {city}...")

    text, image_path = get_forecast(city)

    await message.reply(text)

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as photo:
            await message.reply_photo(photo, caption="Прогноз AQI на 24 часа")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
