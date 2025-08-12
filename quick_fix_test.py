#!/usr/bin/env python3
"""
Быстрый тест исправлений без зависимостей
"""

import re

def quick_replace_image_test(svg_content, field_name, new_image_url):
    """Упрощенная версия replace_image_in_svg для тестирования"""
    
    print(f"🖼️ Обрабатываю изображение: {field_name}")
    
    # Определяем тип изображения для правильного aspect ratio
    if 'headshot' in field_name.lower():
        image_type = 'headshot'
        aspect_ratio = 'xMidYMid slice'
    elif 'property' in field_name.lower():
        image_type = 'property'
        aspect_ratio = 'xMidYMid slice'
    else:
        image_type = 'other'
        aspect_ratio = 'xMidYMid meet'
    
    print(f"🎯 Тип изображения: {image_type}, aspect ratio: {aspect_ratio}")
    
    # Метод 1: Прямой поиск элемента с id и href
    direct_pattern = rf'(<[^>]*id="{re.escape(field_name)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    direct_match = re.search(direct_pattern, svg_content)
    
    if direct_match:
        print(f"✅ Найден прямой элемент с id: {field_name}")
        new_svg = re.sub(direct_pattern, 
                        lambda m: m.group(1) + new_image_url + m.group(2), 
                        svg_content)
        
        # Исправляем aspect ratio если нужно
        if image_type == 'headshot':
            aspect_pattern = rf'(<[^>]*id="{re.escape(field_name)}"[^>]*preserveAspectRatio=")[^"]*("[^>]*>)'
            new_svg = re.sub(aspect_pattern,
                            lambda m: m.group(1) + aspect_ratio + m.group(2),
                            new_svg)
            print(f"🔧 Aspect ratio исправлен на: {aspect_ratio}")
        
        if new_svg != svg_content:
            print(f"✅ Изображение {field_name} заменено!")
            return new_svg
    
    # Метод 2: Поиск через группу (для photo.svg)
    group_pattern = rf'<g[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*>'
    group_match = re.search(group_pattern, svg_content, re.IGNORECASE)
    
    if group_match:
        print(f"✅ Найдена группа с id: {field_name}")
        
        # Находим содержимое группы
        group_start = group_match.end()
        group_end_match = re.search(r'</g>', svg_content[group_start:])
        
        if group_end_match:
            group_content = svg_content[group_start:group_start + group_end_match.start()]
            
            # Ищем fill="url(#pattern_id)" внутри группы
            fill_match = re.search(r'fill="url\(#([^)]+)\)"', group_content)
            
            if fill_match:
                pattern_id = fill_match.group(1)
                print(f"✅ Найден pattern: {pattern_id}")
                
                return replace_via_pattern_test(svg_content, pattern_id, new_image_url, image_type, aspect_ratio)
            else:
                print("❌ Fill с pattern не найден в группе")
        else:
            print("❌ Закрывающий тег </g> не найден")
    
    # Метод 3: Поиск элемента с fill="url(#pattern_id)"
    element_pattern = rf'<[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*fill="url\(#([^)]+)\)"[^>]*>'
    element_match = re.search(element_pattern, svg_content, re.IGNORECASE)
    
    if element_match:
        pattern_id = element_match.group(1)
        print(f"✅ Найден pattern: {pattern_id}")
        
        return replace_via_pattern_test(svg_content, pattern_id, new_image_url, image_type, aspect_ratio)
    
    print(f"❌ Элемент {field_name} не найден")
    return svg_content

