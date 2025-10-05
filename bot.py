import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from forecast import aqi_message, get_coordinates, get_air_pollution, estimate_health_risk
import requests

API_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_TOKEN:
    raise ValueError("BOT_TOKEN not set!")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not set!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ----------------- FSM для /healthrisk -----------------
class HealthRiskForm(StatesGroup):
    city = State()
    hours = State()

# ----------------- /start -----------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Hi! I am your Air Quality Bot 🌍\n"
        "Commands:\n"
        "/aqi <city> — get air quality info\n"
        "/healthrisk — estimate health risk based on AQI and time outdoors\n"
        "/earthdata — learn more on NASA Earthdata"
    )

# ----------------- /aqi -----------------
@dp.message_handler(commands=["aqi"])
async def aqi_handler(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("❗ Please write: /aqi <city>\nExample: /aqi London")
        return
    city = parts[1]
    result = aqi_message(city)
    await message.reply(result)

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

    # Получаем AQI через OpenWeather
    try:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        resp = requests.get(url, timeout=10).json()
        aqi_raw = resp["list"][0]["main"]["aqi"]  # 1-5 по шкале OpenWeather
        # Конвертируем в примерный AQI 0-200 для рисков
        aqi_map = {1:25, 2:50, 3:100, 4:150, 5:200}
        aqi = aqi_map.get(aqi_raw, 75)
    except Exception as e:
        await message.reply(f"❌ Could not retrieve AQI: {e}")
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

# ----------------- /earthdata -----------------
@dp.message_handler(commands=["earthdata"])
async def earthdata_info(message: types.Message):
    await message.reply(
        "🌎 Want to explore NASA Earthdata yourself?\n"
        "You can search and access datasets here:\n"
        "https://search.earthdata.nasa.gov/search\n"
        "This is a great resource for real satellite data on air quality, climate, and more."
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
