# Dockerfile с rsvg-convert и CairoSVG для продакшена
FROM python:3.9-slim

# Устанавливаем ВСЕ необходимые зависимости по рекомендации ChatGPT
RUN apt-get update && apt-get install -y --no-install-recommends \
    librsvg2-bin libgdk-pixbuf2.0-0 \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libffi-dev python3-dev shared-mime-info \
    fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Проверяем что rsvg-convert установлен
RUN which rsvg-convert && rsvg-convert --version

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