#!/usr/bin/env python3
"""
Исправление проблем с headshot (растягивание) и photo слайдом (не заменяется)
"""

import re

def fix_headshot_aspect_ratio(svg_content):
    """
    Исправляет aspect ratio для headshot изображений
    """
    print("🔧 Исправляю aspect ratio для headshot...")
    
    # Ищем headshot элементы с неправильным aspect ratio
    headshot_pattern = r'(<[^>]*id="[^"]*headshot[^"]*"[^>]*preserveAspectRatio=")[^"]*("[^>]*>)'
    
    def fix_aspect_ratio(match):
        # Для headshot используем xMidYMid slice для правильного кропа
        return match.group(1) + 'xMidYMid slice' + match.group(2)
    
    fixed_svg = re.sub(headshot_pattern, fix_aspect_ratio, svg_content, flags=re.IGNORECASE)
    
    if fixed_svg != svg_content:
        print("✅ Aspect ratio для headshot исправлен!")
        return fixed_svg
    else:
        print("ℹ️ Headshot aspect ratio уже корректный")
        return svg_content

def analyze_photo_element_structure(svg_content, field_name="dyno.propertyimage2"):
    """
    Анализирует структуру photo элемента для понимания проблемы
    """
    print(f"🔍 АНАЛИЗ СТРУКТУРЫ: {field_name}")
    print("=" * 50)
    
    # Ищем элемент с данным id
    element_pattern = rf'<[^>]*id="{re.escape(field_name)}"[^>]*>'
    element_match = re.search(element_pattern, svg_content)
    
    if element_match:
        element = element_match.group()
        print(f"✅ Найден элемент: {element}")
        
        # Проверяем есть ли fill с pattern
        fill_match = re.search(r'fill="url\(#([^)]+)\)"', element)
        if fill_match:
            pattern_id = fill_match.group(1)
            print(f"✅ Найден pattern: {pattern_id}")
            
            # Ищем сам pattern
            pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
            pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
            
            if pattern_match:
                pattern_content = pattern_match.group(1)
                print(f"✅ Pattern содержимое: {pattern_content.strip()}")
                
                # Ищем use элемент
                use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"', pattern_content)
                if use_match:
                    image_id = use_match.group(1)
                    print(f"✅ Image ID: {image_id}")
                    
                    # Ищем image элемент
                    image_pattern = rf'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                    image_match = re.search(image_pattern, svg_content)
                    if image_match:
                        print(f"✅ Image элемент найден: {image_match.group()}")
                        return True
                    else:
                        print(f"❌ Image элемент с id {image_id} не найден")
                else:
                    print("❌ Use элемент не найден в pattern")
            else:
                print(f"❌ Pattern с id {pattern_id} не найден")
        else:
            print("❌ Fill с pattern не найден")
            
            # Проверяем другие возможные атрибуты
            if 'xlink:href' in element or 'href' in element:
                print("ℹ️ Элемент имеет прямую ссылку на изображение")
                href_match = re.search(r'(?:xlink:href|href)="([^"]*)"', element)
                if href_match:
                    print(f"🔗 Текущая ссылка: {href_match.group(1)[:50]}...")
                    return "direct"
            
            print("⚠️ Элемент не содержит ссылок на изображения")
    else:
        print(f"❌ Элемент с id {field_name} не найден")
    
    return False

