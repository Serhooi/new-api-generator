#!/usr/bin/env python3
"""
Отладка проблемы с dyno.propertyimage2
"""

import sqlite3
import re

DATABASE_PATH = 'templates.db'

def debug_propertyimage2():
    """Отладка поиска dyno.propertyimage2 в SVG шаблонах"""
    
    print("🔍 ОТЛАДКА DYNO.PROPERTYIMAGE2")
    print("=" * 50)
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем все photo шаблоны
    cursor.execute("SELECT id, name, svg_content FROM templates WHERE template_role = 'photo'")
    photo_templates = cursor.fetchall()
    
    print(f"📊 Найдено {len(photo_templates)} photo шаблонов")
    
    for template_id, name, svg_content in photo_templates:
        print(f"\n🎯 Анализирую шаблон: {name} ({template_id})")
        
        # Ищем все dyno поля в SVG
        dyno_patterns = [
            r'id="(dyno\.[^"]*)"',        # id="dyno.field"
            r"id='(dyno\.[^']*)'",        # id='dyno.field'
            r'\{\{(dyno\.[^}]+)\}\}',     # {{dyno.field}}
            r'\{(dyno\.[^}]+)\}',         # {dyno.field}
        ]
        
        all_dyno_fields = set()
        for pattern in dyno_patterns:
            matches = re.findall(pattern, svg_content)
            all_dyno_fields.update(matches)
        
        print(f"   📋 Найденные dyno поля:")
        for field in sorted(all_dyno_fields):
            print(f"      - {field}")
        
        # Специально ищем propertyimage2
        if 'dyno.propertyimage2' in all_dyno_fields:
            print(f"   ✅ dyno.propertyimage2 НАЙДЕН!")
            
            # Ищем элемент с этим ID
            element_pattern = r'<[^>]*id="dyno\.propertyimage2"[^>]*>'
            match = re.search(element_pattern, svg_content)
            if match:
                element = match.group(0)
                print(f"   📄 Элемент: {element[:100]}...")
                
                # Проверяем, есть ли fill с pattern
                fill_match = re.search(r'fill="url\(#([^)]+)\)"', element)
                if fill_match:
                    pattern_id = fill_match.group(1)
                    print(f"   🎯 Pattern ID: {pattern_id}")
                    
                    # Ищем pattern блок
                    pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                    pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
                    if pattern_match:
                        print(f"   ✅ Pattern блок найден")
                    else:
                        print(f"   ❌ Pattern блок НЕ найден")
                else:
                    print(f"   ❌ Fill с pattern НЕ найден")
            else:
                print(f"   ❌ Элемент с id='dyno.propertyimage2' НЕ найден")
        else:
            print(f"   ❌ dyno.propertyimage2 НЕ найден в этом шаблоне")
            
            # Ищем похожие поля
            similar_fields = [field for field in all_dyno_fields if 'property' in field.lower() or 'image' in field.lower()]
            if similar_fields:
                print(f"   🔍 Похожие поля: {similar_fields}")
    
    conn.close()

if __name__ == "__main__":
    debug_propertyimage2()