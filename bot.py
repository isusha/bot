import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from forecast import get_air_quality

# токен телеграм-бота
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот качества воздуха 🌍\n"
        "Напиши /aqi <город> и я покажу актуальные данные.\n"
        "Например: /aqi London"
    )


@dp.message_handler(commands=["aqi"])
async def aqi_handler(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❗ Напиши так: /aqi <город>\nПример: /aqi Almaty")
        return

    city = parts[1]
    result = get_air_quality(city)

    await message.reply(result)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
