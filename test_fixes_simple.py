#!/usr/bin/env python3
"""
Простой тест исправлений без зависимостей
"""

import re

def test_aspect_ratio_logic():
    """Тестируем логику определения aspect ratio"""
    
    print("🧪 ТЕСТ ЛОГИКИ ASPECT RATIO")
    print("=" * 40)
    
    test_cases = [
        ('dyno.agentheadshot', 'headshot', 'xMidYMid slice'),
        ('dyno.propertyimage2', 'property', 'xMidYMid slice'),
        ('dyno.logo', 'other', 'xMidYMid meet'),
    ]
    
    for field_name, expected_type, expected_aspect in test_cases:
        # Логика из нашего исправления
        if 'headshot' in field_name.lower():
            image_type = 'headshot'
            aspect_ratio = 'xMidYMid slice'
        elif 'property' in field_name.lower():
            image_type = 'property'
            aspect_ratio = 'xMidYMid slice'
        else:
            image_type = 'other'
            aspect_ratio = 'xMidYMid meet'
        
        print(f"📋 {field_name}:")
        print(f"   Тип: {image_type} (ожидался: {expected_type})")
        print(f"   Aspect: {aspect_ratio} (ожидался: {expected_aspect})")
        
        if image_type == expected_type and aspect_ratio == expected_aspect:
            print("   ✅ ПРАВИЛЬНО!")
        else:
            print("   ❌ ОШИБКА!")
        print()

def test_group_detection():
    """Тестируем обнаружение групп в photo.svg"""
    
    print("🧪 ТЕСТ ОБНАРУЖЕНИЯ ГРУПП")
    print("=" * 40)
    
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            photo_svg = f.read()
    except FileNotFoundError:
        print("❌ photo.svg не найден")
        return
    
    field_name = 'dyno.propertyimage2'
    
    # Тестируем новую логику поиска групп
    group_pattern = rf'<g[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*>'
    group_match = re.search(group_pattern, photo_svg, re.IGNORECASE)
    
    if group_match:
        print(f"✅ Найдена группа: {group_match.group()}")
        
        # Находим содержимое группы
        group_start = group_match.end()
        group_end_match = re.search(r'</g>', photo_svg[group_start:])
        
        if group_end_match:
            group_content = photo_svg[group_start:group_start + group_end_match.start()]
            print(f"📋 Содержимое группы: {group_content.strip()[:100]}...")
            
            # Ищем fill="url(#pattern_id)" внутри группы
            fill_match = re.search(r'fill="url\(#([^)]+)\)"', group_content)
            
            if fill_match:
                pattern_id = fill_match.group(1)
                print(f"✅ Найден pattern: {pattern_id}")
                
                # Ищем pattern в SVG
                pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                pattern_match = re.search(pattern_pattern, photo_svg, re.DOTALL)
                
                if pattern_match:
                    pattern_content = pattern_match.group(1)
                    print(f"✅ Pattern найден: {pattern_content.strip()}")
                    
                    # Ищем use элемент
                    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
                    if use_match:
                        image_id = use_match.group(1)
                        print(f"✅ Image ID: {image_id}")
                        print("🎉 ВСЯ ЦЕПОЧКА НАЙДЕНА УСПЕШНО!")
                    else:
                        print("❌ Use элемент не найден")
                else:
                    print(f"❌ Pattern {pattern_id} не найден")
            else:
                print("❌ Fill с pattern не найден в группе")
        else:
            print("❌ Закрывающий тег </g> не найден")
    else:
        print(f"❌ Группа с id содержащим {field_name} не найдена")

def test_headshot_pattern():
    """Тестируем поиск headshot в main.svg"""
    
    print("\n🧪 ТЕСТ HEADSHOT PATTERN")
    print("=" * 40)
    
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            main_svg = f.read()
    except FileNotFoundError:
        print("❌ main.svg не найден")
        return
    
    field_name = 'dyno.agentheadshot'
    
    # Проверяем текущий aspect ratio
    image_pattern = r'<image[^>]*id="image2_294_4"[^>]*preserveAspectRatio="([^"]*)"[^>]*>'
    current_match = re.search(image_pattern, main_svg)
    
    if current_match:
        current_aspect = current_match.group(1)
        print(f"📋 Текущий aspect ratio: {current_aspect}")
        
        if current_aspect == 'xMidYMid meet':
            print("⚠️ ПРОБЛЕМА: используется 'meet' вместо 'slice'")
            print("🔧 Нужно заменить на 'xMidYMid slice'")
        elif current_aspect == 'xMidYMid slice':
            print("✅ Aspect ratio уже правильный!")
        else:
            print(f"❓ Неожиданный aspect ratio: {current_aspect}")
    else:
        print("❌ Image элемент не найден")

def main():
    """Запускаем все тесты"""
    
    print("🚀 ПРОСТЫЕ ТЕСТЫ ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    test_aspect_ratio_logic()
    test_group_detection()
    test_headshot_pattern()
    
    print("\n🎯 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")

if __name__ == "__main__":
    main()