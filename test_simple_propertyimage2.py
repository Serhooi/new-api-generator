#!/usr/bin/env python3
"""
Простой тест обработки dyno.propertyimage2 без Cairo
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

def simple_process_svg(svg_content, replacements):
    """Упрощенная обработка SVG для тестирования"""
    
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
                
                # Ищем pattern в fill атрибуте
                fill_pattern = f'fill="url\\(#([^)]+)\\)"'
                fill_match = re.search(fill_pattern, match.group(0))
                
                if fill_match:
                    pattern_id = fill_match.group(1)
                    print(f"   🎯 Найден pattern: {pattern_id}")
                    
                    # Ищем pattern блок
                    pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                    pattern_match = re.search(pattern_block_pattern, processed_svg, re.DOTALL)
                    
                    if pattern_match:
                        pattern_content = pattern_match.group(1)
                        
                        # Ищем image элемент внутри pattern
                        image_pattern = r'<image[^>]*href="[^"]*"[^>]*/?>'
                        image_match = re.search(image_pattern, pattern_content)
                        
                        if image_match:
                            old_image = image_match.group(0)
                            new_image = old_image
                            
                            # Заменяем URL
                            new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
                            
                            # Применяем замену
                            processed_svg = processed_svg.replace(old_image, new_image)
                            print(f"   ✅ Изображение заменено: {safe_url[:50]}...")
                        else:
                            print(f"   ⚠️ Image элемент не найден в pattern")
                    else:
                        print(f"   ⚠️ Pattern блок {pattern_id} не найден")
                else:
                    print(f"   ⚠️ Fill с pattern не найден")
            else:
                print(f"   ❌ Элемент с id {dyno_field} не найден")
        else:
            # Обработка текстовых полей
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

def test_propertyimage2_processing():
    """Тестирует обработку dyno.propertyimage2"""
    
    print("🧪 ПРОСТОЙ ТЕСТ ОБРАБОТКИ DYNO.PROPERTYIMAGE2")
    print("=" * 50)
    
    # Получаем photo шаблон из базы
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, svg_content FROM templates WHERE template_role = 'photo' LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        print("❌ Photo шаблон не найден")
        return
    
    template_id, name, svg_content = result
    print(f"📄 Тестирую шаблон: {name} ({template_id})")
    
    # Тестовые данные
    test_replacements = {
        'dyno.propertyimage2': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop',
        'dyno.agentheadshot': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
        'dyno.propertyaddress': '123 Main Street, Beverly Hills, CA 90210',
        'dyno.name': 'John Smith',
        'dyno.phone': '(555) 123-4567'
    }
    
    print(f"\n📋 Тестовые данные:")
    for field, value in test_replacements.items():
        print(f"   {field}: {value[:50]}...")
    
    print(f"\n🔄 Запускаю обработку SVG...")
    
    try:
        # Обрабатываем SVG
        processed_svg = simple_process_svg(svg_content, test_replacements)
        
        print(f"\n✅ Обработка завершена!")
        
        # Проверяем результат
        if test_replacements['dyno.propertyimage2'] in processed_svg:
            print(f"✅ dyno.propertyimage2 URL найден в результате!")
        else:
            print(f"❌ dyno.propertyimage2 URL НЕ найден в результате")
            
        # Сохраняем результат
        with open('test_simple_propertyimage2_result.svg', 'w', encoding='utf-8') as f:
            f.write(processed_svg)
        print(f"💾 Результат сохранен в test_simple_propertyimage2_result.svg")
        
    except Exception as e:
        print(f"❌ Ошибка обработки: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    test_propertyimage2_processing()