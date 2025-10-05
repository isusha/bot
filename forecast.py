import os
import requests

API_KEY = os.getenv("OPENAQ_API_KEY")  # ключ для OpenAQ, храним в Railway Variables

def get_aqi(city: str) -> str:
    """
    Получаем данные качества воздуха по городу из OpenAQ API
    """
    url = "https://api.openaq.org/v3/latest"
    headers = {"X-API-Key": API_KEY}   # добавляем API-ключ в заголовки
    params = {"city": city, "limit": 1}

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code != 200:
        return f"Ошибка: {resp.status_code} — {resp.text}"

    data = resp.json()

    if not data.get("results"):
        return f"❌ Данных для города {city} не найдено."

    result = data["results"][0]
    location = result["location"]
    measurements = result["measurements"]

    text = [f"🌍 Качество воздуха в {city} ({location}):"]
    for m in measurements:
        text.append(f"• {m['parameter']} = {m['value']} {m['unit']} (обновлено: {m['lastUpdated']})")

    return "\n".join(text)
