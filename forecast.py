import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# 🚨 ЗАГЛУШКА: пока нет API OpenAQ, создадим фейковые данные
# Потом заменишь на запрос к API
dates = pd.date_range("2025-09-01", periods=50, freq="H")
values = [50 + i*0.2 for i in range(50)]
data = pd.DataFrame({"ds": dates, "y": values})

# Создаём модель
model = Prophet()
model.fit(data)

# Прогноз на 24 часа вперёд
future = model.make_future_dataframe(periods=24, freq="H")
forecast = model.predict(future)

# Сохраняем прогноз
forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_csv("forecast.csv", index=False)

# Картинка
fig = model.plot(forecast)
plt.title("Прогноз PM2.5 на 24 часа")
plt.savefig("forecast.png")
