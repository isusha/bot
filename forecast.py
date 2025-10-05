import os
import requests
import sys

# Берём API ключ из переменной окружения
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

def get_air_quality(city: str):
    url = f"https://api.openaq.org/v3/latest?city={city}"
    headers = {
        "X-API-Key": OPENAQ_API_KEY
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                return f"Нет данных для города {city}."

            # Собираем значения по всем станциям
            text = f"🌍 Качество воздуха в {city}:\n\n"
            for location in results:
                loc_name = location.get("location", "Неизвестная станция")
                measurements = location.get("measurements", [])
                text += f"📍 {loc_name}\n"
                for m in measurements:
                    param = m.get("parameter", "")
                    value = m.get("value", "")
                    unit = m.get("unit", "")
                    text += f"  • {param}: {value} {unit}\n"
                text += "\n"
            return text.strip()
        else:
            return f"Ошибка API: {response.status_code} — {response.text}"
    except Exception as e:
        return f"Ошибка при запросе: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажи город. Например: python forecast.py London")
    else:
        city = sys.argv[1]
        print(get_air_quality(city))
