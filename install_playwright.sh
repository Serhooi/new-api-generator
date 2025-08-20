#!/bin/bash
# Скрипт установки Playwright для Render

echo "🎭 Устанавливаю Playwright..."

# Устанавливаем Playwright
python -m pip install playwright

# Устанавливаем браузеры
python -m playwright install chromium

echo "✅ Playwright установлен!"