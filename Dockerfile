FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/

# Порт для healthcheck (добавим простой хелсчек сервер)
EXPOSE 8080

# Запуск приложения
CMD ["python", "-m", "app.main"] 