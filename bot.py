import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from forecast import get_coordinates, download_nasa_air_quality, parse_nasa_air_quality, estimate_health_risk

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("BOT_TOKEN not set!")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ----------------- FSM для /healthrisk -----------------
class HealthRiskForm(StatesGroup):
    city = State()
    hours = State()

# ----------------- FSM для /nasa_aqi -----------------
class NASAForm(StatesGroup):
    city = State()

# ----------------- /start -----------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Hi! I am your Air Quality Bot 🌍\n"
        "Commands:\n"
        "/nasa_aqi — get NASA air quality data\n"
        "/healthrisk — estimate health risk based on AQI and time outdoors"
    )

# ----------------- /nasa_aqi -----------------
@dp.message_handler(commands=["nasa_aqi"])
async def nasa_aqi_start(message: types.Message):
    await message.reply("Enter the city name to get NASA air quality data:")
    await NASAForm.city.set()

@dp.message_handler(state=NASAForm.city)
async def nasa_aqi_process_city(message: types.Message, state: FSMContext):
    city = message.text
    lat, lon = get_coordinates(city)
    if lat is None:
        await message.reply(f"❌ City '{city}' not found. Please enter again:")
        return
    file_path = download_nasa_air_quality(lat, lon)
    if file_path is None:
        await message.reply("❌ Could not retrieve NASA AQI data.")
        await state.finish()
        return

    aqi, pm25, pm10 = parse_nasa_air_quality(file_path)
    if aqi is None:
        await message.reply("❌ Could not parse NASA AQI data.")
        await state.finish()
        return

    await message.reply(
        f"🌍 NASA Air Quality in {city}:\n"
        f"AQI: {aqi}\nPM2.5: {pm25} µg/m³\nPM10: {pm10} µg/m³"
    )
    await state.finish()

# ----------------- /healthrisk -----------------
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

    file_path = download_nasa_air_quality(lat, lon)
    aqi, _, _ = parse_nasa_air_quality(file_path)
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
