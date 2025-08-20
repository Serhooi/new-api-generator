# Dockerfile с rsvg-convert и CairoSVG для продакшена v2
FROM python:3.9-slim

# ПРИНУДИТЕЛЬНАЯ установка rsvg-convert и всех зависимостей
RUN echo "=== НАЧАЛО УСТАНОВКИ ПАКЕТОВ ==="
RUN apt-get update
RUN apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y --no-install-recommends \
    librsvg2-bin \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libffi-dev \
    python3-dev \
    shared-mime-info \
    fonts-dejavu-core
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN echo "=== ПАКЕТЫ УСТАНОВЛЕНЫ ==="

# ДЕТАЛЬНАЯ проверка что все работает
RUN echo "=== ПРОВЕРКА УСТАНОВЛЕННЫХ ПАКЕТОВ ==="
RUN echo "1. Проверяю rsvg-convert:"
RUN which rsvg-convert || echo "❌ rsvg-convert НЕ НАЙДЕН"
RUN rsvg-convert --version || echo "❌ rsvg-convert НЕ РАБОТАЕТ"
RUN echo "2. Проверяю Cairo библиотеки:"
RUN ls -la /usr/lib/x86_64-linux-gnu/ | grep cairo || echo "❌ Cairo библиотеки НЕ НАЙДЕНЫ"
RUN echo "3. Проверяю Pango библиотеки:"
RUN ls -la /usr/lib/x86_64-linux-gnu/ | grep pango || echo "❌ Pango библиотеки НЕ НАЙДЕНЫ"
RUN echo "=== КОНЕЦ ПРОВЕРКИ ==="

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Проверяем что CairoSVG работает после установки
RUN echo "=== ПРОВЕРКА PYTHON ПАКЕТОВ ==="
RUN python3 -c "import cairosvg; print('✅ CairoSVG работает')" || echo "❌ CairoSVG НЕ РАБОТАЕТ"
RUN python3 -c "import PIL; print('✅ Pillow работает')" || echo "❌ Pillow НЕ РАБОТАЕТ"
RUN echo "=== PYTHON ПАКЕТЫ ПРОВЕРЕНЫ ==="

# Копируем код приложения
COPY . .

# Устанавливаем переменную окружения для порта
ENV PORT=5000

# Открываем порт
EXPOSE $PORT

# Запускаем приложение
CMD gunicorn --bind 0.0.0.0:$PORT app:app