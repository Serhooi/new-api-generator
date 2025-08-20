# Dockerfile с rsvg-convert для продакшена
FROM python:3.9-slim

# Устанавливаем системные зависимости включая rsvg-convert
RUN apt-get update && apt-get install -y \
    librsvg2-bin \
    librsvg2-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Проверяем что rsvg-convert установлен
RUN rsvg-convert --version

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости (без playwright для экономии места)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Устанавливаем переменную окружения для порта
ENV PORT=5000

# Открываем порт
EXPOSE $PORT

# Запускаем приложение
CMD gunicorn --bind 0.0.0.0:$PORT app:app