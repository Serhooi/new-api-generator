# 🎠 API ДОКУМЕНТАЦИЯ - КАРУСЕЛИ

## 🎯 Новые Endpoints

### **GET `/api/carousels/all`**
Получает все карусели с превью для main и photo шаблонов

#### **Ответ:**
```json
{
  "success": true,
  "carousels": [
    {
      "id": "carousel-uuid",
      "name": "Название карусели",
      "category": "Категория",
      "created_at": "2025-01-25 12:00:00",
      "main_template": {
        "id": "main-template-uuid",
        "name": "Название Main шаблона",
        "preview_url": "/output/template_previews/template_main_preview.png",
        "dyno_fields": ["agent_name", "price", "address"]
      },
      "photo_template": {
        "id": "photo-template-uuid", 
        "name": "Название Photo шаблона",
        "preview_url": "/output/template_previews/template_photo_preview.png",
        "dyno_fields": ["property_photo"]
      }
    }
  ],
  "total_count": 1
}
```

### **GET `/api/carousels/<carousel_id>`**
Получает информацию о конкретной карусели

#### **Параметры:**
- `carousel_id` - UUID карусели

#### **Ответ:**
```json
{
  "success": true,
  "carousel": {
    "id": "carousel-uuid",
    "name": "Название карусели",
    "category": "Категория",
    "created_at": "2025-01-25 12:00:00",
    "main_template": {
      "id": "main-template-uuid",
      "name": "Название Main шаблона",
      "preview_url": "/output/template_previews/template_main_preview.png",
      "dyno_fields": ["agent_name", "price", "address"]
    },
    "photo_template": {
      "id": "photo-template-uuid",
      "name": "Название Photo шаблона", 
      "preview_url": "/output/template_previews/template_photo_preview.png",
      "dyno_fields": ["property_photo"]
    }
  }
}
```

## 🌐 Фронтенд Интеграция

### **Получение всех каруселей:**
```javascript
async function loadCarousels() {
  try {
    const response = await fetch('/api/carousels/all');
    const data = await response.json();
    
    if (data.success) {
      const carousels = data.carousels;
      
      // Отображаем карусели пользователю
      carousels.forEach(carousel => {
        displayCarousel(carousel);
      });
    }
  } catch (error) {
    console.error('Ошибка загрузки каруселей:', error);
  }
}

function displayCarousel(carousel) {
  const carouselElement = document.createElement('div');
  carouselElement.className = 'carousel-item';
  
  carouselElement.innerHTML = `
    <h3>🎠 ${carousel.name}</h3>
    <div class="carousel-templates">
      <div class="main-template">
        <h4>🎯 Main Template</h4>
        <img src="${carousel.main_template.preview_url}" alt="Main Preview">
        <p>Поля: ${carousel.main_template.dyno_fields.join(', ')}</p>
      </div>
      <div class="photo-template">
        <h4>📸 Photo Template</h4>
        <img src="${carousel.photo_template.preview_url}" alt="Photo Preview">
        <p>Поля: ${carousel.photo_template.dyno_fields.join(', ')}</p>
      </div>
    </div>
    <button onclick="selectCarousel('${carousel.id}')">Выбрать карусель</button>
  `;
  
  document.getElementById('carousels-container').appendChild(carouselElement);
}
```

### **Выбор карусели:**
```javascript
async function selectCarousel(carouselId) {
  try {
    const response = await fetch(`/api/carousels/${carouselId}`);
    const data = await response.json();
    
    if (data.success) {
      const carousel = data.carousel;
      
      // Сохраняем выбранную карусель
      selectedCarousel = carousel;
      
      // Показываем форму для заполнения данных
      showDataForm(carousel);
    }
  } catch (error) {
    console.error('Ошибка получения карусели:', error);
  }
}

function showDataForm(carousel) {
  // Собираем все уникальные поля из main и photo шаблонов
  const allFields = [
    ...carousel.main_template.dyno_fields,
    ...carousel.photo_template.dyno_fields
  ].filter((field, index, arr) => arr.indexOf(field) === index);
  
  // Создаем форму для заполнения
  const form = document.createElement('form');
  form.innerHTML = `
    <h3>📝 Заполните данные для карусели "${carousel.name}"</h3>
    ${allFields.map(field => `
      <div class="form-group">
        <label for="${field}">${field}:</label>
        <input type="text" id="${field}" name="${field}" required>
      </div>
    `).join('')}
    <button type="submit">🎨 Создать карусель</button>
  `;
  
  form.onsubmit = (e) => {
    e.preventDefault();
    generateCarousel(carousel, new FormData(form));
  };
  
  document.getElementById('data-form-container').appendChild(form);
}
```

