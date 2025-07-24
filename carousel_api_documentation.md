# 🎠 ПОЛНОЦЕННАЯ КАРУСЕЛЬ API - ДОКУМЕНТАЦИЯ

## 🎯 Обзор

Теперь API поддерживает создание полноценных каруселей с **1 main слайдом + до 9 фото слайдов**.

### Поддерживаемые поля изображений:
- `dyno.propertyimage2` - 2-е фото недвижимости
- `dyno.propertyimage3` - 3-е фото недвижимости
- `dyno.propertyimage4` - 4-е фото недвижимости
- `dyno.propertyimage5` - 5-е фото недвижимости
- `dyno.propertyimage6` - 6-е фото недвижимости
- `dyno.propertyimage7` - 7-е фото недвижимости
- `dyno.propertyimage8` - 8-е фото недвижимости
- `dyno.propertyimage9` - 9-е фото недвижимости
- `dyno.propertyimage10` - 10-е фото недвижимости

## 🚀 API Endpoints

### 1. Создание полноценной карусели

**POST** `/api/carousel/create-and-generate`

#### Запрос:
```json
{
  "name": "Property Carousel for 123 Main St",
  "slides": [
    {
      "templateId": "open-house-main",
      "replacements": {
        "dyno.agentName": "John Smith",
        "dyno.propertyAddress": "123 Main Street, Beverly Hills, CA 90210",
        "dyno.price": "$450,000",
        "dyno.bedrooms": "3",
        "dyno.bathrooms": "2",
        "dyno.sqft": "1,850",
        "dyno.agentPhone": "(555) 123-4567",
        "dyno.agentEmail": "john@realty.com",
        "dyno.agentPhoto": "https://example.com/agent.jpg"
      },
      "imagePath": "https://example.com/exterior.jpg"
    },
    {
      "templateId": "open-house-photo",
      "replacements": {
        "dyno.propertyimage2": "https://example.com/living-room.jpg"
      },
      "imagePath": "https://example.com/living-room.jpg"
    },
    {
      "templateId": "open-house-photo", 
      "replacements": {
        "dyno.propertyimage3": "https://example.com/kitchen.jpg"
      },
      "imagePath": "https://example.com/kitchen.jpg"
    }
    // ... до 9 фото слайдов
  ]
}
```

#### Ответ:
```json
{
  "success": true,
  "carousel_id": "uuid-123",
  "name": "Property Carousel for 123 Main St",
  "slides_count": 3,
  "status": "completed",
  "slides": [
    {
      "slide_number": 1,
      "template_id": "open-house-main",
      "template_name": "Open House Main",
      "filename": "slide_01.svg",
      "url": "/output/carousel/uuid-123/slide_01.svg",
      "status": "completed"
    },
    {
      "slide_number": 2,
      "template_id": "open-house-photo",
      "template_name": "Open House Photo",
      "filename": "slide_02.svg", 
      "url": "/output/carousel/uuid-123/slide_02.svg",
      "status": "completed"
    },
    {
      "slide_number": 3,
      "template_id": "open-house-photo",
      "template_name": "Open House Photo",
      "filename": "slide_03.svg",
      "url": "/output/carousel/uuid-123/slide_03.svg", 
      "status": "completed"
    }
  ]
}
```

### 2. Получение информации о карусели

**GET** `/api/carousel/{carousel_id}/slides`

#### Ответ:
```json
{
  "carousel_id": "uuid-123",
  "name": "Property Carousel for 123 Main St",
  "status": "completed",
  "slides_count": 3,
  "created_at": "2025-01-24 10:30:00",
  "slides": [
    {
      "slide_number": 1,
      "filename": "slide_01.svg",
      "image_url": "/output/carousel/uuid-123/slide_01.svg",
      "status": "completed"
    },
    {
      "slide_number": 2,
      "filename": "slide_02.svg",
      "image_url": "/output/carousel/uuid-123/slide_02.svg",
      "status": "completed"
    },
    {
      "slide_number": 3,
      "filename": "slide_03.svg",
      "image_url": "/output/carousel/uuid-123/slide_03.svg",
      "status": "completed"
    }
  ]
}
```

