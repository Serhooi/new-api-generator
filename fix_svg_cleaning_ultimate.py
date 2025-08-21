#!/usr/bin/env python3
"""
Ультимативная очистка SVG для исправления XML ошибок
"""

import re
import xml.etree.ElementTree as ET

def clean_svg_ultimate(svg_content):
    """
    Ультимативная очистка SVG с максимальной агрессивностью
    """
    print("🧹 Начинаю ультимативную очистку SVG...")
    
    cleaned = svg_content
    
    # 1. Убираем невалидные символы
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    print("✅ Удалены невалидные символы")
    
    # 2. Исправляем амперсанды (кроме уже экранированных)
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    print("✅ Исправлены амперсанды")
    
    # 3. Агрессивное исправление image тегов
    # Ищем все варианты незакрытых image тегов
    patterns = [
        r'<image([^>]*?)(?<!/)>(?!</image>)',  # <image ...> без закрытия
        r'<image([^>]*?)\s*>(?!</image>)',     # <image ...> с пробелами
        r'<image([^>]*?)(?<!/)\s*>',          # <image ...> любые варианты
    ]
    
    for pattern in patterns:
        before_count = len(re.findall(pattern, cleaned))
        cleaned = re.sub(pattern, r'<image\1/>', cleaned)
        after_count = len(re.findall(pattern, cleaned))
        if before_count > 0:
            print(f"✅ Исправлено {before_count} image тегов (паттерн: {pattern[:20]}...)")
    
    # 4. Исправляем другие самозакрывающиеся теги
    self_closing_tags = ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop', 'feOffset', 'feGaussianBlur', 'feFlood', 'feComposite', 'feMorphology']
    
    for tag in self_closing_tags:
        pattern = f'<{tag}([^>]*?)(?<!/)>(?!</{tag}>)'
        before_count = len(re.findall(pattern, cleaned))
        cleaned = re.sub(pattern, f'<{tag}\\1/>', cleaned)
        if before_count > 0:
            print(f"✅ Исправлено {before_count} {tag} тегов")
    
    # 5. Исправляем атрибуты с невалидными значениями
    # Убираем пустые атрибуты
    cleaned = re.sub(r'\s+\w+=""', '', cleaned)
    print("✅ Удалены пустые атрибуты")
    
    # 6. Исправляем проблемы с кавычками в атрибутах
    cleaned = re.sub(r'(\w+)=([^"\s>]+)(?=\s|>)', r'\1="\2"', cleaned)
    print("✅ Исправлены кавычки в атрибутах")
    
    # 7. Убираем дублирующиеся пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    print("✅ Убраны лишние пробелы")
    
    # 8. Финальная проверка - пытаемся парсить как XML
    try:
        # Пробуем парсить первые 1000 символов для быстрой проверки
        test_svg = cleaned[:1000] + "</svg>" if not cleaned[:1000].endswith("</svg>") else cleaned[:1000]
        ET.fromstring(test_svg)
        print("✅ XML структура валидна (тест)")
    except ET.ParseError as e:
        print(f"⚠️ XML все еще имеет проблемы: {e}")
        
        # Экстренная очистка - убираем все проблемные теги
        print("🚨 Применяю экстренную очистку...")
        
        # Убираем все незакрытые теги полностью
        cleaned = re.sub(r'<image[^>]*(?<!/)>', '', cleaned)
        cleaned = re.sub(r'<use[^>]*(?<!/)>', '', cleaned)
        print("🚨 Удалены все проблемные теги")
    
    print(f"🎯 Очистка завершена: {len(svg_content)} → {len(cleaned)} символов")
    
    return cleaned

def update_app_with_ultimate_cleaning():
    """Обновляем app.py с ультимативной очисткой"""
    
    print("📝 Читаю app.py...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Находим функцию очистки SVG
    old_cleaning_code = '''            # ОЧИЩАЕМ SVG перед rsvg-convert
            print("🧹 Очищаю SVG для rsvg-convert...")
            cleaned_svg = svg_content
            
            # Исправляем незакрытые теги image
            import re
            cleaned_svg = re.sub(r'<image([^>]*?)(?<!/)>', r'<image\\1/>', cleaned_svg)
            
            # Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # Исправляем другие самозакрывающиеся теги
            for tag in ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path']:
                cleaned_svg = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\\\1/>', cleaned_svg)
            
            print(f"🧹 SVG очищен для rsvg-convert, длина: {len(cleaned_svg)} символов")'''
    
    new_cleaning_code = '''            # УЛЬТИМАТИВНАЯ ОЧИСТКА SVG
            print("🧹 Применяю ультимативную очистку SVG...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. Агрессивное исправление image тегов (несколько паттернов)
            patterns = [
                r'<image([^>]*?)(?<!/)>(?!</image>)',  # <image ...> без закрытия
                r'<image([^>]*?)\\s*>(?!</image>)',     # <image ...> с пробелами
                r'<image([^>]*?)(?<!/)\\s*>',          # <image ...> любые варианты
            ]
            
            for pattern in patterns:
                cleaned_svg = re.sub(pattern, r'<image\\\\1/>', cleaned_svg)
            
            # 4. Исправляем другие самозакрывающиеся теги
            self_closing_tags = ['use', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop', 'feOffset', 'feGaussianBlur', 'feFlood', 'feComposite', 'feMorphology']
            
            for tag in self_closing_tags:
                pattern = f'<{tag}([^>]*?)(?<!/)>(?!</{tag}>)'
                cleaned_svg = re.sub(pattern, f'<{tag}\\\\1/>', cleaned_svg)
            
            # 5. Убираем пустые атрибуты и исправляем кавычки
            cleaned_svg = re.sub(r'\\s+\\w+=""', '', cleaned_svg)
            cleaned_svg = re.sub(r'(\\w+)=([^"\\s>]+)(?=\\s|>)', r'\\\\1="\\\\2"', cleaned_svg)
            
            # 6. Убираем лишние пробелы
            cleaned_svg = re.sub(r'\\s+', ' ', cleaned_svg)
            
            print(f"🧹 Ультимативная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    # Заменяем код
    if old_cleaning_code in content:
        content = content.replace(old_cleaning_code, new_cleaning_code)
        print("✅ Код очистки обновлен")
    else:
        print("⚠️ Не найден старый код очистки")
        return False
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с ультимативной очисткой")
    return True

if __name__ == "__main__":
    # Тестируем на примере
    test_svg = '''<svg><image href="test.jpg" x="0" y="0"><use href="#test"><rect width="100" height="100"></svg>'''
    
    print("🧪 Тестирую очистку:")
    print(f"До: {test_svg}")
    
    cleaned = clean_svg_ultimate(test_svg)
    print(f"После: {cleaned}")
    
    # Обновляем app.py
    print("\n📝 Обновляю app.py...")
    update_app_with_ultimate_cleaning()