### **Генерация карусели:**
```javascript
async function generateCarousel(carousel, formData) {
  try {
    // Подготавливаем данные для замены
    const replacements = {};
    for (let [key, value] of formData.entries()) {
      replacements[key] = value;
    }
    
    // Отправляем запрос на генерацию
    const response = await fetch('/api/generate/carousel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        main_template_id: carousel.main_template.id,
        photo_template_id: carousel.photo_template.id,
        replacements: replacements,
        slides_count: 5 // или любое количество слайдов
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Показываем результат
      showGeneratedCarousel(result);
    }
  } catch (error) {
    console.error('Ошибка генерации карусели:', error);
  }
}
```

## 🎨 Пример использования

### **HTML структура:**
```html
<div id="carousel-selector">
  <h2>🎠 Выберите карусель</h2>
  <div id="carousels-container"></div>
</div>

<div id="data-form-container" style="display: none;">
  <!-- Форма для заполнения данных появится здесь -->
</div>

<div id="result-container" style="display: none;">
  <!-- Результат генерации появится здесь -->
</div>
```

### **CSS стили:**
```css
.carousel-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin: 10px 0;
  background: white;
}

.carousel-templates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 15px 0;
}

.main-template, .photo-template {
  text-align: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
}

.main-template img, .photo-template img {
  width: 100%;
  max-width: 200px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}
```

## 🔧 Workflow для фронтенда

### **1. Загрузка каруселей:**
```javascript
// При загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
  await loadCarousels();
});
```

### **2. Отображение каруселей:**
```javascript
// Показываем все доступные карусели с превью
// Пользователь видит как выглядят main и photo шаблоны
// Может выбрать подходящую карусель
```

### **3. Выбор карусели:**
```javascript
// Пользователь кликает "Выбрать карусель"
// Получаем детальную информацию о карусели
// Показываем форму для заполнения dyno полей
```

### **4. Заполнение данных:**
```javascript
// Пользователь заполняет все необходимые поля
// Отправляем данные на генерацию карусели
```

### **5. Получение результата:**
```javascript
// Получаем готовую карусель
// Показываем пользователю результат
// Предлагаем скачать или поделиться
```

## 🎯 Преимущества нового подхода

### **Для пользователя:**
- **🎨 Визуальный выбор** - видит превью main и photo шаблонов
- **🎯 Готовые комбинации** - не нужно выбирать отдельные шаблоны
- **⚡ Быстрый выбор** - сразу понятно как будет выглядеть карусель
- **📱 Лучший UX** - простой и понятный интерфейс

### **Для разработчика:**
- **🔧 Простая интеграция** - один API call для получения всех каруселей
- **📊 Структурированные данные** - вся информация в одном ответе
- **🎨 Готовые превью** - не нужно генерировать на лету
- **🚀 Масштабируемость** - легко добавлять новые карусели

## 🧪 Тестирование

### **Тестовая страница:**
Откройте `test_carousel_api.html` для проверки API

### **Проверка API:**
```bash
# Получить все карусели
curl http://localhost:5000/api/carousels/all

# Получить конкретную карусель
curl http://localhost:5000/api/carousels/CAROUSEL_ID
```

## 🎉 Итог

**Теперь у вас есть полноценный API для работы с каруселями!**

- ✅ Получение всех каруселей с превью
- ✅ Получение конкретной карусели
- ✅ Структурированные данные для фронтенда
- ✅ Готовые URL превью для отображения
- ✅ Информация о dyno полях для форм
- ✅ Простая интеграция с любым фронтендом

**Пользователи смогут легко выбирать готовые карусели вместо отдельных шаблонов!** 🎠✨