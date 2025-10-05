import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from forecast import aqi_message, get_coordinates, get_air_pollution, estimate_health_risk

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# FSM for /healthrisk
class HealthRiskForm(StatesGroup):
    city = State()
    hours = State()

# Start command
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Hi! I am your Air Quality Bot 🌍\n"
        "Commands:\n"
        "/aqi <city> — get air quality info\n"
        "/healthrisk — estimate health risk based on AQI and time outdoors"
    )

# AQI command
@dp.message_handler(commands=["aqi"])
async def aqi_handler(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❗ Please write: /aqi <city>\nExample: /aqi London")
        return
    city = parts[1]
    result = aqi_message(city)
    await message.reply(result)

# Health risk command
@dp.message_handler(commands=["healthrisk"])
async def healthrisk_start(message: types.Message):
    await message.reply("Enter the city you were in:")
    await HealthRiskForm.city.set()

@dp.message_handler(state=HealthRiskForm.city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    lat, lon = get_coordinates(city)
    if lat is None:
        await message.reply(f"❌ City '{city}' not found. Please enter again:")
        return
    await state.update_data(city=city, lat=lat, lon=lon)
    await message.reply("Enter the number of hours you spent outside:")
    await HealthRiskForm.hours.set()

@dp.message_handler(state=HealthRiskForm.hours)
async def process_hours(message: types.Message, state: FSMContext):
    try:
        hours = float(message.text)
        if hours < 0:
            raise ValueError
    except ValueError:
        await message.reply("❌ Please enter a valid number of hours:")
        return

    data = await state.get_data()
    city = data['city']
    lat = data['lat']
    lon = data['lon']

    aqi, _, _, _, _ = get_air_pollution(lat, lon)
    if aqi is None:
        await message.reply("❌ Could not retrieve AQI data.")
        await state.finish()
        return

    risk = estimate_health_risk(aqi, hours)

    await message.reply(
        f"🌍 Health risk estimation in {city}:\n"
        f"AQI: {aqi}\n"
        f"Time outside: {hours} hours\n"
        f"Risk level: {risk}"
    )
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
