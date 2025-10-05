import os
import requests

# API ключи
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")

if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not set!")
if not NASA_API_KEY:
    raise ValueError("NASA_API_KEY not set!")

# -------------------- OpenWeather functions --------------------
def get_coordinates(city: str):
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

def calculate_aqi(pm25: float, pm10: float):
    aqi_pm25 = int((pm25 / 12.0) * 50)
    aqi_pm10 = int((pm10 / 50.0) * 50)
    return max(aqi_pm25, aqi_pm10)

def get_air_pollution(lat: float, lon: float):
    url_aqi = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    url_weather = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
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
        print(f"Error getting data: {e}")
        return None, None, None, None, None

def analyze_conditions(aqi, temp, wind_speed):
    advices = []
    if temp >= 30:
        advices.append("🌡 High temperature — air pollution may increase.")
    elif temp <= 0:
        advices.append("❄ Low temperature — air pollution may decrease.")

    if wind_speed >= 5:
        advices.append("💨 Strong wind — air pollution likely decreases.")
    elif wind_speed <= 1:
        advices.append("💨 Low wind — air pollution may increase.")

    return " ".join(advices) if advices else "✅ Current conditions are stable for air quality."

def aqi_message(city: str):
    lat, lon = get_coordinates(city)
    if lat is None:
        return f"❌ City '{city}' not found."

    aqi, pm25, pm10, temp, wind_speed = get_air_pollution(lat, lon)
    if aqi is None:
        return "❌ Could not retrieve AQI data."

    if aqi <= 50:
        status = "Good"
    elif aqi <= 100:
        status = "Moderate"
    elif aqi <= 150:
        status = "Unhealthy for sensitive groups"
    elif aqi <= 200:
        status = "Unhealthy"
    else:
        status = "Very unhealthy"

    advice = analyze_conditions(aqi, temp, wind_speed)

    return (
        f"🌍 AQI in {city}: {aqi} ({status})\n"
        f"PM2.5: {pm25} µg/m³, PM10: {pm10} µg/m³\n"
        f"🌡 Temperature: {temp}°C, 💨 Wind: {wind_speed} m/s\n"
        f"{advice}"
    )

def estimate_health_risk(aqi, hours_outside):
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

# -------------------- NASA API functions --------------------
def get_nasa_air_quality(lat: float, lon: float):
    url = f"https://api.nasa.gov/airquality/v1/air_quality?lat={lat}&lon={lon}&api_key={NASA_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Пример структуры данных NASA (нужна адаптация под фактический API)
        aqi = data.get("aqi", None)
        pm25 = data.get("pm25", None)
        pm10 = data.get("pm10", None)
        temperature = data.get("temperature", None)
        wind_speed = data.get("wind_speed", None)

        return aqi, pm25, pm10, temperature, wind_speed
    except Exception as e:
        print(f"Error NASA API: {e}")
        return None, None, None, None, None