## 💻 TypeScript Integration

### Обновленные типы:
```typescript
interface DynoReplacements {
  'dyno.agentName'?: string;
  'dyno.propertyAddress'?: string;
  'dyno.price'?: string;
  'dyno.bedrooms'?: string;
  'dyno.bathrooms'?: string;
  'dyno.sqft'?: string;
  'dyno.agentPhone'?: string;
  'dyno.agentEmail'?: string;
  'dyno.agentPhoto'?: string;
  // Поддержка до 9 дополнительных фото
  'dyno.propertyimage2'?: string;
  'dyno.propertyimage3'?: string;
  'dyno.propertyimage4'?: string;
  'dyno.propertyimage5'?: string;
  'dyno.propertyimage6'?: string;
  'dyno.propertyimage7'?: string;
  'dyno.propertyimage8'?: string;
  'dyno.propertyimage9'?: string;
  'dyno.propertyimage10'?: string;
}
```

### Вспомогательная функция:
```typescript
import { createPropertyCarousel } from './agentflow-integration';

// Простое создание карусели
const propertyData = {
  name: "Beautiful Family Home",
  agentName: "John Smith",
  propertyAddress: "123 Main Street, Beverly Hills, CA 90210",
  price: "$450,000",
  bedrooms: "3",
  bathrooms: "2", 
  sqft: "1,850",
  agentPhone: "(555) 123-4567",
  agentEmail: "john@realty.com",
  agentPhoto: "https://example.com/agent.jpg"
};

const propertyPhotos = [
  "https://example.com/exterior.jpg",
  "https://example.com/living-room.jpg", 
  "https://example.com/kitchen.jpg",
  "https://example.com/bedroom.jpg",
  "https://example.com/bathroom.jpg"
];

const carouselRequest = createPropertyCarousel(propertyData, propertyPhotos);
```

## 🎨 Структура файлов

### Организация файлов карусели:
```
output/
└── carousel/
    └── {carousel_id}/
        ├── slide_01.svg  (main слайд)
        ├── slide_02.svg  (dyno.propertyimage2)
        ├── slide_03.svg  (dyno.propertyimage3)
        ├── slide_04.svg  (dyno.propertyimage4)
        └── ...
```

## 📊 База данных

### Новая таблица `carousels_full`:
```sql
CREATE TABLE carousels_full (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slides_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Тестирование

### Пример тестового запроса:
```python
import requests

carousel_data = {
    "name": "Test Property Carousel",
    "slides": [
        {
            "templateId": "open-house-main",
            "replacements": {
                "dyno.agentName": "John Smith",
                "dyno.propertyAddress": "123 Main Street, Beverly Hills, CA 90210",
                "dyno.price": "$450,000",
                "dyno.agentPhoto": "https://example.com/agent.jpg"
            },
            "imagePath": "https://example.com/exterior.jpg"
        },
        {
            "templateId": "open-house-photo",
            "replacements": {
                "dyno.propertyimage2": "https://example.com/living-room.jpg"
            },
            "imagePath": "https://example.com/living-room.jpg"
        }
    ]
}

response = requests.post(
    "http://localhost:5000/api/carousel/create-and-generate",
    json=carousel_data
)

print(response.json())
```

## 🎯 Ключевые особенности

### ✅ Что работает:
- **Множественные фото слайды** - до 9 дополнительных фото
- **Автоматическая нумерация** - dyno.propertyimage2, dyno.propertyimage3, etc.
- **Синхронная генерация** - все слайды создаются сразу
- **Правильная структура файлов** - организованное хранение
- **TypeScript поддержка** - типизированные интерфейсы

### 🔧 Автоматические функции:
- **Автоматическое добавление полей** - API сам добавляет правильные dyno поля
- **Создание директорий** - автоматическое создание папок для карусели
- **Нумерация слайдов** - slide_01.svg, slide_02.svg, etc.
- **Сохранение метаданных** - информация о карусели в базе данных

## 🚀 Готово к использованию!

Теперь ваш API поддерживает полноценные карусели с множественными фото слайдами. Фронтенд может отправлять до 10 слайдов (1 main + 9 фото) и получать готовую карусель!