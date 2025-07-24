# 🏗️ АНАЛИЗ АРХИТЕКТУРЫ СЕРВИСА ФЛАЕРОВ НЕДВИЖИМОСТИ

## 📋 Общая схема работы

```
ФРОНТЕНД (React/TS) 
    ↓ API запросы
FLASK API СЕРВИС
    ↓ обработка SVG
ГЕНЕРАЦИЯ ФЛАЕРОВ
    ↓ результат
КАРУСЕЛЬ ИЗОБРАЖЕНИЙ (до 10 фото)
```

## 🎯 Основной флоу пользователя

### 1. **Загрузка шаблонов (админ)**
```
Админ → /upload → Загружает SVG шаблоны:
├── Main Template (основная информация о листинге)
└── Photo Template (для фотографий интерьера/экстерьера)
```

### 2. **Выбор шаблона (пользователь)**
```
Пользователь → Фронтенд → GET /api/templates/all-previews
├── Получает список доступных шаблонов
├── Видит превью каждого шаблона
└── Выбирает Main + Photo шаблон
```

### 3. **Создание карусели**
```
Пользователь заполняет данные:
├── Информация о листинге (адрес, цена, спальни, ванные)
├── Информация об агенте (имя, телефон, email, фото)
├── Фотографии недвижимости (до 10 штук)
└── Отправляет на API
```

## 🔧 API Endpoints

### Основные endpoints:
- `GET /api/templates/all-previews` - получить все шаблоны
- `POST /api/generate/carousel` - создать карусель по ID шаблонов
- `POST /api/generate/carousel-by-name` - создать карусель по именам шаблонов
- `POST /api/upload-single` - загрузить одиночный шаблон
- `POST /api/upload-carousel` - загрузить пару шаблонов (main+photo)

### Отсутствующий endpoint:
- `POST /api/carousel/create-and-generate` - **НЕ РЕАЛИЗОВАН!**

## 📊 Структура данных

### Входные данные для карусели:
```json
{
  "main_template_id": "uuid-main-template",
  "photo_template_id": "uuid-photo-template", 
  "replacements": {
    "dyno.agentName": "John Smith",
    "dyno.propertyAddress": "123 Main Street, Beverly Hills, CA 90210",
    "dyno.price": "$450,000",
    "dyno.bedrooms": "3",
    "dyno.bathrooms": "2",
    "dyno.sqft": "1,850",
    "dyno.agentPhone": "(555) 123-4567",
    "dyno.agentEmail": "john@realty.com",
    "dyno.agentPhoto": "https://example.com/agent.jpg",
    "dyno.propertyImage": "https://example.com/photo1.jpg"
  }
}
```

### Выходные данные:
```json
{
  "success": true,
  "carousel_id": "uuid-carousel",
  "main_url": "/output/carousel/carousel_uuid_main.svg",
  "photo_url": "/output/carousel/carousel_uuid_photo.svg"
}
```

## 🎨 Обработка SVG

### Типы полей в шаблонах:
1. **Текстовые поля:**
   - `dyno.agentName` - имя агента
   - `dyno.propertyAddress` - адрес (с автоматическим переносом)
   - `dyno.price` - цена
   - `dyno.bedrooms`, `dyno.bathrooms`, `dyno.sqft` - характеристики

2. **Изображения:**
   - `dyno.agentPhoto` - фото агента (круглое, aspect ratio: meet)
   - `dyno.propertyImage` - фото недвижимости (прямоугольное, aspect ratio: slice)
   - `dyno.companyLogo` - логотип компании (aspect ratio: meet)

### Специальная обработка:
- **Адреса**: автоматический перенос длинных адресов на 2 строки
- **Изображения**: правильный aspect ratio для разных типов
- **Шрифты**: сохранение оригинальных шрифтов (Inter, Montserrat)
- **Экранирование**: безопасная обработка спецсимволов (&, <, >, ", ')

## 🚀 Генерация карусели

### Логика создания:
1. **Main слайд** - основная информация о листинге
2. **Photo слайды** - до 10 фотографий интерьера/экстерьера
3. Каждый слайд генерируется отдельно с заменой dyno полей
4. Результат: набор SVG файлов готовых для отображения

### Файловая структура:
```
output/
├── carousel/
│   ├── carousel_{id}_main.svg
│   └── carousel_{id}_photo.svg
├── single/
│   └── single_{id}.svg
└── previews/
    └── {template_id}_preview.png
```

## ⚠️ Проблемы и недостатки

### 1. **Отсутствующий endpoint**
- TypeScript код ссылается на `/api/carousel/create-and-generate`
- Этот endpoint НЕ РЕАЛИЗОВАН в Flask приложении
- Нужно либо реализовать, либо обновить фронтенд код

### 2. **Ограниченная функциональность карусели**
- Текущие endpoints генерируют только 2 файла (main + photo)
- Нет поддержки множественных фото слайдов
- Нет асинхронной обработки с отслеживанием статуса

### 3. **Отсутствие PNG генерации**
- SVG файлы не конвертируются в PNG автоматически
- Фронтенд получает только SVG ссылки

## 💡 Рекомендации по улучшению

### 1. **Реализовать полноценную карусель**
```python
@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    # Принимать массив фотографий
    # Создавать main + множественные photo слайды
    # Возвращать carousel_id для отслеживания статуса
```

### 2. **Добавить асинхронную обработку**
```python
@app.route('/api/carousel/<carousel_id>/status', methods=['GET'])
def get_carousel_status(carousel_id):
    # Возвращать статус генерации
    # Список готовых слайдов с URL
```

### 3. **Автоматическая PNG конвертация**
- Генерировать PNG версии для лучшей совместимости
- Добавить разные размеры (thumbnail, full)

### 4. **Улучшить TypeScript интеграцию**
- Синхронизировать API endpoints с реальной реализацией
- Добавить правильные типы данных
- Реализовать polling для отслеживания статуса

## 🎯 Текущее состояние

**Работает:**
- ✅ Загрузка и хранение шаблонов
- ✅ Обработка SVG с заменой dyno полей
- ✅ Генерация простых каруселей (main + photo)
- ✅ Веб-интерфейс для управления

**Не работает:**
- ❌ Endpoint `/api/carousel/create-and-generate`
- ❌ Множественные фото слайды в одной карусели
- ❌ Асинхронная обработка с отслеживанием статуса
- ❌ Автоматическая PNG конвертация

**Нужно доработать:**
- 🔧 Синхронизация фронтенд/бэкенд API
- 🔧 Поддержка до 10 фото в карусели
- 🔧 Улучшение производительности
- 🔧 Добавление валидации данных