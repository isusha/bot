import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

if not OPENWEATHER_KEY:
    raise RuntimeError("Не найдена переменная окружения OPENWEATHER_KEY")


def get_city_coords(city):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 1, "appid": OPENWEATHER_KEY}
    resp = requests.get(url, params=params).json()
    if not resp:
        return None
    return resp[0]["lat"], resp[0]["lon"]


def get_air_forecast(lat, lon):
    url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY}
    return requests.get(url, params=params).json()


def aqi_category(aqi):
    if aqi == 1:
        return "🟢 Хорошо"
    elif aqi == 2:
        return "🟡 Умеренно"
    elif aqi == 3:
        return "🟠 Вредно для чувствительных"
    elif aqi == 4:
        return "🔴 Вредно"
    elif aqi == 5:
        return "🟣 Очень вредно"
    return "❓ Неизвестно"


def get_forecast(city: str):
    coords = get_city_coords(city)
    if not coords:
        return f"Город '{city}' не найден.", None

    lat, lon = coords
    data = get_air_forecast(lat, lon)
    if "list" not in data:
        return f"Нет данных прогноза для {city}", None

    times, aqis, cats = [], [], []
    for item in data["list"][:24]:  # прогноз на 24 часа
        dt = datetime.fromtimestamp(item["dt"])
        aqi = item["main"]["aqi"]  # 1–5 по OpenWeather
        times.append(dt)
        aqis.append(aqi)
        cats.append(aqi_category(aqi))

    df = pd.DataFrame({"Время": times, "AQI": aqis, "Категория": cats})

    # Строим график
    plt.figure(figsize=(10, 4))
    plt.plot(df["Время"], df["AQI"], marker="o", color="blue")
    plt.title(f"Прогноз AQI на 24 часа для {city}")
    plt.xlabel("Время")
    plt.ylabel("AQI (1=лучше, 5=хуже)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("forecast.png")

    # Формируем текст
    summary = f"Прогноз качества воздуха для {city}:\n\n"
    for _, row in df.iterrows():
        summary += f"{row['Время'].strftime('%H:%M')} — {row['Категория']}\n"

    return summary, "forecast.png"
