#!/usr/bin/env python3
"""
Быстрый тест dyno.propertyimage2
"""

import sqlite3
import re

DATABASE_PATH = 'templates.db'

def quick_test():
    """Быстрый тест обработки dyno.propertyimage2"""
    
    print("⚡ БЫСТРЫЙ ТЕСТ DYNO.PROPERTYIMAGE2")
    print("=" * 40)
    
    # Получаем photo шаблон
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, svg_content FROM templates WHERE template_role = 'photo' AND category = 'uploaded' LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        print("❌ Загруженный photo шаблон не найден")
        return
    
    template_id, name, svg_content = result
    print(f"📄 Тестирую: {name}")
    
    # Ищем dyno.propertyimage2
    element_pattern = r'<g[^>]*id="dyno\.propertyimage2"[^>]*>(.*?)</g>'
    match = re.search(element_pattern, svg_content, re.DOTALL)
    
    if match:
        print("✅ Найдена группа dyno.propertyimage2")
        
        group_content = match.group(1)
        
        # Ищем fill в группе
        fill_match = re.search(r'fill="url\(#([^)]+)\)"', group_content)
        if fill_match:
            pattern_id = fill_match.group(1)
            print(f"✅ Pattern найден: {pattern_id}")
            
            # Ищем pattern блок
            pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
            pattern_match = re.search(pattern_pattern, svg_content, re.DOTALL)
            
            if pattern_match:
                print("✅ Pattern блок найден")
                
                pattern_content = pattern_match.group(1)
                
                # Ищем image в pattern
                if '<image' in pattern_content:
                    print("✅ Image элемент найден в pattern")
                    
                    # Тестируем замену
                    test_url = "https://test.com/image.jpg"
                    
                    # Заменяем href
                    new_pattern_content = re.sub(r'href="[^"]*"', f'href="{test_url}"', pattern_content)
                    
                    if test_url in new_pattern_content:
                        print("✅ ЗАМЕНА РАБОТАЕТ!")
                        print(f"   Новый URL: {test_url}")
                    else:
                        print("❌ Замена не работает")
                else:
                    print("❌ Image элемент НЕ найден в pattern")
            else:
                print("❌ Pattern блок НЕ найден")
        else:
            print("❌ Fill с pattern НЕ найден в группе")
    else:
        print("❌ Группа dyno.propertyimage2 НЕ найдена")
    
    conn.close()

if __name__ == "__main__":
    quick_test()