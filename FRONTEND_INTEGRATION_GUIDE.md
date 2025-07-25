# 🚀 ИНСТРУКЦИИ ДЛЯ ФРОНТЕНД РАЗРАБОТЧИКА

## 📋 Что изменилось в API

### ✅ **НОВЫЕ ENDPOINTS (готовы к использованию):**

1. **`POST /api/carousel/create-and-generate`** - РЕАЛИЗОВАН! ✅
   - Создает полноценную карусель с множественными фото
   - Поддерживает до 9 фото слайдов
   - Автоматически добавляет поля `dyno.propertyimage2`, `dyno.propertyimage3`, etc.

2. **`GET /api/carousel/{carousel_id}/slides`** - НОВЫЙ ✅
   - Получение информации о слайдах карусели
   - Статус генерации и URL готовых слайдов

3. **`GET /api/templates/all-previews`** - ОБНОВЛЕН ✅
   - Теперь включает `preview_url` для каждого шаблона
   - PNG превью генерируются автоматически

4. **`GET /api/templates/{template_id}/preview`** - НОВЫЙ ✅
   - Возвращает PNG превью конкретного шаблона
   - Автоматическая генерация если превью нет

### 🔧 **ОБНОВЛЕННЫЕ ENDPOINTS:**

- **`POST /api/upload-single`** - теперь возвращает `preview_url`
- **`POST /api/upload-carousel`** - теперь возвращает `main_preview_url` и `photo_preview_url`

## 🎯 Основные изменения для фронтенда

### 1. **Полноценная карусель (до 10 слайдов)**

**Старый способ (2 слайда):**
```javascript
// СТАРЫЙ - только main + 1 photo
const carouselData = {
  main_template_id: "uuid-main",
  photo_template_id: "uuid-photo", 
  replacements: { ... }
}

fetch('/api/generate/carousel', {
  method: 'POST',
  body: JSON.stringify(carouselData)
})
```

**НОВЫЙ способ (до 10 слайдов):**
```javascript
// НОВЫЙ - main + до 9 фото слайдов
const carouselData = {
  name: "Property Carousel for 123 Main St",
  slides: [
    // Main слайд
    {
      templateId: "open-house-main",
      replacements: {
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
      imagePath: "https://example.com/exterior.jpg"
    },
    // Фото слайды (до 9 штук)
    {
      templateId: "open-house-photo",
      replacements: {
        "dyno.propertyimage2": "https://example.com/living-room.jpg"
      },
      imagePath: "https://example.com/living-room.jpg"
    },
    {
      templateId: "open-house-photo",
      replacements: {
        "dyno.propertyimage3": "https://example.com/kitchen.jpg"
      },
      imagePath: "https://example.com/kitchen.jpg"
    }
    // ... до 9 фото слайдов
  ]
}

// ИСПОЛЬЗУЙТЕ ЭТОТ ENDPOINT:
fetch('/api/carousel/create-and-generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(carouselData)
})
```

### 2. **Система превью шаблонов**

**Получение шаблонов с превью:**
```javascript
// Получить все шаблоны с превью
const response = await fetch('/api/templates/all-previews');
const data = await response.json();

data.templates.forEach(template => {
  console.log(template.name);
  console.log(template.preview_url); // PNG превью!
  
  // Отобразить превью:
  const img = document.createElement('img');
  img.src = template.preview_url;
  img.alt = `Превью ${template.name}`;
  img.onerror = () => {
    // Fallback на API URL
    img.src = template.preview_api_url;
  };
});
```

### 3. **Поля для множественных фото**

**ВАЖНО! Используйте эти поля:**
- `dyno.propertyimage2` - 2-е фото
- `dyno.propertyimage3` - 3-е фото
- `dyno.propertyimage4` - 4-е фото
- `dyno.propertyimage5` - 5-е фото
- `dyno.propertyimage6` - 6-е фото
- `dyno.propertyimage7` - 7-е фото
- `dyno.propertyimage8` - 8-е фото
- `dyno.propertyimage9` - 9-е фото
- `dyno.propertyimage10` - 10-е фото

## 📝 Готовый TypeScript код

### Скопируйте этот код в ваш проект:

```typescript
// Типы данных
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
  'dyno.companyLogo'?: string;
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

interface Template {
  id: string;
  name: string;
  category: string;
  template_role: 'main' | 'photo';
  created_at: string;
  preview_url: string;
  preview_api_url: string;
}

interface SlideRequest {
  templateId: string;
  replacements: DynoReplacements;
  imagePath: string;
}

interface CarouselRequest {
  name: string;
  slides: SlideRequest[];
}

// API клиент
class SVGTemplateAPI {
  private baseUrl: string;

  constructor(baseUrl: string = 'https://your-api.onrender.com') {
    this.baseUrl = baseUrl;
  }

  // Получение всех шаблонов с превью
  async getTemplates(): Promise<Template[]> {
    const response = await fetch(`${this.baseUrl}/api/templates/all-previews`);
    const data = await response.json();
    return data.templates;
  }

  // Создание полноценной карусели
  async createCarousel(request: CarouselRequest) {
    const response = await fetch(`${this.baseUrl}/api/carousel/create-and-generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return await response.json();
  }

  // Получение статуса карусели
  async getCarouselStatus(carouselId: string) {
    const response = await fetch(`${this.baseUrl}/api/carousel/${carouselId}/slides`);
    return await response.json();
  }
}

