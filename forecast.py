import os
import requests

# токен OpenAQ
OPENAQ_TOKEN = os.getenv("OPENAQ_TOKEN")

BASE_URL = "https://api.openaq.org/v3/latest"


def get_city_air_quality(city: str) -> str:
    """
    Получаем качество воздуха по городу через OpenAQ API
    """

    headers = {"X-API-Key": OPENAQ_TOKEN}

    params = {
        "city": city
    }

    try:
        resp = requests.get(BASE_URL, headers=headers, params=params, timeout=10)

        if resp.status_code == 401:
            return "❌ Ошибка: неверный или отсутствует API ключ."

        if resp.status_code != 200:
            return f"⚠️ Ошибка API: {resp.status_code}"

        data = resp.json()

        if "results" not in data or len(data["results"]) == 0:
            return f"❌ Данные для города {city} не найдены."

        # берем первую запись
        measurements = data["results"][0]["measurements"]

        msg = f"🌍 Город: {city}\n"
        msg += "Последние замеры качества воздуха:\n"

        for m in measurements:
            msg += f"• {m['parameter']} = {m['value']} {m['unit']} (время: {m['lastUpdated']})\n"

        return msg

    except Exception as e:
        return f"❌ Ошибка при получении данных: {e}"