def replace_via_pattern_test(svg_content, pattern_id, replacement_data, image_type, aspect_ratio):
    """Заменяет изображение через pattern -> image связь"""
    
    # Ищем pattern с данным ID
    pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
    pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
    
    if not pattern_match:
        print(f"❌ Pattern с ID {pattern_id} не найден")
        return svg_content
    
    pattern_content = pattern_match.group(1)
    
    # Ищем use элемент в pattern
    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
    if not use_match:
        print(f"❌ Use элемент не найден в pattern {pattern_id}")
        return svg_content
    
    image_id = use_match.group(1)
    print(f"✅ Найден image ID: {image_id}")
    
    # Заменяем image элемент
    image_pattern = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    
    def replace_image_href(match):
        return match.group(1) + replacement_data + match.group(2)
    
    new_svg = re.sub(image_pattern, replace_image_href, svg_content)
    
    # Исправляем aspect ratio если это headshot
    if image_type == 'headshot':
        aspect_pattern = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*preserveAspectRatio=")[^"]*("[^>]*>)'
        new_svg = re.sub(aspect_pattern,
                        lambda m: m.group(1) + aspect_ratio + m.group(2),
                        new_svg)
        print(f"🔧 Aspect ratio исправлен на: {aspect_ratio}")
    
    if new_svg != svg_content:
        print(f"✅ Изображение успешно заменено через pattern!")
        return new_svg
    else:
        print(f"❌ Замена через pattern не удалась")
        return svg_content

def test_headshot_fix():
    """Тестируем исправление headshot"""
    
    print("🧪 ТЕСТ HEADSHOT ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            main_svg = f.read()
    except FileNotFoundError:
        print("❌ main.svg не найден")
        return
    
    # Проверяем текущий aspect ratio
    current_aspect_match = re.search(r'<image[^>]*id="image2_294_4"[^>]*preserveAspectRatio="([^"]*)"[^>]*>', main_svg)
    if current_aspect_match:
        print(f"📋 Текущий aspect ratio: {current_aspect_match.group(1)}")
    
    # Тестовые данные
    test_image = "data:image/jpeg;base64,TEST_DATA"
    
    # Применяем исправление
    fixed_svg = quick_replace_image_test(main_svg, 'dyno.agentheadshot', test_image)
    
    if fixed_svg != main_svg:
        # Проверяем новый aspect ratio
        new_aspect_match = re.search(r'<image[^>]*id="image2_294_4"[^>]*preserveAspectRatio="([^"]*)"[^>]*>', fixed_svg)
        if new_aspect_match:
            new_aspect = new_aspect_match.group(1)
            print(f"✅ Новый aspect ratio: {new_aspect}")
            
            if new_aspect == 'xMidYMid slice':
                print("🎉 HEADSHOT ASPECT RATIO ИСПРАВЛЕН!")
            else:
                print(f"❌ Aspect ratio не исправлен правильно")
        
        # Проверяем замену изображения
        if test_image in fixed_svg:
            print("✅ Изображение заменено!")
        
        with open('main_quick_test.svg', 'w', encoding='utf-8') as f:
            f.write(fixed_svg)
        print("💾 Результат сохранен в main_quick_test.svg")
    else:
        print("❌ SVG не был изменен")

def test_photo_fix():
    """Тестируем исправление photo"""
    
    print("\n🧪 ТЕСТ PHOTO ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            photo_svg = f.read()
    except FileNotFoundError:
        print("❌ photo.svg не найден")
        return
    
    # Тестовые данные
    test_image = "data:image/jpeg;base64,TEST_PHOTO_DATA"
    
    # Применяем исправление
    fixed_svg = quick_replace_image_test(photo_svg, 'dyno.propertyimage2', test_image)
    
    if fixed_svg != photo_svg:
        # Проверяем замену изображения
        if test_image in fixed_svg:
            print("✅ Изображение заменено!")
            print("🎉 PHOTO ГРУППА ИСПРАВЛЕНА!")
        
        with open('photo_quick_test.svg', 'w', encoding='utf-8') as f:
            f.write(fixed_svg)
        print("💾 Результат сохранен в photo_quick_test.svg")
        
        print(f"📊 Изменение размера: {len(fixed_svg) - len(photo_svg):+d} символов")
    else:
        print("❌ SVG не был изменен")

def main():
    """Запускаем тесты"""
    
    print("🚀 БЫСТРЫЕ ТЕСТЫ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    test_headshot_fix()
    test_photo_fix()
    
    print("\n🎯 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")

if __name__ == "__main__":
    main()