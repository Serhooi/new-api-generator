# 🖼️ СИСТЕМА ПРЕВЬЮ SVG ШАБЛОНОВ

## 🎯 Обзор

Система автоматически генерирует PNG превью для всех загруженных SVG шаблонов, чтобы пользователи могли видеть как выглядит шаблон перед использованием.

## 🔧 Как это работает

### 1. **Автоматическая генерация при загрузке**
- При загрузке SVG шаблона автоматически создается PNG превью
- Dyno поля заменяются на примеры данных
- Превью сохраняется в `/output/previews/{template_id}_preview.png`

### 2. **Примеры данных для превью**
```python
preview_data = {
    'dyno.agentName': 'John Smith',
    'dyno.propertyAddress': '123 Main Street, Beverly Hills, CA 90210',
    'dyno.price': '$450,000',
    'dyno.bedrooms': '3',
    'dyno.bathrooms': '2',
    'dyno.sqft': '1,850',
    'dyno.agentPhone': '(555) 123-4567',
    'dyno.agentEmail': 'john@realty.com',
    'dyno.agentPhoto': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
    'dyno.propertyImage': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa',
    'dyno.propertyimage2': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be',
    # ... до dyno.propertyimage10
}
```

## 🚀 API Endpoints

### 1. Получение всех шаблонов с превью
**GET** `/api/templates/all-previews`

#### Ответ:
```json
{
  "templates": [
    {
      "id": "uuid-123",
      "name": "Open House Main",
      "category": "open-house",
      "template_role": "main",
      "created_at": "2025-01-24 10:30:00",
      "preview_url": "/output/previews/uuid-123_preview.png",
      "preview_api_url": "/api/templates/uuid-123/preview"
    }
  ],
  "total": 1
}
```

### 2. Получение превью конкретного шаблона
**GET** `/api/templates/{template_id}/preview`

- Возвращает PNG изображение (Content-Type: image/png)
- Если превью не существует, генерирует его автоматически
- Fallback на SVG если PNG генерация не удалась

### 3. Загрузка шаблона с автоматическим превью
**POST** `/api/upload-single`

#### Ответ включает информацию о превью:
```json
{
  "success": true,
  "template_id": "uuid-123",
  "preview_url": "/output/previews/uuid-123_preview.png",
  "preview_filename": "uuid-123_preview.png",
  "message": "Шаблон успешно загружен"
}
```

## 💻 Frontend Integration

### React компонент для выбора шаблонов:
```typescript
import { TemplateSelector } from './agentflow-integration';

const MyComponent = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<Template>();

  return (
    <TemplateSelector
      templateRole="main"
      selectedTemplate={selectedTemplate}
      onTemplateSelect={setSelectedTemplate}
    />
  );
};
```

### Отображение превью:
```jsx
<img
  src={template.preview_url}
  alt={`Превью ${template.name}`}
  className="w-full h-32 object-cover"
  onError={(e) => {
    // Fallback на API URL если прямая ссылка не работает
    const target = e.target as HTMLImageElement;
    if (target.src !== template.preview_api_url) {
      target.src = template.preview_api_url;
    }
  }}
/>
```

## 📁 Структура файлов

```
output/
├── previews/
│   ├── {template_id}_preview.png
│   ├── {template_id}_preview.png
│   └── ...
├── carousel/
│   └── {carousel_id}/
└── single/
```

## 🎨 Настройки генерации

### Размеры превью:
- **Ширина:** 400px
- **Высота:** 300px (автоматически)
- **Фон:** Белый
- **Формат:** PNG

### Качество:
- Высокое разрешение для четкого отображения
- Оптимизировано для веб-отображения
- Быстрая загрузка

## 🔄 Автоматические функции

### 1. **Ленивая генерация**
- Превью генерируется только при необходимости
- Кэшируется для повторного использования
- Автоматическая регенерация при обновлении шаблона

### 2. **Fallback система**
- PNG превью (приоритет)
- SVG с примерами данных (fallback)
- Обработка ошибок загрузки

### 3. **Оптимизация**
- Превью генерируется асинхронно
- Не блокирует основные операции
- Кэширование результатов

## 🧪 Тестирование

### Проверка генерации превью:
```python
# Загрузите SVG шаблон
response = requests.post('/api/upload-single', files={'svg_file': svg_file})

# Проверьте что превью создано
assert 'preview_url' in response.json()

# Получите превью
preview_response = requests.get(response.json()['preview_url'])
assert preview_response.status_code == 200
assert preview_response.headers['Content-Type'] == 'image/png'
```

## ✅ Преимущества системы превью

### Для пользователей:
- **Визуальный выбор** - видят как выглядит шаблон
- **Быстрое сравнение** - могут сравнить разные шаблоны
- **Уверенность в выборе** - знают что получат

### Для разработчиков:
- **Автоматизация** - превью создаются автоматически
- **Кэширование** - быстрая загрузка повторных запросов
- **Fallback** - система работает даже при ошибках

### Для системы:
- **Производительность** - PNG загружается быстрее SVG
- **Совместимость** - PNG поддерживается везде
- **Масштабируемость** - легко добавить новые размеры

## 🎯 Готово к использованию!

Теперь при загрузке SVG шаблонов автоматически создаются красивые превью, которые пользователи могут видеть при выборе шаблонов на фронтенде!