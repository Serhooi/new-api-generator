#!/usr/bin/env python3
"""
Тест исправления очистки SVG - проверяем что теги закрываются правильно
"""

import re

def test_svg_cleaning():
    """Тестируем исправленную очистку SVG"""
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ ОЧИСТКИ SVG")
    print("=" * 50)
    
    # Тестовый SVG с проблемными тегами
    test_svg = '''<svg xmlns="http://www.w3.org/2000/svg">
        <image id="test1" href="data:image/jpeg;base64,/9j/4AAQ" width="100" height="100">
        <image id="test2" href="data:image/png;base64,iVBOR" width="200" height="200"/>
        <use id="test3" href="#pattern1">
        <use id="test4" href="#pattern2"/>
    </svg>'''
    
    print("📋 Исходный SVG:")
    print(test_svg)
    
    print("\n🔧 Применяю исправления...")
    
    cleaned_svg = test_svg
    
    # 4. Исправляем image теги - ТОЛЬКО если они не самозакрывающиеся
    def fix_image_tag(match):
        tag_content = match.group(1)
        # Если уже самозакрывающийся - не трогаем
        if tag_content.strip().endswith('/'):
            return match.group(0)
        # Если не самозакрывающийся - делаем самозакрывающимся
        return f'<image{tag_content}/>'
    
    # Ищем только НЕ самозакрывающиеся image теги
    cleaned_svg = re.sub(r'<image([^>]*?[^/])>', fix_image_tag, cleaned_svg)
    
    # 5. Исправляем use теги - ТОЛЬКО если они не самозакрывающиеся
    def fix_use_tag(match):
        tag_content = match.group(1)
        # Если уже самозакрывающийся - не трогаем
        if tag_content.strip().endswith('/'):
            return match.group(0)
        # Если не самозакрывающийся - делаем самозакрывающимся
        return f'<use{tag_content}/>'
    
    # Ищем только НЕ самозакрывающиеся use теги
    cleaned_svg = re.sub(r'<use([^>]*?[^/])>', fix_use_tag, cleaned_svg)
    
    # 6. КРИТИЧЕСКАЯ ПРОВЕРКА: ищем незакрытые теги
    unclosed_tags = re.findall(r'<(image|use)\s[^>]*[^/>]$', cleaned_svg, re.MULTILINE)
    if unclosed_tags:
        print(f"⚠️ Найдены незакрытые теги: {unclosed_tags}")
        # Исправляем незакрытые теги в конце строк
        cleaned_svg = re.sub(r'<(image|use)([^>]*[^/>])$', r'<\1\2/>', cleaned_svg, flags=re.MULTILINE)
    
    print("\n📋 Очищенный SVG:")
    print(cleaned_svg)
    
    print("\n📊 РЕЗУЛЬТАТ:")
    # Проверяем что все теги закрыты
    image_tags = re.findall(r'<image[^>]*>', cleaned_svg)
    use_tags = re.findall(r'<use[^>]*>', cleaned_svg)
    
    print(f"   Image теги: {len(image_tags)}")
    for tag in image_tags:
        if tag.endswith('/>'):
            print(f"     ✅ {tag[:50]}...")
        else:
            print(f"     ❌ {tag[:50]}...")
    
    print(f"   Use теги: {len(use_tags)}")
    for tag in use_tags:
        if tag.endswith('/>'):
            print(f"     ✅ {tag[:50]}...")
        else:
            print(f"     ❌ {tag[:50]}...")

if __name__ == "__main__":
    test_svg_cleaning()