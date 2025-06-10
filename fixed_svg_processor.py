#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ ФУНКЦИЯ ОБРАБОТКИ SVG
Полностью переписанная функция для правильной замены dyno полей
"""

import re
import html

def safe_escape_for_svg_fixed(text):
    """Безопасное экранирование для SVG - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    if not text:
        return text
    
    # Заменяем & ПЕРВЫМ (важно!)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    # Дополнительно экранируем специальные символы
    text = text.replace('"', '&quot;')  # Правая двойная кавычка
    text = text.replace('"', '&quot;')  # Левая двойная кавычка
    text = text.replace('—', '&mdash;')  # Длинное тире
    text = text.replace('–', '&ndash;')  # Короткое тире
    
    return text

def process_svg_completely_fixed(svg_content, replacements):
    """
    ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ обработка SVG
    Заменяет ВСЕ dyno поля правильно
    """
    
    processed_svg = svg_content
    
    # 1. ЗАМЕНА ТЕКСТОВЫХ ПОЛЕЙ В TSPAN
    def replace_tspan_content(match):
        full_match = match.group(0)
        tspan_content = match.group(1)
        
        # Ищем dyno поле в содержимом
        for dyno_field, replacement in replacements.items():
            if dyno_field in tspan_content:
                # Заменяем ТОЛЬКО содержимое, сохраняя все атрибуты
                safe_replacement = safe_escape_for_svg_fixed(str(replacement))
                new_content = tspan_content.replace(dyno_field, safe_replacement)
                return full_match.replace(tspan_content, new_content)
        
        return full_match
    
    # Паттерн для поиска <tspan>содержимое</tspan>
    tspan_pattern = r'<tspan[^>]*>(.*?)</tspan>'
    processed_svg = re.sub(tspan_pattern, replace_tspan_content, processed_svg, flags=re.DOTALL)
    
    # 2. ЗАМЕНА ТЕКСТОВЫХ ПОЛЕЙ В TEXT (если не в tspan)
    def replace_text_content(match):
        full_match = match.group(0)
        text_content = match.group(1)
        
        # Ищем dyno поле в содержимом
        for dyno_field, replacement in replacements.items():
            if dyno_field in text_content:
                safe_replacement = safe_escape_for_svg_fixed(str(replacement))
                new_content = text_content.replace(dyno_field, safe_replacement)
                return full_match.replace(text_content, new_content)
        
        return full_match
    
    # Паттерн для text элементов без tspan
    text_pattern = r'<text[^>]*>([^<]*)</text>'
    processed_svg = re.sub(text_pattern, replace_text_content, processed_svg, flags=re.DOTALL)
    
    # 3. ЗАМЕНА ID АТРИБУТОВ (для полей которые не заменились)
    for dyno_field, replacement in replacements.items():
        # Ищем элементы с id="dyno.field"
        id_pattern = f'id="{dyno_field}"'
        if id_pattern in processed_svg:
            print(f"🔍 Найден элемент с id: {dyno_field}")
            
            # Для текстовых элементов - заменяем содержимое
            if 'image' not in dyno_field.lower() and 'headshot' not in dyno_field.lower() and 'logo' not in dyno_field.lower():
                # Ищем текстовый элемент с этим ID
                element_pattern = f'<text[^>]*id="{dyno_field}"[^>]*>(.*?)</text>'
                def replace_element_content(match):
                    safe_replacement = safe_escape_for_svg_fixed(str(replacement))
                    return match.group(0).replace(match.group(1), safe_replacement)
                
                processed_svg = re.sub(element_pattern, replace_element_content, processed_svg, flags=re.DOTALL)
    
    # 4. ЗАМЕНА ИЗОБРАЖЕНИЙ В PATTERNS
    for dyno_field, replacement in replacements.items():
        if 'image' in dyno_field.lower() or 'headshot' in dyno_field.lower() or 'logo' in dyno_field.lower():
            # Простые URL без параметров для избежания XML ошибок
            simple_url = str(replacement).split('?')[0]
            
            # Заменяем в pattern элементах
            pattern_regex = r'<image[^>]*href="[^"]*"[^>]*>'
            def replace_image_href(match):
                return re.sub(r'href="[^"]*"', f'href="{simple_url}"', match.group(0))
            
            processed_svg = re.sub(pattern_regex, replace_image_href, processed_svg)
    
    return processed_svg

# Тестирование функции
if __name__ == "__main__":
    # Тестовые данные
    test_svg = '''
    <text id="dyno.date"><tspan>MAY 17 2025</tspan></text>
    <text id="dyno.price"><tspan>$5.000.000</tspan></text>
    <text id="dyno.propertyaddress"><tspan>Address</tspan></text>
    '''
    
    test_replacements = {
        'dyno.date': 'DECEMBER 15, 2025',
        'dyno.price': '$3,250,000',
        'dyno.propertyaddress': '2468 Ocean View Drive, Malibu, CA 90265'
    }
    
    result = process_svg_completely_fixed(test_svg, test_replacements)
    print("Результат обработки:")
    print(result)

