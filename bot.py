import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import aqi_message

# Токен бота в переменной окружения BOT_TOKEN
API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("Не задан BOT_TOKEN!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот качества воздуха 🌍\n"
        "Напиши /aqi <город> и я покажу актуальные данные.\n"
        "Пример: /aqi Almaty"
    )

@dp.message_handler(commands=["aqi"])
async def aqi_handler(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❗ Напиши так: /aqi <город>\nПример: /aqi Almaty")
        return

    city = parts[1]
    result = aqi_message(city)
    await message.reply(result)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
