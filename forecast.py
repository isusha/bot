import requests
import os

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")  # Токен OpenAQ

def get_air_quality(city: str) -> str:
    url = f"https://api.openaq.org/v2/latest?city={city}"
    headers = {"X-API-Key": OPENAQ_API_KEY}
    resp = requests.get(url, headers=headers).json()

    # Если данных нет
    if "results" not in resp or len(resp["results"]) == 0:
        return f"❌ Данные для города '{city}' не найдены."

    result = resp["results"][0]
    location = result.get("location", "Неизвестная станция")
    country = result.get("country", "N/A")

    measurements = result.get("measurements", [])
    if not measurements:
        return f"⚠️ В городе '{city}' нет доступных данных сейчас."

    # Собираем текст
    text = f"🌍 Город: {city} ({country})\n📍 Станция: {location}\n\n"
    for m in measurements:
        param = m["parameter"].upper()
        val = m["value"]
        unit = m["unit"]
        last_updated = m["lastUpdated"]
        text += f"• {param}: {val} {unit} (обновлено {last_updated})\n"

    return text
