import os
import requests

# Ключ OpenWeather, сохраняем в переменной окружения OPENWEATHER_API_KEY
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("Не задан OPENWEATHER_API_KEY!")

def get_coordinates(city: str):
    """Получаем координаты города через OpenWeather Geocoding API"""
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            return lat, lon
    except Exception as e:
        print(f"Ошибка при получении координат: {e}")
    return None, None

def get_aqi(lat: float, lon: float):
    """Получаем AQI через OpenWeather Air Pollution API"""
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # OpenWeather возвращает aqi от 1 до 5
        aqi_index = data["list"][0]["main"]["aqi"]
        return aqi_index
    except Exception as e:
        print(f"Ошибка при получении AQI: {e}")
        return None

def aqi_message(city: str):
    """Возвращает текстовое сообщение для Telegram"""
    lat, lon = get_coordinates(city)
    if lat is None:
        return f"❌ Город '{city}' не найден."

    aqi_index = get_aqi(lat, lon)
    if aqi_index is None:
        return "❌ Не удалось получить данные AQI."

    # Статусы по документации OpenWeather
    status = ["Хороший", "Умеренный", "Вредный для чувствительных", "Вредный", "Очень вредный"]
    return f"🌍 AQI в {city}: {aqi_index} ({status[aqi_index-1]})"
