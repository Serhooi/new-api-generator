# 🖼️ СИСТЕМА ПРЕВЬЮ SVG ШАБЛОНОВ

## 📋 Обзор

Система превью позволяет пользователям видеть как будет выглядеть флаер с их данными **перед финальной генерацией**. Это критически важно для UX - пользователь может проверить правильность данных, позиционирование изображений и общий вид.

## 🎯 Основные возможности

### 1. **Превью шаблонов без данных**
- Просмотр "пустых" шаблонов
- Быстрая оценка дизайна
- Выбор подходящего шаблона

### 2. **Превью с заполненными данными**
- Замена всех `dyno.*` полей реальными данными
- Загрузка изображений (headshot, property photos)
- Проверка позиционирования и масштабирования

### 3. **Превью карусели**
- Одновременный просмотр main + photo слайдов
- Проверка согласованности дизайна
- Валидация всех данных

### 4. **Разные форматы превью**
- **PNG файлы** - для скачивания и сохранения
- **Base64** - для встраивания в HTML
- **Thumbnails** - маленькие превью для списков

## 🔧 API Endpoints

### `GET /api/preview/template/<template_id>`
Генерирует превью шаблона без данных

**Параметры query string:**
- `type` - тип превью (`png`, `base64`, `thumbnail`)
- `width` - ширина в пикселях (по умолчанию 400)
- `height` - высота в пикселях (по умолчанию 300)

**Пример запроса:**
```
GET /api/preview/template/uuid-123?type=png&width=500&height=400
```

**Ответ:**
```json
{
  "success": true,
  "template_name": "Modern Open House",
  "template_id": "uuid-123",
  "preview_id": "uuid-456",
  "filename": "preview_uuid-456.png",
  "url": "/output/previews/preview_uuid-456.png",
  "width": 500,
  "height": 400,
  "file_size": 45678,
  "format": "png"
}
```

### `POST /api/preview/with-data`
Генерирует превью шаблона с заполненными данными

**Тело запроса:**
```json
{
  "template_id": "uuid-123",
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
    "dyno.propertyImage": "https://example.com/property.jpg"
  },
  "type": "png",
  "width": 400,
  "height": 300
}
```

**Ответ:**
```json
{
  "success": true,
  "template_name": "Modern Open House",
  "template_id": "uuid-123",
  "preview_id": "uuid-789",
  "url": "/output/previews/preview_uuid-789.png",
  "width": 400,
  "height": 300,
  "replacements_count": 10,
  "has_data": true,
  "format": "png"
}
```

### `POST /api/preview/carousel`
Генерирует превью карусели (main + photo)

**Тело запроса:**
```json
{
  "main_template_id": "uuid-main",
  "photo_template_id": "uuid-photo",
  "replacements": {
    "dyno.agentName": "John Smith",
    "dyno.propertyImage": "https://example.com/property.jpg"
  },
  "type": "png"
}
```

**Ответ:**
```json
{
  "success": true,
  "main_preview": {
    "template_name": "Main Template",
    "template_id": "uuid-main",
    "url": "/output/previews/preview_main.png",
    "width": 400,
    "height": 300
  },
  "photo_preview": {
    "template_name": "Photo Template", 
    "template_id": "uuid-photo",
    "url": "/output/previews/preview_photo.png",
    "width": 400,
    "height": 300
  }
}
```

### `POST /api/preview/cleanup`
Очищает старые превью файлы

**Тело запроса:**
```json
{
  "max_age_hours": 24
}
```

## 🌐 Веб-интерфейс

### Страница превью: `/preview`

**Функции:**
1. **Выбор шаблона** - отображает все доступные шаблоны
2. **Заполнение данных** - форма для ввода данных недвижимости и агента
3. **Генерация превью** - создание превью с выбранными данными
4. **Отображение результатов** - показ сгенерированных превью

**Поля формы:**
- Имя агента
- Адрес недвижимости (с автоматическим переносом)
- Цена
- Количество спален/ванных
- Площадь
- Контакты агента
- URL фото агента (headshot)
- URL фото недвижимости

## 🔧 Техническая реализация

### Основные компоненты:

1. **`preview_system.py`** - основная логика генерации превью
2. **API endpoints в `app.py`** - REST API для фронтенда
3. **`templates/preview.html`** - веб-интерфейс
4. **Директория `output/previews/`** - хранение сгенерированных файлов

### Процесс генерации превью:

```python
# 1. Получение шаблона из БД
template = get_template_by_id(template_id)

# 2. Обработка SVG с заменой dyno полей
processed_svg = process_svg_font_perfect(template.svg_content, replacements)

# 3. Конвертация SVG в PNG через cairosvg
png_data = cairosvg.svg2png(
    bytestring=processed_svg.encode('utf-8'),
    output_width=width,
    output_height=height,
    background_color='white'
)

# 4. Сохранение файла и возврат URL
save_preview_file(png_data, preview_id)
return preview_url
```

### Оптимизации:

1. **Автоматическая очистка** старых превью файлов
2. **Кэширование** для повторных запросов
3. **Оптимизация размера** thumbnail изображений
4. **Валидация SVG** перед обработкой

## 📱 Интеграция с фронтендом

### JavaScript пример:

```javascript
// Генерация превью с данными
async function generatePreview(templateId, data) {
  const response = await fetch('/api/preview/with-data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      template_id: templateId,
      replacements: data,
      type: 'png',
      width: 400,
      height: 300
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    // Отображаем превью
    const img = document.createElement('img');
    img.src = result.url;
    document.getElementById('preview-container').appendChild(img);
  }
}
```

### React Hook пример:

```typescript
const usePreviewGeneration = () => {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const generatePreview = async (templateId: string, data: any) => {
    setLoading(true);
    try {
      const response = await fetch('/api/preview/with-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: templateId,
          replacements: data,
          type: 'png'
        })
      });
      
      const result = await response.json();
      setPreview(result);
    } finally {
      setLoading(false);
    }
  };
  
  return { preview, loading, generatePreview };
};
```

## 🎯 Преимущества системы превью

### Для пользователей:
1. **Мгновенная обратная связь** - видят результат до генерации
2. **Проверка данных** - могут исправить ошибки заранее
3. **Выбор лучшего шаблона** - сравнение разных вариантов
4. **Контроль качества** - проверка позиционирования изображений

### Для разработчиков:
1. **Снижение нагрузки** - меньше повторных генераций
2. **Лучший UX** - пользователи довольны результатом
3. **Отладка** - легче найти проблемы в шаблонах
4. **Тестирование** - быстрая проверка изменений

## 🔄 Workflow использования

```
1. Пользователь заходит на /preview
2. Выбирает шаблон из списка
3. Заполняет данные в форме
4. Нажимает "Создать превью"
5. Видит результат мгновенно
6. При необходимости корректирует данные
7. Повторяет превью или переходит к финальной генерации
```

## ⚠️ Ограничения и рекомендации

### Ограничения:
- Превью файлы автоматически удаляются через 24 часа
- Максимальный размер превью: 1200x800 пикселей
- Поддерживаются только PNG и Base64 форматы

### Рекомендации:
- Используйте превью перед каждой финальной генерацией
- Проверяйте позиционирование headshot изображений
- Тестируйте с разными длинами адресов
- Очищайте старые превью регулярно

## 🚀 Будущие улучшения

1. **Интерактивное редактирование** - изменение позиции элементов
2. **Пакетное превью** - генерация превью для множественных данных
3. **Сравнение шаблонов** - side-by-side просмотр
4. **Экспорт в разные форматы** - PDF, JPEG, WebP
5. **Предустановленные данные** - шаблоны данных для быстрого тестирования