def fix_photo_replacement_logic(svg_content, field_name, new_image_data):
    """
    Исправленная логика замены для photo элементов
    """
    print(f"🔧 Исправляю замену для {field_name}...")
    
    # Сначала анализируем структуру
    structure = analyze_photo_element_structure(svg_content, field_name)
    
    if structure == "direct":
        # Прямая замена href
        print("🔄 Использую прямую замену href...")
        element_pattern = rf'(<[^>]*id="{re.escape(field_name)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
        
        def replace_href(match):
            return match.group(1) + new_image_data + match.group(2)
        
        new_svg = re.sub(element_pattern, replace_href, svg_content)
        
        if new_svg != svg_content:
            print("✅ Прямая замена выполнена!")
            return new_svg
        else:
            print("❌ Прямая замена не удалась")
    
    elif structure == True:
        # Замена через pattern (стандартная логика)
        print("🔄 Использую замену через pattern...")
        return replace_image_via_pattern(svg_content, field_name, new_image_data)
    
    # Если стандартные методы не работают, пробуем альтернативные подходы
    print("🔄 Пробую альтернативные методы...")
    
    # Метод 1: Поиск по частичному совпадению id
    partial_pattern = rf'<[^>]*id="[^"]*{re.escape(field_name.split(".")[-1])}[^"]*"[^>]*>'
    partial_matches = re.findall(partial_pattern, svg_content, re.IGNORECASE)
    
    if partial_matches:
        print(f"🔍 Найдены частичные совпадения: {len(partial_matches)}")
        for match in partial_matches:
            print(f"   - {match}")
    
    # Метод 2: Поиск всех image элементов
    all_images = re.findall(r'<image[^>]*>', svg_content)
    print(f"🖼️ Всего image элементов: {len(all_images)}")
    
    return svg_content

def replace_image_via_pattern(svg_content, field_name, new_image_data):
    """
    Стандартная замена через pattern
    """
    # Ищем элемент с id
    element_pattern = rf'<[^>]*id="{re.escape(field_name)}"[^>]*fill="url\(#([^)]+)\)"[^>]*>'
    element_match = re.search(element_pattern, svg_content)
    
    if not element_match:
        return svg_content
    
    pattern_id = element_match.group(1)
    
    # Ищем pattern
    pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
    pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
    
    if not pattern_match:
        return svg_content
    
    pattern_content = pattern_match.group(1)
    
    # Ищем use элемент
    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"', pattern_content)
    if not use_match:
        return svg_content
    
    image_id = use_match.group(1)
    
    # Заменяем image элемент
    image_pattern = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    
    def replace_image_href(match):
        return match.group(1) + new_image_data + match.group(2)
    
    new_svg = re.sub(image_pattern, replace_image_href, svg_content)
    
    if new_svg != svg_content:
        print("✅ Замена через pattern выполнена!")
        return new_svg
    else:
        print("❌ Замена через pattern не удалась")
        return svg_content

def test_fixes():
    """
    Тестируем исправления на реальных файлах
    """
    print("🧪 ТЕСТ ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    # Тестируем на photo.svg
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            photo_svg = f.read()
        
        print("\n📄 Анализ photo.svg:")
        analyze_photo_element_structure(photo_svg, 'dyno.propertyimage2')
        
        # Тестируем исправление
        test_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
        fixed_photo = fix_photo_replacement_logic(photo_svg, 'dyno.propertyimage2', test_image_data)
        
        if fixed_photo != photo_svg:
            print("✅ Photo.svg исправлен!")
            with open('photo_fixed.svg', 'w', encoding='utf-8') as f:
                f.write(fixed_photo)
        else:
            print("⚠️ Photo.svg не изменен")
            
    except FileNotFoundError:
        print("⚠️ photo.svg не найден")
    
    # Тестируем на main.svg
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            main_svg = f.read()
        
        print("\n📄 Анализ main.svg (headshot):")
        analyze_photo_element_structure(main_svg, 'dyno.agentheadshot')
        
        # Исправляем aspect ratio
        fixed_main = fix_headshot_aspect_ratio(main_svg)
        
        if fixed_main != main_svg:
            print("✅ Main.svg исправлен!")
            with open('main_fixed.svg', 'w', encoding='utf-8') as f:
                f.write(fixed_main)
        else:
            print("⚠️ Main.svg не изменен")
            
    except FileNotFoundError:
        print("⚠️ main.svg не найден")

if __name__ == "__main__":
    test_fixes()