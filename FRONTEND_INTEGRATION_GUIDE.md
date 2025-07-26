# 🎯 РУКОВОДСТВО ПО ИНТЕГРАЦИИ ДЛЯ ФРОНТЕНДА

## 📋 Обновление API: SVG → JPG URLs

**ВАЖНО:** API теперь возвращает JPG URL вместо SVG URL для отображения изображений в `<img>` тегах.

## 🚀 Основные изменения

### ❌ Было (проблема):
```json
{
  "images": [
    "/output/carousel/carousel_xxx_main.svg",
    "/output/carousel/carousel_xxx_photo.svg"
  ]
}
```
**Проблема:** SVG файлы не отображаются в `<img>` тегах, вызывают ошибку "Failed to load slide"

### ✅ Стало (решение):
```json
{
  "images": [
    "/output/carousel/carousel_xxx_main.jpg",
    "/output/carousel/carousel_xxx_photo.jpg"
  ],
  "format": "jpg"
}
```
**Решение:** JPG файлы корректно отображаются в `<img>` тегах

## 📡 API Endpoints

### 1. Генерация карусели (основной)

**Endpoint:** `POST /api/generate/carousel`

**Request:**
```javascript
const response = await fetch('/api/generate/carousel', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    main_template_id: "template-id",
    photo_template_id: "template-id", 
    data: {
      'dyno.agentName': 'John Smith',
      'dyno.propertyAddress': '123 Main Street',
      'dyno.price': '$450,000',
      'dyno.agentPhone': '(555) 123-4567'
    }
  })
});
```

**Response:**
```json
{
  "success": true,
  "carousel_id": "c6aa98a6-8f15-4ba7-ac99-2b0ef35118dc",
  "main_template_name": "Test Main Template",
  "photo_template_name": "Test Photo Template",
  "main_url": "/output/carousel/carousel_xxx_main.jpg",
  "photo_url": "/output/carousel/carousel_xxx_photo.jpg",
  "replacements_applied": 4,
  "images": [
    "/output/carousel/carousel_xxx_main.jpg",
    "/output/carousel/carousel_xxx_photo.jpg"
  ],
  "slides": [
    "/output/carousel/carousel_xxx_main.jpg",
    "/output/carousel/carousel_xxx_photo.jpg"
  ],
  "urls": [
    "/output/carousel/carousel_xxx_main.jpg",
    "/output/carousel/carousel_xxx_photo.jpg"
  ],
  "image_url": "/output/carousel/carousel_xxx_main.jpg",
  "data": {
    "images": [
      "/output/carousel/carousel_xxx_main.jpg",
      "/output/carousel/carousel_xxx_photo.jpg"
    ]
  },
  "slides_count": 2,
  "status": "completed",
  "format": "jpg"
}
```

### 2. Генерация карусели по именам шаблонов

**Endpoint:** `POST /api/generate/carousel-by-name`

**Request:**
```javascript
const response = await fetch('/api/generate/carousel-by-name', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    main_template_name: "template-name",
    photo_template_name: "template-name",
    replacements: {
      'dyno.agentName': 'John Smith',
      'dyno.propertyAddress': '123 Main Street'
    }
  })
});
```

### 3. Создание полноценной карусели (до 10 слайдов)

**Endpoint:** `POST /api/carousel/create-and-generate`

**Request:**
```javascript
const response = await fetch('/api/carousel/create-and-generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: "Property Carousel",
    slides: [
      {
        templateId: "main-template-id",
        replacements: {
          'dyno.agentName': 'John Smith',
          'dyno.propertyAddress': '123 Main Street'
        },
        imagePath: "https://example.com/photo1.jpg"
      },
      {
        templateId: "photo-template-id", 
        replacements: {
          'dyno.propertyimage2': 'https://example.com/photo2.jpg'
        },
        imagePath: "https://example.com/photo2.jpg"
      }
    ]
  })
});
```

**Response:**
```json
{
  "success": true,
  "carousel_id": "xxx-xxx-xxx",
  "slides_count": 2,
  "status": "completed"
}
```

