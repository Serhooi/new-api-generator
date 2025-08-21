#!/usr/bin/env python3
"""
Отладка проблемы с незакрытым тегом image на строке 68
"""

import requests
import re

def analyze_svg_line68():
    """Анализируем проблему с line 68 column 29638"""
    
    # Тестируем с реальным API
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "main_template_1",
        "photo_template_id": "photo_template_1", 
        "data": {
            "propertyaddress": "123 Test Street, Test City",
            "price": "$500,000",
            "beds": "3",
            "baths": "2",
            "sqft": "1,500"
        }
    }
    
    print("🔍 Запрашиваю SVG с сервера...")
    
    try:
        response = requests.post(api_url, json=test_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return
        
        result = response.json()
        
        if 'urls' not in result:
            print("❌ Нет urls в ответе")
            print(f"Response keys: {list(result.keys())}")
            return
        
        # Получаем SVG
        print(f"URLs type: {type(result['urls'])}")
        print(f"URLs: {result['urls']}")
        
        # Ищем SVG URL в разных местах
        svg_url = None
        if isinstance(result['urls'], list) and len(result['urls']) > 0:
            svg_url = result['urls'][0]  # Берем первый URL
        elif isinstance(result['urls'], dict):
            svg_url = result['urls'].get('main_svg')
        
        if not svg_url:
            print("❌ Не найден SVG URL")
            return
        print(f"📥 Загружаю SVG: {svg_url}")
        
        svg_response = requests.get(svg_url, timeout=10)
        svg_content = svg_response.text
        
        print(f"📊 SVG размер: {len(svg_content)} символов")
        
        # Анализируем строку 68
        lines = svg_content.split('\n')
        
        if len(lines) >= 68:
            line68 = lines[67]  # 0-based index
            print(f"🔍 Строка 68 (длина {len(line68)}):")
            print(f"'{line68}'")
            
            # Ищем позицию 29638
            if len(line68) >= 29638:
                context_start = max(0, 29638 - 50)
                context_end = min(len(line68), 29638 + 50)
                context = line68[context_start:context_end]
                print(f"🎯 Контекст вокруг позиции 29638:")
                print(f"'{context}'")
                
                # Ищем незакрытые теги image
                image_tags = re.findall(r'<image[^>]*>', line68)
                print(f"🖼️ Найдено image тегов: {len(image_tags)}")
                
                for i, tag in enumerate(image_tags[:5]):  # Показываем первые 5
                    print(f"  {i+1}: {tag}")
                    if not tag.endswith('/>'):
                        print(f"    ⚠️ Незакрытый тег!")
            else:
                print(f"⚠️ Строка 68 короче 29638 символов (длина: {len(line68)})")
        else:
            print(f"⚠️ SVG содержит только {len(lines)} строк")
        
        # Ищем все незакрытые image теги
        all_image_tags = re.findall(r'<image[^>]*[^/]>', svg_content)
        print(f"🔍 Всего незакрытых image тегов: {len(all_image_tags)}")
        
        if all_image_tags:
            print("🚨 Примеры незакрытых тегов:")
            for i, tag in enumerate(all_image_tags[:3]):
                print(f"  {i+1}: {tag[:100]}...")
        
        # Тестируем нашу очистку
        print("\n🧹 Тестирую очистку SVG...")
        
        cleaned_svg = svg_content
        
        # Исправляем незакрытые теги image
        cleaned_svg = re.sub(r'<image([^>]*?)(?<!/)>', r'<image\1/>', cleaned_svg)
        
        # Убираем невалидные символы
        cleaned_svg = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned_svg)
        
        # Исправляем амперсанды
        cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
        
        # Исправляем другие самозакрывающиеся теги
        for tag in ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path']:
            cleaned_svg = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\1/>', cleaned_svg)
        
        print(f"✅ Очистка завершена, новый размер: {len(cleaned_svg)} символов")
        
        # Проверяем результат
        cleaned_image_tags = re.findall(r'<image[^>]*[^/]>', cleaned_svg)
        print(f"🔍 Незакрытых image тегов после очистки: {len(cleaned_image_tags)}")
        
        if cleaned_image_tags:
            print("⚠️ Очистка не помогла! Остались незакрытые теги:")
            for i, tag in enumerate(cleaned_image_tags[:3]):
                print(f"  {i+1}: {tag[:100]}...")
        else:
            print("✅ Все image теги закрыты!")
        
        # Сохраняем для анализа
        with open('debug_original.svg', 'w') as f:
            f.write(svg_content)
        
        with open('debug_cleaned.svg', 'w') as f:
            f.write(cleaned_svg)
        
        print("💾 Сохранены файлы: debug_original.svg, debug_cleaned.svg")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    analyze_svg_line68()