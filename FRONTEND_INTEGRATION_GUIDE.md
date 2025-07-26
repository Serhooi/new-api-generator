# 🌐 РУКОВОДСТВО ПО ИНТЕГРАЦИИ С ФРОНТЕНДОМ

## 🎯 Быстрый старт

### **1. Получение списка шаблонов с превью:**
```javascript
const response = await fetch('/api/templates/all-previews');
const data = await response.json();

// data.templates содержит массив шаблонов с превью
data.templates.forEach(template => {
  console.log(template.name, template.preview_url);
});
```

### **2. Отображение превью:**
```html
<img src="/output/template_previews/template_uuid_preview.png" 
     alt="Template Preview"
     onerror="this.src='/fallback-preview.png'">
```

## 📡 API Endpoints

### **GET `/api/templates/all-previews`**
Возвращает все шаблоны с URL превью

**Ответ:**
```json
{
  "templates": [
    {
      "id": "uuid-123",
      "name": "Modern Open House",
      "category": "open-house", 
      "template_role": "main",
      "preview_url": "/output/template_previews/template_uuid-123_preview.png",
      "preview_type": "manual"
    }
  ],
  "total": 1
}
```

**Типы превью:**
- `manual` - загружено вручную (лучшее качество)
- `default` - создано автоматически с названием шаблона
- `auto` - старая система автоматической генерации

## 🖼️ Работа с превью

### **Рекомендуемый HTML:**
```html
<div class="template-card">
  <img src="${template.preview_url}" 
       alt="${template.name}"
       class="template-preview"
       loading="lazy"
       onerror="handleImageError(this, '${template.id}')">
  
  <h3>${template.name}</h3>
  <p>${template.category}</p>
  
  <span class="preview-badge ${template.preview_type}">
    ${template.preview_type === 'manual' ? '✅ Ручное' : '🔄 Авто'}
  </span>
</div>
```

### **Обработка ошибок загрузки:**
```javascript
function handleImageError(img, templateId) {
  // Fallback на placeholder
  img.src = '/assets/template-placeholder.png';
  img.alt = 'Preview not available';
}
```

## 🎨 CSS стили

### **Базовые стили:**
```css
.template-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #eee;
  background: #f8f9fa;
}

.preview-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
}

.preview-badge.manual {
  background: #d4edda;
  color: #155724;
}

.preview-badge.default {
  background: #f8d7da; 
  color: #721c24;
}
```

## 🚀 React компонент

### **Хук для загрузки шаблонов:**
```jsx
import { useState, useEffect } from 'react';

function useTemplates() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/templates/all-previews')
      .then(res => res.json())
      .then(data => {
        setTemplates(data.templates || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return { templates, loading, error };
}
```

### **Компонент выбора шаблона:**
```jsx
function TemplateSelector({ onSelect }) {
  const { templates, loading, error } = useTemplates();
  const [selected, setSelected] = useState(null);

  if (loading) return <div>⏳ Загружаю шаблоны...</div>;
  if (error) return <div>❌ Ошибка: {error}</div>;

  return (
    <div className="template-grid">
      {templates.map(template => (
        <div 
          key={template.id}
          className={`template-card ${selected === template.id ? 'selected' : ''}`}
          onClick={() => {
            setSelected(template.id);
            onSelect?.(template);
          }}
        >
          <img 
            src={template.preview_url}
            alt={template.name}
            className="template-preview"
            onError={(e) => {
              e.target.src = '/assets/template-placeholder.png';
            }}
          />
          
          <h3>{template.name}</h3>
          <p>{template.category}</p>
          
          <span className={`preview-badge ${template.preview_type}`}>
            {template.preview_type === 'manual' ? '✅ Ручное' : '🔄 Авто'}
          </span>
        </div>
      ))}
    </div>
  );
}
```

## 📱 Мобильная адаптация

### **Responsive CSS:**
```css
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  .template-preview {
    height: 150px;
  }
}

@media (max-width: 480px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
}
```

## ⚡ Оптимизация производительности

### **Lazy loading:**
```html
<img src="${template.preview_url}" 
     loading="lazy"
     decoding="async">
```

### **Preload критичных превью:**
```html
<link rel="preload" as="image" href="/output/template_previews/popular_template.png">
```

### **Кэширование:**
```javascript
// Service Worker для кэширования превью
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/output/template_previews/')) {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request);
      })
    );
  }
});
```

## 🔄 Обновление превью

### **Автоматическое обновление:**
```javascript
// Проверяем обновления каждые 30 секунд
setInterval(async () => {
  const response = await fetch('/api/templates/all-previews');
  const data = await response.json();
  
  if (data.templates.length !== currentTemplates.length) {
    updateTemplatesList(data.templates);
  }
}, 30000);
```

## 🧪 Тестирование

### **Файлы для тестирования:**
- `frontend_example.html` - полный пример интеграции
- `test_manual_preview.html` - тестирование системы превью

### **Как протестировать:**
1. Откройте `frontend_example.html` в браузере
2. Проверьте что превью загружаются
3. Попробуйте выбрать разные шаблоны
4. Проверьте работу на мобильных устройствах

## ✅ Чек-лист интеграции

- [ ] API endpoint `/api/templates/all-previews` работает
- [ ] Превью изображения отображаются корректно
- [ ] Обработка ошибок загрузки изображений
- [ ] Мобильная адаптация
- [ ] Индикаторы типа превью (ручное/авто)
- [ ] Выбор шаблона работает
- [ ] Fallback на placeholder изображения
- [ ] Lazy loading для оптимизации
- [ ] Кэширование превью

## 🎯 Итог

**Превью система полностью готова для интеграции с фронтендом!**

1. **📡 Простой API** - один endpoint возвращает все превью
2. **🖼️ Готовые изображения** - мгновенная загрузка
3. **🔄 Fallback система** - всегда есть превью
4. **📱 Адаптивность** - работает на всех устройствах
5. **⚡ Оптимизация** - lazy loading и кэширование

**Пользователи увидят красивые превью и смогут легко выбрать нужный шаблон!** 🎉