### 4. Получение информации о слайдах карусели

**Endpoint:** `GET /api/carousel/{carousel_id}/slides`

**Request:**
```javascript
const response = await fetch(`/api/carousel/${carouselId}/slides`);
```

**Response:**
```json
{
  "carousel_id": "xxx-xxx-xxx",
  "name": "Property Carousel",
  "status": "completed",
  "slides_count": 2,
  "created_at": "2025-07-26T00:00:00",
  "slides": [
    {
      "slide_number": 1,
      "filename": "slide_01.jpg",
      "image_url": "/output/carousel/xxx/slide_01.jpg",
      "status": "completed",
      "format": "jpg"
    },
    {
      "slide_number": 2,
      "filename": "slide_02.jpg", 
      "image_url": "/output/carousel/xxx/slide_02.jpg",
      "status": "completed",
      "format": "jpg"
    }
  ]
}
```

## 🎨 Интеграция в React

### React Hook для генерации карусели:

```typescript
import { useState, useCallback } from 'react';

interface CarouselData {
  carousel_id: string;
  images: string[];
  format: 'jpg' | 'svg';
  status: string;
}

interface CarouselRequest {
  main_template_id: string;
  photo_template_id: string;
  data: Record<string, string>;
}

export const useCarouselGeneration = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [carouselData, setCarouselData] = useState<CarouselData | null>(null);

  const generateCarousel = useCallback(async (request: CarouselRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate/carousel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

  return {
    isLoading,
    error,
    carouselData,
    generateCarousel
  };
};
```

### React компонент для отображения карусели:

```typescript
import React from 'react';
import { useCarouselGeneration } from './useCarouselGeneration';

interface CarouselProps {
  mainTemplateId: string;
  photoTemplateId: string;
  replacements: Record<string, string>;
}

export const CarouselGenerator: React.FC<CarouselProps> = ({
  mainTemplateId,
  photoTemplateId,
  replacements
}) => {
  const { isLoading, error, carouselData, generateCarousel } = useCarouselGeneration();

  const handleGenerate = async () => {
    await generateCarousel({
      main_template_id: mainTemplateId,
      photo_template_id: photoTemplateId,
      data: replacements
    });
  };

  return (
    <div className="carousel-generator">
      <button 
        onClick={handleGenerate}
        disabled={isLoading}
        className="generate-btn"
      >
        {isLoading ? 'Генерируем...' : 'Сгенерировать карусель'}
      </button>

      {error && (
        <div className="error">
          Ошибка: {error}
        </div>
      )}

      {carouselData && (
        <div className="carousel-images">
          <h3>Сгенерированные изображения:</h3>
          <div className="images-grid">
            {carouselData.images.map((imageUrl, index) => (
              <div key={index} className="image-container">
                <img 
                  src={imageUrl}
                  alt={`Slide ${index + 1}`}
                  className="carousel-image"
                  onError={(e) => {
                    console.error('Failed to load image:', imageUrl);
                    e.currentTarget.style.display = 'none';
                  }}
                />
                <div className="image-info">
                  Формат: {carouselData.format}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🎨 Интеграция в Vue.js

### Vue Composition API:

```typescript
import { ref, reactive } from 'vue';

interface CarouselData {
  carousel_id: string;
  images: string[];
  format: 'jpg' | 'svg';
  status: string;
}

