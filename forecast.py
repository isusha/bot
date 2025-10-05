import requests
import matplotlib.pyplot as plt
import pandas as pd
import os

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "95e13bfa3b35404fd122302be673e711cefd4c878a125edb91389d97a0d53d1b")

def get_forecast(city: str):
    url = f"https://api.openaq.org/v2/latest?city={city}&parameter=pm25"
    headers = {"X-API-Key": OPENAQ_API_KEY}
    resp = requests.get(url, headers=headers).json()

    if "results" not in resp or len(resp["results"]) == 0:
        return f"❌ Данные по городу '{city}' не найдены.", None

    measurements = resp["results"][0]["measurements"]
    if not measurements:
        return f"⚠️ Нет данных по качеству воздуха для '{city}'", None

    value = measurements[0]["value"]

    # AQI градация
    if value <= 50:
        status = "🟢 Хорошее качество воздуха"
    elif value <= 100:
        status = "🟡 Умеренное качество воздуха"
    elif value <= 150:
        status = "🟠 Вредно для чувствительных групп"
    else:
        status = "🔴 Вредно для здоровья"

    # график (можно на 1 точку или позже расширить до прогноза)
    plt.figure(figsize=(6,4))
    plt.bar([city], [value], color="green" if value<=50 else "orange" if value<=100 else "red")
    plt.title(f"PM2.5 в {city}")
    plt.ylabel("µg/m³")
    plt.tight_layout()

    image_path = "forecast.png"
    plt.savefig(image_path)
    plt.close()

    text = f"🌍 Город: {city}\nPM2.5: {value}\nСтатус: {status}"
    return text, image_path
