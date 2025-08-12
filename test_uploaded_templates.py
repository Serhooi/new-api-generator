#!/usr/bin/env python3
"""
Тест обработки загруженных шаблонов
"""

import sqlite3
from test_simple_propertyimage2 import simple_process_svg

DATABASE_PATH = 'templates.db'

def test_uploaded_templates():
    """Тестирует обработку загруженных шаблонов"""
    
    print("🧪 ТЕСТ ЗАГРУЖЕННЫХ ШАБЛОНОВ")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Получаем последние загруженные шаблоны
    cursor.execute("SELECT id, name, template_role, svg_content FROM templates WHERE category = 'uploaded' ORDER BY created_at DESC")
    templates = cursor.fetchall()
    
    if not templates:
        print("❌ Загруженные шаблоны не найдены")
        print("   Сначала загрузите шаблоны с помощью: python3 upload_templates.py")
        return
    
    print(f"📊 Найдено {len(templates)} загруженных шаблонов")
    
    # Тестовые данные
    test_data = {
        # Для main слайда
        "dyno.propertyimage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1080&h=600&fit=crop",
        "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
        
        # Для photo слайда
        "dyno.propertyimage2": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop",
        "dyno.propertyimage3": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=1080&h=800&fit=crop",
        
        # Общие поля
        "dyno.propertyaddress": "123 Main Street, Beverly Hills, CA 90210",
        "dyno.price": "$450,000",
        "dyno.name": "John Smith",
        "dyno.phone": "(555) 123-4567",
        "dyno.email": "john@example.com",
        "dyno.agentName": "John Smith",
        "dyno.agentPhone": "(555) 123-4567",
        "dyno.agentEmail": "john@example.com"
    }
    
    for template_id, name, role, svg_content in templates:
        print(f"\n🎯 Тестирую: {name} ({role.upper()})")
        print(f"   ID: {template_id}")
        
        try:
            # Обрабатываем шаблон
            processed_svg = simple_process_svg(svg_content, test_data)
            
            # Сохраняем результат
            output_filename = f"test_uploaded_{role}_{template_id[:8]}.svg"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(processed_svg)
            
            print(f"   ✅ Обработка завершена, результат: {output_filename}")
            
            # Специальная проверка для photo шаблона
            if role == 'photo':
                if 'dyno.propertyimage2' in test_data:
                    test_url = test_data['dyno.propertyimage2']
                    escaped_url = test_url.replace('&', '&amp;')
                    
                    if escaped_url in processed_svg:
                        print(f"   ✅ dyno.propertyimage2 НАЙДЕН в результате!")
                    else:
                        print(f"   ❌ dyno.propertyimage2 НЕ найден в результате")
                        
                        # Ищем что там есть
                        import re
                        image_urls = re.findall(r'href="([^"]*)"', processed_svg)
                        print(f"      🔍 Найденные URL: {image_urls}")
            
        except Exception as e:
            print(f"   ❌ Ошибка обработки: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    test_uploaded_templates()