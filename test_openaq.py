import os, requests, sys

CANDIDATES = ["OPENAQ_API_KEY", "OPENAQ_TOKEN", "OPENAQ", "OPENAQKEY"]

def find_key():
    for name in CANDIDATES:
        v = os.getenv(name)
        if v and v.strip():
            return name, v.strip()
    return None, None

def mask(k):
    if not k: return "None"
    if len(k) <= 8: return k[0] + "****" + k[-1]
    return k[:4] + "*"*(len(k)-8) + k[-4:]

if __name__ == "__main__":
    city = "London"
    if len(sys.argv) > 1:
        city = sys.argv[1]

    name, key = find_key()
    print("Проверка переменных окружения...")
    for n in CANDIDATES:
        print(f"  -> {n} = {'SET' if os.getenv(n) else 'NOT SET'}")

    if not key:
        print("\nОШИБКА: не найден API-ключ. Поставь переменную OPENAQ_API_KEY (или OPENAQ_TOKEN) и перезапусти сервис.")
        raise SystemExit(1)

    print(f"\nБуду использовать переменную: {name} = {mask(key)}")

    url = "https://api.openaq.org/v3/latest"
    headers = {"X-API-Key": key}
    params = {"city": city, "limit": 1}

    print(f"\nДелаю запрос: {url}?city={city} (с заголовком X-API-Key)")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
    except Exception as e:
        print("Ошибка при запросе:", e)
        raise SystemExit(1)

    print("HTTP status:", resp.status_code)
    preview = resp.text[:1000]
    print("Ответ (preview):\n", preview)
    if resp.status_code == 401:
        print("\n401 Unauthorized — ключ неверный или не принимается сервером. Проверь ключ в аккаунте OpenAQ.")
    elif resp.status_code == 200:
        print("\nOK — API отвечает. Пробуй /aqi в боте.")
    else:
        print("\nСтатус отличный от 200/401 — смотри текст ответа.")
