#!/bin/bash
# Скрипт установки шрифтов для Render

echo "🔤 Устанавливаю системные шрифты..."

# Обновляем пакеты
apt-get update -y

# Устанавливаем основные шрифты
apt-get install -y \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    fonts-roboto \
    fonts-open-sans \
    fontconfig

# Обновляем кэш шрифтов
fc-cache -fv

echo "✅ Шрифты установлены!"
echo "📋 Доступные шрифты:"
fc-list | head -10

