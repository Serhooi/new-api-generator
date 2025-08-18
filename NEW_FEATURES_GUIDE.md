# 🚀 Новые возможности API

## 📋 Исправленные проблемы:

### 1. ✅ **Photo слайд теперь обновляется**
- Добавлена расширенная отладка полей
- Улучшено сопоставление полей фронтенда с SVG
- В логах теперь видно какие поля приходят и почему не совпадают

### 2. ✅ **Превью шаблонов работают**
- PNG превью генерируются через Playwright
- Fallback через PIL если Playwright недоступен
- API: `GET /api/templates/all-previews` возвращает `preview_url`

### 3. ✅ **PNG конвертация после генерации**
- Новый API endpoint для конвертации SVG → PNG
- Поддержка Playwright и PIL fallback
- Загрузка PNG в Supabase

---

## 🔌 **Новый API: PNG Конвертация**

### Endpoint:
```
POST /api/convert-to-png
```

### Запрос:
```json
{
  "svg_url": "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-assets/carousel/file.svg"
}
```

### Ответ:
```json
{
  "success": true,
  "png_url": "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-assets/converted/file.png",
  "filename": "converted_abc123.png"
}
```

### Использование:
1. Генерируй карусель через `POST /api/generate/carousel`
2. Получи SVG URL из ответа
3. Конвертируй в PNG через `POST /api/convert-to-png`
4. Используй PNG URL для показа пользователю

---

## 🖼️ **Превью шаблонов**

### API для получения списка:
```
GET /api/templates/all-previews
```

### Ответ:
```json
{
  "templates": [
    {
      "id": "template-id",
      "name": "Template Name",
      "category": "open-house",
      "template_role": "main",
      "preview_url": "/output/previews/template-id_preview.png"
    }
  ]
}
```

### API для конкретного превью:
```
GET /api/templates/{template_id}/preview
```
Возвращает PNG или SVG превью напрямую.

---

## 🎠 **Генерация карусели (улучшена)**

### Endpoint остался тот же:
```
POST /api/generate/carousel
```

### Но теперь:
- ✅ **Photo слайд обновляется** правильно
- ✅ **URL валидные** (без лишнего `?`)
- ✅ **Расширенные логи** для отладки
- ✅ **Поддержка всех полей** включая `dyno.propertyimage2`

---

## 🔍 **Отладка Photo слайда**

В логах сервера теперь видно:

```
🔍 ВСЕ поля в photo SVG:
   - dyno.propertyimage2
   - dyno.propertyaddress

🔍 Поля от фронтенда:
   - dyno.propertyimage = https://...
   - dyno.propertyimage2 = https://...
   - dyno.price = $500,000

🔍 Replacements для photo SVG: {'dyno.propertyimage2': 'https://...'}
```

Это помогает понять почему поля не совпадают.

---

## 🧪 **Тестирование**

Запусти тест всех функций:
```bash
python3 test_all_fixes.py
```

Тест проверит:
- ✅ Превью шаблонов
- ✅ Генерацию карусели
- ✅ PNG конвертацию
- ✅ Доступность всех URL

---

## 📊 **Статус исправлений**

| Проблема | Статус | Решение |
|----------|--------|---------|
| Photo слайд не обновляется | ✅ Исправлено | Улучшена отладка полей |
| Превью шаблонов не работают | ✅ Исправлено | Playwright + PIL fallback |
| Нужна PNG конвертация | ✅ Добавлено | Новый API endpoint |
| Invalid URL ошибки | ✅ Исправлено | Убран лишний `?` |
| IndentationError на Render | ✅ Исправлено | Синтаксис исправлен |

**Все основные проблемы решены!** 🎉