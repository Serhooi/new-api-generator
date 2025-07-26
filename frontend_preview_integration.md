# 🌐 ИНТЕГРАЦИЯ ПРЕВЬЮ С ФРОНТЕНДОМ

## 🎯 Как фронтенд получает превью

### **API Endpoint для получения шаблонов:**
```
GET /api/templates/all-previews
```

### **Ответ API:**
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
    },
    {
      "id": "uuid-456", 
      "name": "Luxury Listing",
      "category": "for-sale",
      "template_role": "main",
      "preview_url": "/output/template_previews/template_uuid-456_preview.png",
      "preview_type": "default"
    }
  ],
  "total": 2
}
```

## 🖼️ Отображение на фронтенде

### **React компонент:**
```jsx
function TemplateSelector() {
  const [templates, setTemplates] = useState([]);
  
  useEffect(() => {
    fetch('/api/templates/all-previews')
      .then(res => res.json())
      .then(data => setTemplates(data.templates));
  }, []);
  
  return (
    <div className="template-grid">
      {templates.map(template => (
        <div key={template.id} className="template-card">
          {/* 🎯 ПРЕВЬЮ ИЗОБРАЖЕНИЕ */}
          <img 
            src={template.preview_url} 
            alt={template.name}
            className="template-preview"
            onError={(e) => {
              e.target.src = '/fallback-preview.png';
            }}
          />
          
          <h3>{template.name}</h3>
          <p>Категория: {template.category}</p>
          
          {/* Индикатор типа превью */}
          <span className={`preview-badge ${template.preview_type}`}>
            {template.preview_type === 'manual' ? '✅ Ручное' : '🔄 Авто'}
          </span>
          
          <button onClick={() => selectTemplate(template.id)}>
            Выбрать шаблон
          </button>
        </div>
      ))}
    </div>
  );
}
```

### **Vanilla JavaScript:**
```javascript
async function loadTemplates() {
  const response = await fetch('/api/templates/all-previews');
  const data = await response.json();
  
  const container = document.getElementById('templates');
  
  data.templates.forEach(template => {
    const card = document.createElement('div');
    card.className = 'template-card';
    
    card.innerHTML = `
      <img src="${template.preview_url}" 
           alt="${template.name}"
           class="template-preview"
           onerror="this.src='/fallback-preview.png'">
      <h3>${template.name}</h3>
      <p>${template.category}</p>
      <button onclick="selectTemplate('${template.id}')">
        Выбрать
      </button>
    `;
    
    container.appendChild(card);
  });
}
```

## 🔗 URL структура превью

### **Ручные превью (загруженные вами):**
```
/output/template_previews/template_{uuid}_preview.png
```

### **Дефолтные превью (созданные автоматически):**
```
/output/template_previews/template_{uuid}_preview.png
```

### **Старые автоматические превью:**
```
/output/previews/{uuid}_preview.png
```

## 🎨 CSS стили для превью

```css
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.template-card {
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 15px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.template-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #eee;
}

.preview-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
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

## 🚀 Преимущества для фронтенда

### **1. Мгновенная загрузка**
```javascript
// Раньше: ждали генерации
await generatePreview(template); // 2-5 секунд

// Теперь: готовые изображения
<img src="/output/template_previews/template_123.png"> // мгновенно
```

### **2. Лучший UX**
- Пользователь сразу видит как выглядит шаблон
- Нет задержек при выборе шаблонов
- Превью показывает реальный результат с данными
- Можно добавить lazy loading для оптимизации

### **3. Простая интеграция**
```javascript
// Один запрос получает все превью
const templates = await fetch('/api/templates/all-previews');

// Простое отображение
templates.forEach(template => {
  showTemplate(template.name, template.preview_url);
});
```

## 🔄 Fallback стратегия

### **Если превью не загружается:**
```javascript
function handleImageError(img, template) {
  // 1. Пробуем дефолтное превью
  img.src = `/output/template_previews/template_${template.id}_preview.png`;
  
  img.onerror = () => {
    // 2. Пробуем старое автоматическое превью
    img.src = `/output/previews/${template.id}_preview.png`;
    
    img.onerror = () => {
      // 3. Показываем placeholder
      img.src = '/assets/template-placeholder.png';
    };
  };
}
```

## 📱 Адаптивность

### **Responsive превью:**
```css
.template-preview {
  width: 100%;
  height: auto;
  aspect-ratio: 4/3; /* Фиксированное соотношение */
  object-fit: cover;
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
```

## 🎯 Пример полной интеграции

### **HTML:**
```html
<div id="template-selector">
  <h2>Выберите шаблон</h2>
  <div id="templates-grid" class="template-grid">
    <!-- Шаблоны загружаются динамически -->
  </div>
</div>
```

### **JavaScript:**
```javascript
class TemplateSelector {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.selectedTemplate = null;
    this.loadTemplates();
  }
  
  async loadTemplates() {
    try {
      const response = await fetch('/api/templates/all-previews');
      const data = await response.json();
      
      this.renderTemplates(data.templates);
    } catch (error) {
      this.showError('Ошибка загрузки шаблонов');
    }
  }
  
  renderTemplates(templates) {
    this.container.innerHTML = templates.map(template => `
      <div class="template-card ${this.selectedTemplate === template.id ? 'selected' : ''}"
           onclick="templateSelector.selectTemplate('${template.id}')">
        <img src="${template.preview_url}" 
             alt="${template.name}"
             class="template-preview"
             onerror="this.src='/assets/template-placeholder.png'">
        <h3>${template.name}</h3>
        <p class="template-category">${template.category}</p>
        <span class="preview-type ${template.preview_type}">
          ${template.preview_type === 'manual' ? 'Ручное превью' : 'Авто превью'}
        </span>
      </div>
    `).join('');
  }
  
  selectTemplate(templateId) {
    this.selectedTemplate = templateId;
    this.renderTemplates(); // Перерисовываем с выделением
    
    // Уведомляем родительское приложение
    this.onTemplateSelected?.(templateId);
  }
}

// Инициализация
const templateSelector = new TemplateSelector('templates-grid');
templateSelector.onTemplateSelected = (templateId) => {
  console.log('Выбран шаблон:', templateId);
  // Здесь ваша логика обработки выбора
};
```

## ✅ Итог

**Да, превью будет отдаваться на фронт правильно!**

1. **📡 API возвращает готовые URL** превью изображений
2. **🖼️ Фронтенд просто отображает** эти изображения
3. **⚡ Мгновенная загрузка** - нет задержек
4. **🎯 Пользователь видит** точно как выглядит шаблон
5. **🔄 Fallback система** на случай ошибок

**Пользователь увидит красивые превью и сможет легко выбрать нужный шаблон!** 🎉