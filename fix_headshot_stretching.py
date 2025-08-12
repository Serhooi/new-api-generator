#!/usr/bin/env python3
"""
Исправление растягивания headshot изображений
"""

import re

def fix_headshot_aspect_ratio(svg_content):
    """
    Исправляет preserveAspectRatio для headshot изображений
    """
    print("🔧 Исправляю preserveAspectRatio для headshot...")
    
    # Ищем все image элементы с preserveAspectRatio="none"
    image_pattern = r'(<image[^>]*preserveAspectRatio=")none("[^>]*>)'
    
    def fix_aspect_ratio(match):
        # Заменяем "none" на "xMidYMid slice" для правильного кропа
        return match.group(1) + 'xMidYMid slice' + match.group(2)
    
    fixed_svg = re.sub(image_pattern, fix_aspect_ratio, svg_content)
    
    changes = len(re.findall(image_pattern, svg_content))
    if changes > 0:
        print(f"✅ Исправлено {changes} image элементов с preserveAspectRatio")
        return fixed_svg
    else:
        print("ℹ️ Не найдено image элементов с preserveAspectRatio='none'")
        return svg_content

def analyze_headshot_structure(svg_content):
    """
    Анализирует структуру headshot элемента
    """
    print("🔍 АНАЛИЗ СТРУКТУРЫ HEADSHOT")
    print("=" * 40)
    
    # Ищем dyno.agentheadshot группу
    headshot_pattern = r'<g[^>]*id="[^"]*agentheadshot[^"]*"[^>]*>'
    headshot_match = re.search(headshot_pattern, svg_content, re.IGNORECASE)
    
    if headshot_match:
        print(f"✅ Найдена headshot группа: {headshot_match.group()}")
        
        # Находим содержимое группы
        group_start = headshot_match.end()
        group_end_match = re.search(r'</g>', svg_content[group_start:])
        
        if group_end_match:
            group_content = svg_content[group_start:group_start + group_end_match.start()]
            print(f"📋 Содержимое группы: {group_content.strip()}")
            
            # Ищем fill pattern
            fill_match = re.search(r'fill="url\(#([^)]+)\)"', group_content)
            if fill_match:
                pattern_id = fill_match.group(1)
                print(f"✅ Pattern ID: {pattern_id}")
                
                # Ищем pattern
                pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
                
                if pattern_match:
                    pattern_content = pattern_match.group(1)
                    print(f"📋 Pattern содержимое: {pattern_content.strip()}")
                    
                    # Ищем use элемент
                    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*transform="([^"]+)"', pattern_content)
                    if use_match:
                        image_id = use_match.group(1)
                        transform = use_match.group(2)
                        print(f"✅ Image ID: {image_id}")
                        print(f"📐 Transform: {transform}")
                        
                        # Ищем image элемент
                        image_pattern = rf'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                        image_match = re.search(image_pattern, svg_content)
                        
                        if image_match:
                            image_element = image_match.group()
                            print(f"🖼️ Image элемент: {image_element}")
                            
                            # Проверяем preserveAspectRatio
                            aspect_match = re.search(r'preserveAspectRatio="([^"]+)"', image_element)
                            if aspect_match:
                                aspect_ratio = aspect_match.group(1)
                                print(f"📏 preserveAspectRatio: {aspect_ratio}")
                                
                                if aspect_ratio == "none":
                                    print("❌ ПРОБЛЕМА: preserveAspectRatio='none' вызывает растягивание!")
                                    print("💡 РЕШЕНИЕ: Заменить на 'xMidYMid slice' для правильного кропа")
                            
                            # Проверяем размеры
                            width_match = re.search(r'width="([^"]+)"', image_element)
                            height_match = re.search(r'height="([^"]+)"', image_element)
                            
                            if width_match and height_match:
                                width = width_match.group(1)
                                height = height_match.group(1)
                                print(f"📏 Размеры image: {width}x{height}")
                                
                                # Анализируем пропорции
                                try:
                                    w = float(width)
                                    h = float(height)
                                    ratio = w / h
                                    print(f"📊 Соотношение сторон: {ratio:.3f}")
                                    
                                    if ratio != 1.0:
                                        print(f"⚠️ Image не квадратный ({w}x{h}), но headshot должен быть 120x120")
                                except:
                                    pass

def test_headshot_fix():
    """Тестируем исправление headshot"""
    
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ HEADSHOT")
    print("=" * 50)
    
    # Читаем main.svg
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print("❌ Файл main.svg не найден")
        return
    
    # Анализируем структуру
    analyze_headshot_structure(svg_content)
    
    # Применяем исправление
    fixed_svg = fix_headshot_aspect_ratio(svg_content)
    
    # Сохраняем результат
    if fixed_svg != svg_content:
        with open('main_fixed_headshot.svg', 'w', encoding='utf-8') as f:
            f.write(fixed_svg)
        
        print(f"\n✅ Файл исправлен и сохранен: main_fixed_headshot.svg")
        
        # Проверяем что исправление применилось
        if 'preserveAspectRatio="xMidYMid slice"' in fixed_svg:
            print("✅ preserveAspectRatio исправлен на 'xMidYMid slice'")
        else:
            print("❌ preserveAspectRatio не был исправлен")
    else:
        print("\n❌ Файл не был изменен")

if __name__ == "__main__":
    test_headshot_fix()