export const useCarouselGeneration = () => {
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const carouselData = ref<CarouselData | null>(null);

  const generateCarousel = async (request: {
    main_template_id: string;
    photo_template_id: string;
    data: Record<string, string>;
  }) => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await fetch('/api/generate/carousel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

  return {
    isLoading,
    error,
    carouselData,
    generateCarousel
  };
};
```

### Vue компонент:

```vue
<template>
  <div class="carousel-generator">
    <button 
      @click="handleGenerate"
      :disabled="isLoading"
      class="generate-btn"
    >
      {{ isLoading ? 'Генерируем...' : 'Сгенерировать карусель' }}
    </button>

    <div v-if="error" class="error">
      Ошибка: {{ error }}
    </div>

    <div v-if="carouselData" class="carousel-images">
      <h3>Сгенерированные изображения:</h3>
      <div class="images-grid">
        <div 
          v-for="(imageUrl, index) in carouselData.images" 
          :key="index"
          class="image-container"
        >
          <img 
            :src="imageUrl"
            :alt="`Slide ${index + 1}`"
            class="carousel-image"
            @error="handleImageError"
          />
          <div class="image-info">
            Формат: {{ carouselData.format }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCarouselGeneration } from './useCarouselGeneration';

const props = defineProps<{
  mainTemplateId: string;
  photoTemplateId: string;
  replacements: Record<string, string>;
}>();

const { isLoading, error, carouselData, generateCarousel } = useCarouselGeneration();

const handleGenerate = async () => {
  await generateCarousel({
    main_template_id: props.mainTemplateId,
    photo_template_id: props.photoTemplateId,
    data: props.replacements
  });
};

const handleImageError = (event: Event) => {
  console.error('Failed to load image:', (event.target as HTMLImageElement).src);
  (event.target as HTMLImageElement).style.display = 'none';
};
</script>
```

## 🎨 Интеграция в Vanilla JavaScript

### Простая интеграция:

```javascript
class CarouselGenerator {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  async generateCarousel(request) {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate/carousel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      });

      const data = await response.json();
      
      if (data.success) {
        return data;
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Carousel generation error:', error);
      throw error;
    }
  }

  displayImages(images, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    
    images.forEach((imageUrl, index) => {
      const imgDiv = document.createElement('div');
      imgDiv.className = 'image-container';
      
      const img = document.createElement('img');
      img.src = imageUrl;
      img.alt = `Slide ${index + 1}`;
      img.className = 'carousel-image';
      
      img.onerror = () => {
        console.error('Failed to load image:', imageUrl);
        img.style.display = 'none';
      };
      
      imgDiv.appendChild(img);
      container.appendChild(imgDiv);
    });
  }
}

// Использование:
const generator = new CarouselGenerator();

const request = {
  main_template_id: "template-id",
  photo_template_id: "template-id",
  data: {
    'dyno.agentName': 'John Smith',
    'dyno.propertyAddress': '123 Main Street',
    'dyno.price': '$450,000'
  }
};

try {
  const result = await generator.generateCarousel(request);
  generator.displayImages(result.images, 'carousel-container');
} catch (error) {
  console.error('Error:', error);
}
```

## 🔄 Fallback механизм

Если конвертация в JPG не удалась, API возвращает SVG URL с `"format": "svg"`:

```json
{
  "images": [
    "/output/carousel/carousel_xxx_main.svg",
    "/output/carousel/carousel_xxx_photo.svg"
  ],
  "format": "svg"
}
```

В этом случае фронтенд может:

1. **Использовать `<object>` для SVG:**
```html
<object data="/output/carousel/carousel_xxx_main.svg" type="image/svg+xml">
  <img src="fallback-image.jpg" alt="Fallback">
</object>
```

2. **Или использовать `<embed>`:**
```html
<embed src="/output/carousel/carousel_xxx_main.svg" type="image/svg+xml">
```

## 🎯 Ключевые моменты

1. **Все URL теперь JPG** - готовы для использования в `<img>` тегах
2. **Поле `format`** указывает тип файла (`"jpg"` или `"svg"`)
3. **Fallback механизм** - если JPG не удался, возвращается SVG
4. **Обратная совместимость** - старый код продолжит работать
5. **Высокое качество** - JPG генерируются с DPI 300

## ✅ Тестирование

Для тестирования API используйте:

```bash
curl -X POST http://localhost:5000/api/generate/carousel \
  -H "Content-Type: application/json" \
  -d '{
    "main_template_id": "test-main-template",
    "photo_template_id": "test-photo-template", 
    "data": {
      "dyno.agentName": "John Smith",
      "dyno.propertyAddress": "123 Main Street",
      "dyno.price": "$450,000"
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

Теперь фронтенд может корректно отображать изображения без ошибок "Failed to load slide"! 🎉