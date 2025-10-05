import os
import requests
import h5py
import numpy as np

# ---------------------- Настройки ----------------------
NASA_TOKEN = os.getenv("NASA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not NASA_TOKEN:
    raise ValueError("NASA_API_KEY not set!")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not set!")

# ---------------------- Функции ----------------------
def get_coordinates(city: str):
    """Получаем координаты города через OpenWeather Geo API"""
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
    except Exception as e:
        print(f"Error getting coordinates: {e}")
    return None, None

def download_nasa_air_quality(lat: float, lon: float):
    """
    Скачиваем данные NASA по координатам через токен.
    Пример: GEOS-CF/processed AQ data в формате NetCDF/HDF5.
    """
    url = f"https://example-nasa-data-url/{lat},{lon}/air_quality.nc"  # <-- заменить на реальный URL NASA
    headers = {"Authorization": f"Bearer {NASA_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        with open("nasa_air_quality.nc", "wb") as f:
            f.write(response.content)
        return "nasa_air_quality.nc"
    except Exception as e:
        print(f"Error downloading NASA data: {e}")
        return None

def parse_nasa_air_quality(file_path):
    """Парсер HDF5/NetCDF, возвращает AQI и PM2.5/PM10"""
    try:
        with h5py.File(file_path, "r") as f:
            # Структура файла может быть разная, пример для GEOS-CF
            aqi = f["AQI"][0]
            pm25 = f["PM2_5"][0]
            pm10 = f["PM10"][0]
            return int(aqi), float(pm25), float(pm10)
    except Exception as e:
        print(f"Error parsing NASA data: {e}")
        return None, None, None

def estimate_health_risk(aqi, hours_outside):
    """Оценка риска для здоровья на основе AQI и времени на улице"""
    if aqi <= 50:
        return "Safe exposure 👍"
    elif aqi <= 100:
        if hours_outside <= 2:
            return "Minor risk — short time outside is generally safe."
        elif hours_outside <= 5:
            return "Moderate risk — consider limiting outdoor time."
        else:
            return "High risk — reduce outdoor exposure!"
    elif aqi <= 150:
        if hours_outside <= 2:
            return "Moderate risk — sensitive people should be careful."
        elif hours_outside <= 5:
            return "High risk — prolonged exposure not recommended!"
        else:
            return "Very high risk — avoid staying outside!"
    elif aqi <= 200:
        if hours_outside <= 2:
            return "High risk — limit outdoor activities."
        elif hours_outside <= 5:
            return "Very high risk — avoid outdoor exposure."
        else:
            return "Danger — severe risk for everyone!"
    else:
        return "Extreme danger — avoid any outdoor exposure!"
