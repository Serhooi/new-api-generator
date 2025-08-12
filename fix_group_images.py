#!/usr/bin/env python3
"""
Исправление для обработки изображений в группах
"""

import sqlite3
import re

DATABASE_PATH = 'templates.db'

def safe_escape_for_svg(text):
    """Безопасное экранирование для SVG"""
    if not text:
        return text
    
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

def process_svg_with_groups(svg_content, replacements):
    """Обработка SVG с поддержкой групп"""
    
    processed_svg = svg_content
    
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Проверяем, является ли поле изображением
        if any(keyword in dyno_field.lower() for keyword in ['image', 'photo', 'headshot']):
            print(f"🖼️ Обрабатываю изображение: {dyno_field}")
            
            safe_url = str(replacement).replace('&', '&amp;')
            
            # Ищем элемент с id
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            if match:
                print(f"   ✅ Найден элемент с id: {dyno_field}")
                
                element_content = match.group(0)
                pattern_id = None
                
                # Ищем pattern в fill атрибуте самого элемента
                fill_pattern = r'fill="url\(#([^)]+)\)"'
                fill_match = re.search(fill_pattern, element_content)
                
                if fill_match:
                    pattern_id = fill_match.group(1)
                    print(f"   🎯 Найден pattern в элементе: {pattern_id}")
                else:
                    # Если это группа, ищем pattern во вложенных элементах
                    if element_content.startswith('<g'):
                        print(f"   🔍 Это группа, ищу pattern во вложенных элементах...")
                        
                        # Ищем всю группу с содержимым
                        group_pattern = f'<g[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</g>'
                        group_match = re.search(group_pattern, processed_svg, re.DOTALL)
                        
                        if group_match:
                            group_content = group_match.group(1)
                            
                            # Ищем fill в любом вложенном элементе
                            nested_fill_match = re.search(fill_pattern, group_content)
                            if nested_fill_match:
                                pattern_id = nested_fill_match.group(1)
                                print(f"   🎯 Найден pattern во вложенном элементе: {pattern_id}")
                
                if pattern_id:
                    # Ищем pattern блок
                    pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                    pattern_match = re.search(pattern_block_pattern, processed_svg, re.DOTALL)
                    
                    if pattern_match:
                        pattern_content = pattern_match.group(1)
                        
                        # Ищем image элемент в pattern (прямой или через use)
                        image_replaced = False
                        
                        # Сначала ищем use элемент
                        use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
                        use_match = re.search(use_pattern, pattern_content)
                        
                        if use_match:
                            image_id = use_match.group(1)
                            print(f"   🔗 Найден use элемент: #{image_id}")
                            
                            # Ищем соответствующий image элемент
                            image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
                            image_match = re.search(image_pattern, processed_svg)
                            
                            if image_match:
                                old_image = image_match.group(0)
                                new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', old_image)
                                new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                                
                                processed_svg = processed_svg.replace(old_image, new_image)
                                print(f"   ✅ Изображение через use заменено: {safe_url[:50]}...")
                                image_replaced = True
                        
                        # Если use не найден, ищем прямой image
                        if not image_replaced:
                            direct_image_pattern = r'<image[^>]*href="[^"]*"[^>]*/?>'
                            direct_image_match = re.search(direct_image_pattern, pattern_content)
                            
                            if direct_image_match:
                                old_image = direct_image_match.group(0)
                                new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', old_image)
                                new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                                
                                processed_svg = processed_svg.replace(old_image, new_image)
                                print(f"   ✅ Прямое изображение заменено: {safe_url[:50]}...")
                                image_replaced = True
                        
                        if not image_replaced:
                            print(f"   ⚠️ Image элемент не найден в pattern")
                    else:
                        print(f"   ⚠️ Pattern блок {pattern_id} не найден")
                else:
                    print(f"   ⚠️ Pattern не найден в элементе или группе")
            else:
                print(f"   ❌ Элемент с id {dyno_field} не найден")
        else:
            # Обработка текстовых полей (упрощенная)
            print(f"🔤 Обрабатываю текстовое поле: {dyno_field}")
            
            safe_replacement = safe_escape_for_svg(str(replacement))
            
            # Ищем text элемент
            element_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
            
            def replace_element_content(match):
                full_element = match.group(0)
                element_content = match.group(1)
                
                # Заменяем содержимое первого tspan
                def replace_tspan_content(tspan_match):
                    opening_tag = tspan_match.group(1)
                    old_content = tspan_match.group(2)
                    closing_tag = tspan_match.group(3)
                    
                    return opening_tag + safe_replacement + closing_tag
                
                tspan_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
                new_content = re.sub(tspan_pattern, replace_tspan_content, element_content, count=1)
                
                return full_element.replace(element_content, new_content)
            
            new_svg = re.sub(element_pattern, replace_element_content, processed_svg, flags=re.DOTALL)
            
            if new_svg != processed_svg:
                processed_svg = new_svg
                print(f"   ✅ Поле {dyno_field} успешно заменено!")
            else:
                print(f"   ❌ Поле {dyno_field} не найдено")
    
    return processed_svg

def test_real_templates():
    """Тестирует обработку реальных загруженных шаблонов"""
    
    print("🧪 ТЕСТ РЕАЛЬНЫХ ШАБЛОНОВ С ПОДДЕРЖКОЙ ГРУПП")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем реальные загруженные шаблоны
    cursor.execute("SELECT id, name, template_role, svg_content FROM templates WHERE category = 'uploaded'")
    templates = cursor.fetchall()
    
    if not templates:
        print("❌ Загруженные шаблоны не найдены")
        return
    
    # Тестовые данные
    test_data = {
        "dyno.propertyimage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1080&h=600&fit=crop",
        "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
        "dyno.propertyimage2": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop",
        "dyno.propertyaddress": "123 Main Street, Beverly Hills, CA 90210",
        "dyno.price": "$450,000",
        "dyno.name": "John Smith",
        "dyno.phone": "(555) 123-4567",
        "dyno.email": "john@example.com"
    }
    
    for template_id, name, role, svg_content in templates:
        print(f"\n🎯 Тестирую: {name} ({role.upper()})")
        
        try:
            processed_svg = process_svg_with_groups(svg_content, test_data)
            
            # Сохраняем результат
            output_filename = f"test_real_{role}_{template_id[:8]}.svg"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(processed_svg)
            
            print(f"\n   ✅ Результат сохранен: {output_filename}")
            
            # Специальная проверка для photo шаблона
            if role == 'photo' and 'dyno.propertyimage2' in test_data:
                test_url = test_data['dyno.propertyimage2']
                escaped_url = test_url.replace('&', '&amp;')
                
                if escaped_url in processed_svg:
                    print(f"   ✅ dyno.propertyimage2 НАЙДЕН в результате!")
                else:
                    print(f"   ❌ dyno.propertyimage2 НЕ найден в результате")
                    
                    # Ищем что там есть
                    image_urls = re.findall(r'href="([^"]*)"', processed_svg)
                    print(f"      🔍 Найденные URL: {image_urls}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    test_real_templates()