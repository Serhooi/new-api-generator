# 🧪 РУКОВОДСТВО ПО ТЕСТИРОВАНИЮ

## 🚀 Быстрый старт

### 1. Запуск сервера
```bash
python3 app.py
```

### 2. Тестирование локального сохранения
```bash
python3 test_local_files.py
```

### 3. Проверка слайдов
```bash
python3 debug_slide_loading.py
```

## 🔧 Исправленные проблемы

### ❌ "Failed to load slide 1, Image URL may be expired or invalid"

**Причина**: Неправильная конфигурация Supabase

**Решение**: 
- ✅ Исправлена конфигурация Supabase URL
- ✅ Для локальной разработки файлы сохраняются локально
- ✅ URL слайдов теперь доступны через `localhost:5000`

## 📋 Что проверить

### 1. Сервер запущен
```
✅ Flask app running on http://127.0.0.1:5000
✅ Supabase клиент инициализирован (или локальное сохранение)
```

### 2. Создание карусели работает
```bash
curl -X POST http://localhost:5000/api/carousel/create-and-generate \
  -H "Content-Type: application/json" \
  -d '{
    "dyno.agentName": "Test Agent",
    "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
    "dyno.propertyimage2": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300"
  }'
```

### 3. Слайды доступны
- ✅ URL слайдов возвращаются в ответе API
- ✅ Файлы существуют в `output/carousel/`
- ✅ Файлы доступны по HTTP через `localhost:5000/output/carousel/`
- ✅ SVG содержат base64 изображения

## 🎯 Ожидаемый результат

### API ответ:
```json
{
  "success": true,
  "carousel_id": "uuid-here",
  "slides": [
    {
      "type": "main",
      "url": "http://localhost:5000/output/carousel/carousel_uuid_main.svg"
    },
    {
      "type": "photo",
      "url": "http://localhost:5000/output/carousel/carousel_uuid_photo_1.svg"
    }
  ]
}
```

### Файлы:
```
output/carousel/
├── carousel_uuid_main.svg     (содержит dyno.propertyimage)
└── carousel_uuid_photo_1.svg  (содержит dyno.propertyimage2)
```

### SVG содержимое:
- ✅ Headshot: правильный размер (scale 0.7) без растягивания
- ✅ Main слайд: использует `dyno.propertyimage`
- ✅ Photo слайд: использует `dyno.propertyimage2`
- ✅ Все изображения конвертированы в base64

## 🐛 Отладка проблем

### Проблема: Сервер не запускается
```bash
# Проверить зависимости
pip install -r requirements.txt

# Проверить порт
lsof -i :5000
```

### Проблема: Слайды не создаются
```bash
# Проверить директории
ls -la output/carousel/

# Проверить логи сервера
# Должны быть сообщения о создании файлов
```

### Проблема: Изображения не загружаются
```bash
# Тест доступности изображений
python3 debug_image_loading.py
```

### Проблема: Фронтенд не загружает слайды
1. Проверить что URL слайдов доступны в браузере
2. Проверить CORS настройки
3. Проверить что SVG файлы валидны

## ✅ Финальная проверка

Все должно работать если:
- ✅ Сервер запущен на порту 5000
- ✅ API возвращает URL слайдов
- ✅ URL слайдов доступны в браузере
- ✅ SVG файлы содержат base64 изображения
- ✅ Headshot правильного размера
- ✅ Photo слайды используют правильные изображения

**Статус**: 🟢 Готово к использованию!