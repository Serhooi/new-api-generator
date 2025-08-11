# Исправления для множественных SVG файлов карусели

## ✅ Что исправлено:

### 1. Увеличено количество photo слайдов до 9
- Теперь можно загружать от 1 до 9 photo слайдов
- Поддержка dyno.propertyimage2 до dyno.propertyimage10

### 2. Упрощена обработка хедшотов
- Для хедшотов теперь ТОЛЬКО заменяется URL
- НЕ применяются никакие трансформации или изменения preserveAspectRatio
- Хедшоты работают как логотипы - простая замена URL

### 3. Правильный маппинг полей для карусели
- Main слайд: `dyno.propertyimage`, `dyno.agentheadshot`, `dyno.name`, и т.д.
- Photo слайд 1: `dyno.propertyimage2` 
- Photo слайд 2: `dyno.propertyimage3`
- Photo слайд 3: `dyno.propertyimage4`
- И так далее до `dyno.propertyimage10`

### 4. Новый API эндпоинт
- `/api/carousel/create-and-generate` - основной эндпоинт для создания карусели
- `/api/carousel` - простой эндпоинт (перенаправляет на основной)
- Автоматическое определение количества photo слайдов по наличию полей

## 🎯 Как это работает:

### Пример запроса:
```json
{
  "main_template_name": "Modern Open House - Main",
  "photo_template_name": "Modern Open House - Photo",
  "replacements": {
    "dyno.propertyimage": "https://example.com/main.jpg",
    "dyno.agentheadshot": "https://example.com/agent.jpg",
    "dyno.name": "John Smith",
    "dyno.propertyimage2": "https://example.com/photo1.jpg",
    "dyno.propertyimage3": "https://example.com/photo2.jpg",
    "dyno.propertyimage4": "https://example.com/photo3.jpg"
  }
}
```

### Результат:
- 1 main слайд с `dyno.propertyimage` и `dyno.agentheadshot`
- 3 photo слайда с `dyno.propertyimage2`, `dyno.propertyimage3`, `dyno.propertyimage4`
- Всего 4 слайда в карусели

## 🔧 Изменения в коде:

### Frontend (upload.html):
- Увеличено количество photo слотов до 9
- Улучшена обработка множественных файлов
- Динамическое создание photo слотов

### Backend (app.py):
- Упрощена обработка хедшотов (только замена URL)
- Новый эндпоинт `/api/carousel/create-and-generate`
- Правильный маппинг dyno.propertyimage2-10
- Автоматическое определение количества photo слайдов

## 🚀 Готово к использованию!

Теперь ваше приложение поддерживает:
- ✅ До 9 photo слайдов
- ✅ Правильный маппинг dyno.propertyimage2-10  
- ✅ Простую обработку хедшотов (только замена URL)
- ✅ Автоматическое определение количества слайдов