// Вспомогательная функция для создания карусели
function createPropertyCarousel(
  propertyData: {
    agentName: string;
    propertyAddress: string;
    price: string;
    bedrooms: string;
    bathrooms: string;
    sqft: string;
    agentPhone: string;
    agentEmail: string;
    agentPhoto?: string;
  },
  propertyPhotos: string[], // До 9 фотографий
  mainTemplateId: string,
  photoTemplateId: string
): CarouselRequest {
  
  const limitedPhotos = propertyPhotos.slice(0, 9);
  
  return {
    name: `Property Carousel for ${propertyData.propertyAddress}`,
    slides: [
      // Main слайд
      {
        templateId: mainTemplateId,
        replacements: {
          'dyno.agentName': propertyData.agentName,
          'dyno.propertyAddress': propertyData.propertyAddress,
          'dyno.price': propertyData.price,
          'dyno.bedrooms': propertyData.bedrooms,
          'dyno.bathrooms': propertyData.bathrooms,
          'dyno.sqft': propertyData.sqft,
          'dyno.agentPhone': propertyData.agentPhone,
          'dyno.agentEmail': propertyData.agentEmail,
          'dyno.agentPhoto': propertyData.agentPhoto
        },
        imagePath: limitedPhotos[0] || ""
      },
      // Фото слайды
      ...limitedPhotos.map((photoUrl, index) => ({
        templateId: photoTemplateId,
        replacements: {
          [`dyno.propertyimage${index + 2}`]: photoUrl
        } as DynoReplacements,
        imagePath: photoUrl
      }))
    ]
  };
}
```

## 🎯 Пример использования

```typescript
// Инициализация API
const api = new SVGTemplateAPI('https://your-api.onrender.com');

// 1. Получить шаблоны с превью
const templates = await api.getTemplates();
console.log('Доступные шаблоны:', templates);

// 2. Найти нужные шаблоны
const mainTemplate = templates.find(t => t.template_role === 'main');
const photoTemplate = templates.find(t => t.template_role === 'photo');

// 3. Подготовить данные
const propertyData = {
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

// 4. Создать карусель
const carouselRequest = createPropertyCarousel(
  propertyData,
  propertyPhotos,
  mainTemplate.id,
  photoTemplate.id
);

// 5. Отправить запрос
const result = await api.createCarousel(carouselRequest);
console.log('Карусель создана:', result);

// 6. Получить готовые слайды
if (result.success) {
  const carouselInfo = await api.getCarouselStatus(result.carousel_id);
  console.log('Слайды готовы:', carouselInfo.slides);
  
  // Отобразить слайды
  carouselInfo.slides.forEach(slide => {
    if (slide.image_url) {
      const img = document.createElement('img');
      img.src = slide.image_url;
      img.alt = `Slide ${slide.slide_number}`;
      document.body.appendChild(img);
    }
  });
}
```

## ⚠️ ВАЖНЫЕ ИЗМЕНЕНИЯ

### 1. **Обязательно обновите URL endpoint:**
```javascript
// СТАРЫЙ (не работает)
'/api/generate/carousel'

// НОВЫЙ (работает)
'/api/carousel/create-and-generate'
```

### 2. **Измените структуру данных:**
```javascript
// СТАРЫЙ формат
{
  main_template_id: "uuid",
  photo_template_id: "uuid",
  replacements: { ... }
}

// НОВЫЙ формат
{
  name: "Carousel Name",
  slides: [
    { templateId: "uuid", replacements: { ... }, imagePath: "url" },
    { templateId: "uuid", replacements: { ... }, imagePath: "url" }
  ]
}
```

### 3. **Используйте правильные поля для фото:**
```javascript
// Для каждого фото слайда используйте соответствующее поле:
{
  templateId: "photo-template-id",
  replacements: {
    "dyno.propertyimage2": "https://photo2.jpg"  // Для 2-го слайда
  },
  imagePath: "https://photo2.jpg"
}

{
  templateId: "photo-template-id", 
  replacements: {
    "dyno.propertyimage3": "https://photo3.jpg"  // Для 3-го слайда
  },
  imagePath: "https://photo3.jpg"
}
```

## 🎉 Готово!

Теперь ваш фронтенд может:
- ✅ Создавать карусели с до 9 фото слайдов
- ✅ Показывать превью шаблонов пользователям
- ✅ Использовать правильные API endpoints
- ✅ Получать готовые URL слайдов

Если есть вопросы - пишите! 🚀