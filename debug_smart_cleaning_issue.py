#!/usr/bin/env python3
"""
Отладка проблем с умной очисткой SVG
"""

import requests
import re

def debug_real_svg_from_api():
    """Получаем реальный проблемный SVG с API"""
    
    print("🔍 Получаю реальный проблемный SVG с API...")
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "123 Test Street, Test City",
            "price": "$500,000",
            "beds": "3",
            "baths": "2",
            "sqft": "1,500",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    try:
        response = requests.post(api_url, json=test_data, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ API ошибка: {response.status_code}")
            return None
        
        result = response.json()
        
        if 'urls' not in result or len(result['urls']) == 0:
            print("❌ Нет URLs в ответе")
            return None
        
        # Получаем main SVG (первый URL)
        main_svg_url = result['urls'][0]
        print(f"📥 Загружаю main SVG: {main_svg_url}")
        
        svg_response = requests.get(main_svg_url, timeout=10)
        svg_content = svg_response.text
        
        print(f"📊 SVG размер: {len(svg_content)} символов")
        
        return svg_content
        
    except Exception as e:
        print(f"❌ Ошибка получения SVG: {e}")
        return None

def analyze_problematic_svg(svg_content):
    """Анализируем проблемный SVG"""
    
    print("🔍 Анализирую проблемный SVG...")
    
    # Ищем все image теги
    image_tags = re.findall(r'<image[^>]*>', svg_content)
    print(f"📊 Найдено {len(image_tags)} image тегов:")
    
    for i, tag in enumerate(image_tags[:5]):  # Показываем первые 5
        print(f"  {i+1}: {tag[:100]}...")
        
        # Проверяем закрыт ли тег
        if tag.endswith('/>'):
            print(f"    ✅ Тег закрыт")
        elif tag.endswith('>') and not tag.endswith('/>'):
            print(f"    ❌ Тег НЕ закрыт!")
        else:
            print(f"    ⚠️ Неопределенный статус")
    
    # Ищем use теги
    use_tags = re.findall(r'<use[^>]*>', svg_content)
    print(f"📊 Найдено {len(use_tags)} use тегов:")
    
    for i, tag in enumerate(use_tags[:5]):
        print(f"  {i+1}: {tag[:100]}...")
        
        if tag.endswith('/>'):
            print(f"    ✅ Тег закрыт")
        elif tag.endswith('>') and not tag.endswith('/>'):
            print(f"    ❌ Тег НЕ закрыт!")
    
    # Ищем конкретную проблему в позиции 373076
    if len(svg_content) >= 373076:
        problem_area = svg_content[373070:373090]
        print(f"🎯 Проблемная область (позиция 373076): '{problem_area}'")
    
    return image_tags, use_tags

def test_improved_smart_cleaning(svg_content):
    """Тестируем улучшенную умную очистку"""
    
    print("🧠 Тестирую УЛУЧШЕННУЮ умную очистку...")
    
    cleaned = svg_content
    
    # 1. Убираем невалидные символы
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    # 2. Исправляем амперсанды
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    
    # 3. БОЛЕЕ АГРЕССИВНАЯ очистка image тегов
    print("🔧 Исправляю image теги...")
    
    # Паттерн 1: <image ...> (без закрытия)
    pattern1 = r'<image([^>]*?)(?<!/)>'
    matches1 = re.findall(pattern1, cleaned)
    print(f"  Найдено незакрытых image тегов (паттерн 1): {len(matches1)}")
    cleaned = re.sub(pattern1, r'<image\1/>', cleaned)
    
    # Паттерн 2: <image ...> с пробелами
    pattern2 = r'<image([^>]*?)\s+>'
    matches2 = re.findall(pattern2, cleaned)
    print(f"  Найдено image тегов с пробелами (паттерн 2): {len(matches2)}")
    cleaned = re.sub(pattern2, r'<image\1/>', cleaned)
    
    # Паттерн 3: Любые image теги без />
    pattern3 = r'<image([^>]*?[^/])>'
    matches3 = re.findall(pattern3, cleaned)
    print(f"  Найдено image тегов без / (паттерн 3): {len(matches3)}")
    cleaned = re.sub(pattern3, r'<image\1/>', cleaned)
    
    # 4. То же для use тегов
    print("🔧 Исправляю use теги...")
    
    use_pattern1 = r'<use([^>]*?)(?<!/)>'
    use_matches1 = re.findall(use_pattern1, cleaned)
    print(f"  Найдено незакрытых use тегов: {len(use_matches1)}")
    cleaned = re.sub(use_pattern1, r'<use\1/>', cleaned)
    
    # 5. Убираем лишние пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    print(f"🧠 Улучшенная очистка завершена: {len(svg_content)} → {len(cleaned)} символов")
    
    # Проверяем результат
    remaining_image = len(re.findall(r'<image[^>]*[^/]>', cleaned))
    remaining_use = len(re.findall(r'<use[^>]*[^/]>', cleaned))
    
    print(f"🔍 После очистки:")
    print(f"  - Незакрытых image тегов: {remaining_image}")
    print(f"  - Незакрытых use тегов: {remaining_use}")
    
    if remaining_image == 0 and remaining_use == 0:
        print("✅ Все теги исправлены!")
        return cleaned, True
    else:
        print("❌ Остались незакрытые теги!")
        return cleaned, False

def main():
    """Основная функция отладки"""
    
    print("🔍 ОТЛАДКА ПРОБЛЕМ С УМНОЙ ОЧИСТКОЙ")
    print("=" * 50)
    
    # Получаем реальный проблемный SVG
    svg_content = debug_real_svg_from_api()
    
    if not svg_content:
        print("❌ Не удалось получить SVG для анализа")
        return
    
    # Анализируем проблемы
    image_tags, use_tags = analyze_problematic_svg(svg_content)
    
    # Тестируем улучшенную очистку
    cleaned_svg, success = test_improved_smart_cleaning(svg_content)
    
    if success:
        print("\n✅ Улучшенная очистка работает!")
        
        # Сохраняем результат
        with open('debug_improved_cleaned.svg', 'w') as f:
            f.write(cleaned_svg)
        
        print("💾 Сохранен файл: debug_improved_cleaned.svg")
    else:
        print("\n❌ Нужны еще более агрессивные исправления")

if __name__ == "__main__":
    main()