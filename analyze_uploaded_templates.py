#!/usr/bin/env python3
"""
Анализ загруженных SVG шаблонов
"""

import sqlite3
import re

DATABASE_PATH = 'templates.db'

def analyze_templates():
    """Анализирует все загруженные шаблоны"""
    
    print("🔍 АНАЛИЗ ЗАГРУЖЕННЫХ ШАБЛОНОВ")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем все шаблоны
    cursor.execute("SELECT id, name, template_role, dyno_fields, svg_content FROM templates ORDER BY template_role, name")
    templates = cursor.fetchall()
    
    if not templates:
        print("❌ Шаблоны не найдены")
        return
    
    print(f"📊 Найдено {len(templates)} шаблонов")
    
    for template_id, name, role, dyno_fields_str, svg_content in templates:
        print(f"\n🎯 {name} ({role.upper()})")
        print(f"   ID: {template_id}")
        
        # Анализируем dyno поля
        dyno_fields = dyno_fields_str.split(',') if dyno_fields_str else []
        print(f"   📋 Dyno поля ({len(dyno_fields)}):")
        
        for field in dyno_fields:
            field = field.strip()
            if field:
                # Проверяем, есть ли элемент с этим ID в SVG
                element_pattern = f'<[^>]*id="{re.escape(field)}"[^>]*>'
                match = re.search(element_pattern, svg_content)
                
                if match:
                    element = match.group(0)
                    
                    # Определяем тип элемента
                    if any(keyword in field.lower() for keyword in ['image', 'photo', 'headshot']):
                        # Это изображение
                        fill_match = re.search(r'fill="url\(#([^)]+)\)"', element)
                        if fill_match:
                            pattern_id = fill_match.group(1)
                            print(f"      ✅ {field} (изображение, pattern: {pattern_id})")
                        else:
                            print(f"      ⚠️ {field} (изображение, но нет pattern)")
                    else:
                        # Это текст
                        print(f"      ✅ {field} (текст)")
                else:
                    print(f"      ❌ {field} (элемент не найден в SVG)")
        
        # Специальная проверка для propertyimage2
        if role == 'photo':
            print(f"\n   🔍 СПЕЦИАЛЬНАЯ ПРОВЕРКА PROPERTYIMAGE2:")
            
            if 'dyno.propertyimage2' in dyno_fields:
                print(f"      ✅ dyno.propertyimage2 есть в списке полей")
                
                # Ищем элемент
                element_pattern = r'<[^>]*id="dyno\.propertyimage2"[^>]*>'
                match = re.search(element_pattern, svg_content)
                
                if match:
                    element = match.group(0)
                    print(f"      ✅ Элемент найден: {element[:100]}...")
                    
                    # Проверяем pattern
                    fill_match = re.search(r'fill="url\(#([^)]+)\)"', element)
                    if fill_match:
                        pattern_id = fill_match.group(1)
                        print(f"      ✅ Pattern ID: {pattern_id}")
                        
                        # Ищем pattern блок
                        pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                        pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
                        
                        if pattern_match:
                            print(f"      ✅ Pattern блок найден")
                            
                            # Ищем image внутри pattern
                            image_pattern = r'<image[^>]*href="[^"]*"[^>]*/?>'
                            image_match = re.search(image_pattern, pattern_match.group(1))
                            
                            if image_match:
                                print(f"      ✅ Image элемент найден в pattern")
                            else:
                                print(f"      ❌ Image элемент НЕ найден в pattern")
                        else:
                            print(f"      ❌ Pattern блок НЕ найден")
                    else:
                        print(f"      ❌ Fill с pattern НЕ найден")
                else:
                    print(f"      ❌ Элемент с id='dyno.propertyimage2' НЕ найден")
            else:
                print(f"      ❌ dyno.propertyimage2 НЕТ в списке полей")
                
                # Ищем похожие поля
                similar_fields = [f for f in dyno_fields if 'property' in f.lower() or 'image' in f.lower()]
                if similar_fields:
                    print(f"      🔍 Похожие поля: {similar_fields}")
    
    # Проверяем карусели
    print(f"\n🎠 КАРУСЕЛИ:")
    cursor.execute("SELECT id, name, main_template_id, photo_template_id FROM carousels")
    carousels = cursor.fetchall()
    
    for carousel_id, name, main_id, photo_id in carousels:
        print(f"   📦 {name} ({carousel_id})")
        print(f"      Main: {main_id}")
        print(f"      Photo: {photo_id}")
    
    conn.close()

if __name__ == "__main__":
    analyze_templates()