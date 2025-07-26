# 🚀 БЫСТРЫЙ СТАРТ ДЛЯ ФРОНТЕНДА

## ⚡ Что изменилось

**Проблема решена:** API теперь возвращает JPG URL вместо SVG URL

### ❌ Было:
```json
{
  "images": ["/output/carousel/carousel_xxx_main.svg"]
}
```
**Ошибка:** "Failed to load slide" - SVG не отображается в `<img>`

### ✅ Стало:
```json
{
  "images": ["/output/carousel/carousel_xxx_main.jpg"],
  "format": "jpg"
}
```
**Результат:** JPG корректно отображается в `<img>`

## 🎯 Основной API endpoint

```javascript
// Генерация карусели
const response = await fetch('/api/generate/carousel', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    main_template_id: "template-id",
    photo_template_id: "template-id",
    data: {
      'dyno.agentName': 'John Smith',
      'dyno.propertyAddress': '123 Main Street',
      'dyno.price': '$450,000'
    }
  })
});

const result = await response.json();

// ✅ Теперь это JPG URL!
result.images.forEach(imageUrl => {
  const img = document.createElement('img');
  img.src = imageUrl; // /output/carousel/carousel_xxx_main.jpg
  document.body.appendChild(img);
});
```

## 📡 Все доступные endpoints

1. **`POST /api/generate/carousel`** - Основная генерация
2. **`POST /api/generate/carousel-by-name`** - По именам шаблонов  
3. **`POST /api/carousel/create-and-generate`** - Полная карусель (до 10 слайдов)
4. **`GET /api/carousel/{id}/slides`** - Получение информации о слайдах

## 🎨 React Hook (готовый к использованию)

```typescript
import { useState, useCallback } from 'react';

export const useCarouselGeneration = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [carouselData, setCarouselData] = useState<any>(null);

  const generateCarousel = useCallback(async (request: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate/carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      const data = await response.json();
      
      if (data.success) {
        setCarouselData(data);
      } else {
        setError(data.error || 'Unknown error');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { isLoading, error, carouselData, generateCarousel };
};
```

## 🎨 Vue Composition API

```typescript
import { ref } from 'vue';

export const useCarouselGeneration = () => {
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const carouselData = ref<any>(null);

  const generateCarousel = async (request: any) => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await fetch('/api/generate/carousel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      const data = await response.json();
      
      if (data.success) {
        carouselData.value = data;
      } else {
        error.value = data.error || 'Unknown error';
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Network error';
    } finally {
      isLoading.value = false;
    }
  };

  return { isLoading, error, carouselData, generateCarousel };
};
```

## 🔄 Fallback механизм

Если JPG конвертация не удалась, API вернет SVG:

```json
{
  "images": ["/output/carousel/carousel_xxx_main.svg"],
  "format": "svg"
}
```

Для SVG используйте:
```html
<object data="/output/carousel/carousel_xxx_main.svg" type="image/svg+xml">
  <img src="fallback.jpg" alt="Fallback">
</object>
```

## ✅ Тестирование

```bash
curl -X POST http://localhost:5000/api/generate/carousel \
  -H "Content-Type: application/json" \
  -d '{
    "main_template_id": "test-main-template",
    "photo_template_id": "test-photo-template",
    "data": {
      "dyno.agentName": "John Smith",
      "dyno.propertyAddress": "123 Main Street"
    }
  }'
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "images": [
    "/output/carousel/carousel_xxx_main.jpg",
    "/output/carousel/carousel_xxx_photo.jpg"
  ],
  "format": "jpg"
}
```

## 🎯 Ключевые моменты

1. **Все URL теперь JPG** - готовы для `<img>` тегов
2. **Поле `format`** - указывает тип файла (`"jpg"` или `"svg"`)
3. **Fallback** - если JPG не удался, возвращается SVG
4. **Обратная совместимость** - старый код продолжит работать
5. **Высокое качество** - JPG с DPI 300

## 🚀 Готово к использованию!

Теперь фронтенд может корректно отображать изображения без ошибок "Failed to load slide"! 🎉

**Никаких дополнительных изменений в коде фронтенда не требуется** - просто используйте полученные URL в `<img>` тегах как обычно. 