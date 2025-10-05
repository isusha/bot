import os
import requests

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
            return data[0]["lat"], data[0]["lon"]
    except Exception as e:
        print(f"Ошибка при получении координат: {e}")
    return None, None

def calculate_aqi(pm25: float, pm10: float):
    """Считаем AQI аналогично Android"""
    aqi_pm25 = int((pm25 / 12.0) * 50)
    aqi_pm10 = int((pm10 / 50.0) * 50)
    return max(aqi_pm25, aqi_pm10)

def get_air_pollution(lat: float, lon: float):
    """Получаем AQI, PM2.5, PM10, температуру и скорость ветра"""
    url_aqi = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    url_weather = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        resp_aqi = requests.get(url_aqi, timeout=10)
        resp_aqi.raise_for_status()
        data_aqi = resp_aqi.json()
        components = data_aqi["list"][0]["components"]
        pm25 = components.get("pm2_5", 0)
        pm10 = components.get("pm10", 0)
        aqi = calculate_aqi(pm25, pm10)

        resp_weather = requests.get(url_weather, timeout=10)
        resp_weather.raise_for_status()
        data_weather = resp_weather.json()
        temp = data_weather["main"]["temp"]
        wind_speed = data_weather["wind"].get("speed", 0)

        return aqi, pm25, pm10, temp, wind_speed
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None, None, None, None, None

def analyze_conditions(aqi, temp, wind_speed):
    """Даем прогноз по изменению загрязнения воздуха"""
    advices = []
    if temp >= 30:
        advices.append("🌡 Высокая температура — возможное увеличение загрязнения.")
    elif temp <= 0:
        advices.append("❄ Низкая температура — загрязнение может уменьшаться.")

    if wind_speed >= 5:
        advices.append("💨 Сильный ветер — загрязнение воздуха вероятно уменьшится.")
    elif wind_speed <= 1:
        advices.append("💨 Слабый ветер — загрязнение может увеличиться.")

    return " ".join(advices) if advices else "✅ Текущие условия стабильны для воздуха."

def aqi_message(city: str):
    """Возвращаем текст для Telegram"""
    lat, lon = get_coordinates(city)
    if lat is None:
        return f"❌ Город '{city}' не найден."

    aqi, pm25, pm10, temp, wind_speed = get_air_pollution(lat, lon)
    if aqi is None:
        return "❌ Не удалось получить данные AQI."

    if aqi <= 50:
        status = "Хороший"
    elif aqi <= 100:
        status = "Умеренный"
    elif aqi <= 150:
        status = "Вредный для чувствительных"
    elif aqi <= 200:
        status = "Вредный"
    else:
        status = "Очень вредный"

    advice = analyze_conditions(aqi, temp, wind_speed)

    return (
        f"🌍 AQI в {city}: {aqi} ({status})\n"
        f"PM2.5: {pm25} µg/m³, PM10: {pm10} µg/m³\n"
        f"🌡 Температура: {temp}°C, 💨 Ветер: {wind_speed} м/с\n"
        f"{advice}"
    )
