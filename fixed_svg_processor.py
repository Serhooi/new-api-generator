#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ SVG ПРОЦЕССОР С ПРАВИЛЬНЫМ ПОИСКОМ DYNO ПОЛЕЙ
=========================================================

Исправляет проблему с обнаружением dyno полей в формате id="dyno.field"
"""

import re

def has_dyno_fields_fixed(svg_content):
    """
    ИСПРАВЛЕННАЯ функция проверки наличия dyno полей в SVG
    
    Ищет dyno поля в разных форматах:
    1. {{dyno.field}} - в тексте
    2. {dyno.field} - в тексте  
    3. id="dyno.field" - в атрибутах элементов
    4. dyno.field - в любом месте
    """
    
    patterns = [
        r'\{\{dyno\.[^}]+\}\}',     # {{dyno.field}}
        r'\{dyno\.[^}]+\}',         # {dyno.field}
        r'id="dyno\.[^"]*"',        # id="dyno.field"
        r"id='dyno\.[^']*'",        # id='dyno.field'
        r'dyno\.[a-zA-Z][a-zA-Z0-9]*'  # dyno.field (как ID или в тексте)
    ]
    
    found_fields = []
    
    for pattern in patterns:
        matches = re.findall(pattern, svg_content)
        if matches:
            found_fields.extend(matches)
    
    return len(found_fields) > 0, found_fields

def extract_dyno_fields_from_svg(svg_content):
    """
    Извлекает все dyno поля из SVG с их типами
    """
    
    # Ищем dyno поля в id атрибутах
    id_pattern = r'id="(dyno\.[^"]*)"'
    id_matches = re.findall(id_pattern, svg_content)
    
    # Ищем dyno поля в тексте
    text_patterns = [
        r'\{\{(dyno\.[^}]+)\}\}',
        r'\{(dyno\.[^}]+)\}'
    ]
    
    text_matches = []
    for pattern in text_patterns:
        text_matches.extend(re.findall(pattern, svg_content))
    
    # Объединяем все найденные поля
    all_fields = list(set(id_matches + text_matches))
    
    # Определяем типы полей
    field_types = {}
    for field in all_fields:
        if any(img_keyword in field.lower() for img_keyword in ['image', 'photo', 'picture', 'logo', 'headshot']):
            field_types[field] = 'image'
        else:
            field_types[field] = 'text'
    
    return {
        'fields': all_fields,
        'types': field_types,
        'count': len(all_fields),
        'has_dyno': len(all_fields) > 0
    }

def process_svg_with_id_replacement(svg_content, replacements):
    """
    Обрабатывает SVG с заменой dyno полей в формате id="dyno.field"
    """
    
    result = svg_content
    
    print("🔄 Обрабатываю SVG с ID заменами...")
    
    for key, value in replacements.items():
        # Убираем префикс dyno. если он есть
        clean_key = key.replace('dyno.', '')
        
        # Формируем возможные варианты ключей
        possible_keys = [
            f'dyno.{clean_key}',
            f'dyno.{key}',
            key,
            clean_key
        ]
        
        for possible_key in possible_keys:
            # Заменяем в id атрибутах
            id_pattern = f'id="{possible_key}"'
            if id_pattern in result:
                print(f"✅ Найден элемент с id='{possible_key}', заменяю...")
                
                # Для изображений
                if any(img_keyword in possible_key.lower() for img_keyword in ['image', 'photo', 'picture', 'logo', 'headshot']):
                    # Заменяем href или xlink:href в элементах image
                    image_pattern = f'<image[^>]*id="{possible_key}"[^>]*>'
                    image_match = re.search(image_pattern, result)
                    if image_match:
                        image_element = image_match.group(0)
                        # Заменяем href на новое изображение
                        new_image = re.sub(r'(href|xlink:href)="[^"]*"', f'href="{value}"', image_element)
                        result = result.replace(image_element, new_image)
                        print(f"   🖼️ Заменено изображение: {possible_key}")
                
                # Для текста
                else:
                    # Ищем текстовые элементы с этим id
                    text_pattern = f'<text[^>]*id="{possible_key}"[^>]*>([^<]*)</text>'
                    text_match = re.search(text_pattern, result)
                    if text_match:
                        old_text_element = text_match.group(0)
                        old_text_content = text_match.group(1)
                        new_text_element = old_text_element.replace(old_text_content, str(value))
                        result = result.replace(old_text_element, new_text_element)
                        print(f"   📝 Заменен текст: {possible_key} -> {value}")
                    
                    # Также ищем в tspan элементах
                    tspan_pattern = f'<tspan[^>]*>([^<]*)</tspan>'
                    parent_pattern = f'<text[^>]*id="{possible_key}"[^>]*>(.*?)</text>'
                    parent_match = re.search(parent_pattern, result, re.DOTALL)
                    if parent_match:
                        parent_content = parent_match.group(1)
                        tspan_matches = re.findall(tspan_pattern, parent_content)
                        if tspan_matches:
                            # Заменяем содержимое первого tspan
                            new_parent_content = re.sub(tspan_pattern, f'<tspan>{value}</tspan>', parent_content, count=1)
                            result = result.replace(parent_content, new_parent_content)
                            print(f"   📝 Заменен tspan: {possible_key} -> {value}")
    
    print("✅ SVG обработан")
    return result

if __name__ == "__main__":
    # Тестируем на примере
    test_svg = '''
    <svg>
        <text id="dyno.headline">Test Headline</text>
        <text id="dyno.price">$500,000</text>
        <image id="dyno.logo" href="old-logo.jpg"/>
    </svg>
    '''
    
    # Проверяем поиск dyno полей
    has_dyno, fields = has_dyno_fields_fixed(test_svg)
    print(f"Has dyno: {has_dyno}")
    print(f"Fields: {fields}")
    
    # Извлекаем детальную информацию
    field_info = extract_dyno_fields_from_svg(test_svg)
    print(f"Field info: {field_info}")
    
    # Тестируем замену
    replacements = {
        'dyno.headline': 'New Headline',
        'dyno.price': '$750,000',
        'dyno.logo': 'new-logo.jpg'
    }
    
    processed = process_svg_with_id_replacement(test_svg, replacements)
    print(f"Processed SVG: {processed}")

