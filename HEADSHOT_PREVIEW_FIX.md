# ИСПРАВЛЕНИЕ ПРЕВЬЮ ХЕДШОТА

## Проблема
Система превью заменяла headshot изображения на данные пользователя, что было неправильно.

## Решение
**Headshot теперь показывается как в оригинальном шаблоне, БЕЗ замены.**

## Что изменилось

### ✅ Исправлено в `preview_system.py`:

1. **Функция `process_image_replacements()`**:
   - Headshot поля (`dyno.agentheadshot`, `dyno.agentphoto`) теперь **пропускаются**
   - Показывается оригинальный headshot из шаблона
   - Property изображения по-прежнему заменяются

2. **Функция `replace_image_in_svg()`**:
   - Убрана логика изменения aspect ratio для headshot
   - Убрано масштабирование `scale(0.7)` для headshot
   - Headshot остается как в оригинальном шаблоне

### ✅ Исправлено в `app.py`:

1. **Функция `get_aspect_ratio_for_image()`**:
   - Для headshot возвращает `None` (не трогаем aspect ratio)

## Логика работы

```python
# Поля изображений обрабатываются так:
for field_name, image_url in image_data.items():
    if is_image_field(field_name):
        if is_headshot_field(field_name):
            # ⏭️ ПРОПУСКАЕМ - показываем оригинальный
            print(f"Пропускаю {field_name} (headshot)")
        else:
            # ✅ ЗАМЕНЯЕМ - property, logo и т.д.
            replace_image_in_svg(svg, field_name, image_url)
```

## Результат

### До исправления:
- ❌ Headshot заменялся на пользовательское изображение
- ❌ Применялось масштабирование `scale(0.7)`
- ❌ Изменялся aspect ratio на `xMidYMid meet`

### После исправления:
- ✅ Headshot показывается как в оригинальном шаблоне
- ✅ Никаких изменений aspect ratio или масштабирования
- ✅ Property изображения по-прежнему заменяются корректно

## Тестирование

Создан тест `test_headshot_logic.py` который проверяет:
- `dyno.agentheadshot` - пропускается ⏭️
- `dyno.agentphoto` - пропускается ⏭️  
- `dyno.propertyimage` - заменяется ✅
- `dyno.logo` - заменяется ✅

## Коммит
`682f33b` - ИСПРАВЛЕНИЕ: Убрана замена headshot в превью - показываем оригинальный из шаблона