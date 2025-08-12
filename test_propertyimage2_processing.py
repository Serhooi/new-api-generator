#!/usr/bin/env python3
"""
Тест обработки dyno.propertyimage2
"""

import sqlite3
from app import process_svg_font_perfect

DATABASE_PATH = 'templates.db'

def test_propertyimage2_processing():
    """Тестирует обработку dyno.propertyimage2"""
    
    print("🧪 ТЕСТ ОБРАБОТКИ DYNO.PROPERTYIMAGE2")
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
        processed_svg = process_svg_font_perfect(svg_content, test_replacements)
        
        print(f"✅ Обработка завершена успешно!")
        
        # Проверяем, что URL заменился
        if test_replacements['dyno.propertyimage2'] in processed_svg:
            print(f"✅ dyno.propertyimage2 URL найден в результате!")
        else:
            print(f"❌ dyno.propertyimage2 URL НЕ найден в результате")
            
        # Проверяем, что остались ли нераспознанные dyno поля
        import re
        remaining_dyno = re.findall(r'dyno\.[a-zA-Z][a-zA-Z0-9]*', processed_svg)
        if remaining_dyno:
            print(f"⚠️ Остались нераспознанные dyno поля: {remaining_dyno}")
        else:
            print(f"✅ Все dyno поля обработаны!")
            
        # Сохраняем результат для проверки
        with open('test_propertyimage2_result.svg', 'w', encoding='utf-8') as f:
            f.write(processed_svg)
        print(f"💾 Результат сохранен в test_propertyimage2_result.svg")
        
    except Exception as e:
        print(f"❌ Ошибка обработки: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    test_propertyimage2_processing()