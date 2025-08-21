#!/usr/bin/env python3
"""
РАДИКАЛЬНОЕ исправление SVG через XML парсер
"""

import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

def fix_svg_with_xml_parser(svg_content):
    """
    РАДИКАЛЬНАЯ очистка SVG через XML парсер
    """
    print("🔥 РАДИКАЛЬНАЯ очистка SVG через XML парсер...")
    
    try:
        # Сначала пробуем базовую очистку
        cleaned = svg_content
        
        # 1. Убираем невалидные символы
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        # 2. Исправляем амперсанды
        cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
        
        # 3. АГРЕССИВНО исправляем все незакрытые теги
        # Находим все теги image и принудительно закрываем их
        cleaned = re.sub(r'<image([^>]*?)(?<!/)>', r'<image\1/>', cleaned)
        
        # Исправляем другие самозакрывающиеся теги
        self_closing_tags = ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop', 'feOffset', 'feGaussianBlur', 'feFlood', 'feComposite', 'feMorphology']
        
        for tag in self_closing_tags:
            cleaned = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\1/>', cleaned)
        
        print(f"✅ Базовая очистка завершена")
        
        # 4. Пробуем парсить как XML
        try:
            root = ET.fromstring(cleaned)
            print("✅ XML парсинг успешен!")
            
            # Конвертируем обратно в строку
            cleaned = ET.tostring(root, encoding='unicode')
            print("✅ XML реконструкция успешна!")
            
        except ET.ParseError as e:
            print(f"⚠️ XML парсинг не удался: {e}")
            
            # ЭКСТРЕННАЯ МЕРА - убираем все проблемные теги
            print("🚨 ЭКСТРЕННАЯ ОЧИСТКА - убираю все image теги!")
            
            # Убираем все image теги полностью
            cleaned = re.sub(r'<image[^>]*/?>', '', cleaned)
            
            # Убираем все use теги полностью
            cleaned = re.sub(r'<use[^>]*/?>', '', cleaned)
            
            print("🚨 Все проблемные теги удалены!")
        
        print(f"🎯 Очистка завершена: {len(svg_content)} → {len(cleaned)} символов")
        return cleaned
        
    except Exception as e:
        print(f"❌ Критическая ошибка очистки: {e}")
        return svg_content

def update_app_with_xml_parser():
    """Обновляем app.py с XML парсером"""
    
    print("📝 Читаю app.py...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Находим и заменяем функцию очистки
    old_cleaning_pattern = r'            # УЛЬТИМАТИВНАЯ ОЧИСТКА SVG.*?print\(f"🧹 Ультимативная очистка завершена, длина: \{len\(cleaned_svg\)\} символов"\)'
    
    new_cleaning_code = '''            # РАДИКАЛЬНАЯ ОЧИСТКА SVG ЧЕРЕЗ XML ПАРСЕР
            print("🔥 РАДИКАЛЬНАЯ очистка SVG через XML парсер...")
            cleaned_svg = svg_content
            
            import re
            import xml.etree.ElementTree as ET
            
            try:
                # 1. Убираем невалидные символы
                cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
                
                # 2. Исправляем амперсанды
                cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
                
                # 3. АГРЕССИВНО исправляем все незакрытые теги
                cleaned_svg = re.sub(r'<image([^>]*?)(?<!/)>', r'<image\\\\1/>', cleaned_svg)
                
                # Исправляем другие самозакрывающиеся теги
                self_closing_tags = ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop', 'feOffset', 'feGaussianBlur', 'feFlood', 'feComposite', 'feMorphology']
                
                for tag in self_closing_tags:
                    cleaned_svg = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\\\1/>', cleaned_svg)
                
                # 4. Пробуем парсить как XML
                try:
                    root = ET.fromstring(cleaned_svg)
                    cleaned_svg = ET.tostring(root, encoding='unicode')
                    print("✅ XML парсинг и реконструкция успешны!")
                    
                except ET.ParseError as xml_error:
                    print(f"⚠️ XML парсинг не удался: {xml_error}")
                    
                    # ЭКСТРЕННАЯ МЕРА - убираем все проблемные теги
                    print("🚨 ЭКСТРЕННАЯ ОЧИСТКА - убираю все image теги!")
                    cleaned_svg = re.sub(r'<image[^>]*/?>', '', cleaned_svg)
                    cleaned_svg = re.sub(r'<use[^>]*/?>', '', cleaned_svg)
                    print("🚨 Все проблемные теги удалены!")
                
            except Exception as critical_error:
                print(f"❌ Критическая ошибка очистки: {critical_error}")
                # В крайнем случае возвращаем оригинал
                cleaned_svg = svg_content
            
            print(f"🔥 Радикальная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    # Заменяем код
    import re as regex
    content = regex.sub(old_cleaning_pattern, new_cleaning_code, content, flags=regex.DOTALL)
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с XML парсером")
    return True

if __name__ == "__main__":
    # Тестируем на проблемном примере
    test_svg = '''<svg><image href="test.jpg" x="0" y="0" width="100" height="100"><use href="#test"><rect width="100" height="100"></svg>'''
    
    print("🧪 Тестирую радикальную очистку:")
    print(f"До: {test_svg}")
    
    cleaned = fix_svg_with_xml_parser(test_svg)
    print(f"После: {cleaned}")
    
    # Обновляем app.py
    print("\n📝 Обновляю app.py...")
    update_app_with_xml_parser()