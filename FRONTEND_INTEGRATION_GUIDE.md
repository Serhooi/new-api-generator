# 🌐 РУКОВОДСТВО ПО ИНТЕГРАЦИИ ДЛЯ ФРОНТЕНДА

## 🎯 Генерация карусели (до 10 слайдов)

### **API Endpoint:**
```
POST /api/carousel/create-and-generate
```

### **Структура запроса:**
```json
{
  "name": "Название карусели",
  "main_template_name": "Имя главного шаблона",
  "photo_template_name": "Имя фото шаблона",
  "replacements": {
    // Основные поля для всех слайдов
    "dyno.agentName": "Имя агента",
    "dyno.agentPhone": "Телефон агента",
    "dyno.agentEmail": "Email агента",
    "dyno.agentheadshot": "URL фото агента",
    "dyno.logo": "URL логотипа",
    "dyno.propertyAddress": "Адрес недвижимости",
    "dyno.price": "Цена",
    "dyno.bedrooms": "Количество спален",
    "dyno.bathrooms": "Количество ванных",
    
    // Изображения для разных слайдов
    "dyno.propertyimage": "URL главного изображения (для main слайда)",
    "dyno.propertyimage2": "URL изображения для photo слайда 1",
    "dyno.propertyimage3": "URL изображения для photo слайда 2",
    "dyno.propertyimage4": "URL изображения для photo слайда 3",
    "dyno.propertyimage5": "URL изображения для photo слайда 4",
    "dyno.propertyimage6": "URL изображения для photo слайда 5",
    "dyno.propertyimage7": "URL изображения для photo слайда 6",
    "dyno.propertyimage8": "URL изображения для photo слайда 7",
    "dyno.propertyimage9": "URL изображения для photo слайда 8",
    "dyno.propertyimage10": "URL изображения для photo слайда 9"
  }
}
```

### **Как это работает:**

1. **Main слайд** использует:
   - `dyno.propertyimage` - главное изображение недвижимости
   - `dyno.agentheadshot` - фото агента
   - `dyno.logo` - логотип
   - Все текстовые поля

2. **Photo слайды** используют:
   - **Photo слайд 1**: `dyno.propertyimage2` + все остальные поля
   - **Photo слайд 2**: `dyno.propertyimage3` + все остальные поля
   - **Photo слайд 3**: `dyno.propertyimage4` + все остальные поля
   - И так далее...

### **Пример для 5 слайдов:**
```json
{
  "name": "Luxury House Carousel",
  "main_template_name": "Main Template",
  "photo_template_name": "Photo Template",
  "replacements": {
    "dyno.agentName": "John Smith",
    "dyno.agentheadshot": "https://example.com/agent.jpg",
    "dyno.logo": "https://example.com/logo.png",
    "dyno.propertyimage": "https://example.com/main.jpg",
    "dyno.propertyimage2": "https://example.com/photo1.jpg",
    "dyno.propertyimage3": "https://example.com/photo2.jpg",
    "dyno.propertyimage4": "https://example.com/photo3.jpg",
    "dyno.propertyimage5": "https://example.com/photo4.jpg"
  }
}
```

**Результат:**
- 1 main слайд + 4 photo слайда = 5 слайдов всего
- Каждый photo слайд показывает свое изображение
- Все остальные данные (агент, лого, текст) одинаковые на всех слайдах

## 🔧 Получение списка шаблонов

### **API Endpoint:**
```
GET /api/templates/all-previews
```

### **Ответ:**
```json
{
  "templates": [
    {
      "id": "uuid-123",
      "name": "Main Template",
      "category": "open-house",
      "template_role": "main",
      "preview_url": "/output/previews/uuid-123_preview.png",
      "created_at": "2025-08-11T14:30:00"
    }
  ],
  "total": 1
}
```

## 📱 JavaScript пример:

```javascript
// Генерация карусели
async function generateCarousel(templateNames, data) {
  const response = await fetch('/api/carousel/create-and-generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'My Carousel',
      main_template_name: templateNames.main,
      photo_template_name: templateNames.photo,
      replacements: data
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log('Карусель создана:', result.carousel_id);
    console.log('Слайды:', result.images);
  }
}

// Использование
const carouselData = {
  'dyno.agentName': 'John Smith',
  'dyno.propertyimage': 'https://example.com/main.jpg',
  'dyno.propertyimage2': 'https://example.com/photo1.jpg',
  'dyno.propertyimage3': 'https://example.com/photo2.jpg'
};

generateCarousel({
  main: 'Main Template',
  photo: 'Photo Template'
}, carouselData);
```

## 🎯 Ключевые моменты:

1. **Передавайте все поля** которые нужны на слайдах
2. **Используйте правильные названия** для изображений: `propertyimage2`, `propertyimage3`, etc.
3. **Количество слайдов** определяется по наличию `propertyimage2`, `propertyimage3`, etc.
4. **Все остальные поля** (агент, лого, текст) копируются на все слайды
5. **Превью генерируются автоматически** при запросе списка шаблонов