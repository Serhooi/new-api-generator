#!/usr/bin/env python3
"""
Простой тест генерации карусели без Cairo
"""

import sqlite3
import uuid
import json
import os
from test_simple_propertyimage2 import simple_process_svg

DATABASE_PATH = 'templates.db'
OUTPUT_DIR = 'output'

def generate_carousel_simple():
    """Генерирует карусель без использования Cairo"""
    
    print("🎠 ПРОСТАЯ ГЕНЕРАЦИЯ КАРУСЕЛИ")
    print("=" * 50)
    
    # Создаем директории
    os.makedirs(f'{OUTPUT_DIR}/carousel', exist_ok=True)
    
    # Получаем шаблоны
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, svg_content FROM templates WHERE template_role = 'main' LIMIT 1")
    main_result = cursor.fetchone()
    
    cursor.execute("SELECT id, name, svg_content FROM templates WHERE template_role = 'photo' LIMIT 1")
    photo_result = cursor.fetchone()
    
    if not main_result or not photo_result:
        print("❌ Шаблоны не найдены")
        return
    
    main_id, main_name, main_svg = main_result
    photo_id, photo_name, photo_svg = photo_result
    
    print(f"📄 Main шаблон: {main_name} ({main_id})")
    print(f"📄 Photo шаблон: {photo_name} ({photo_id})")
    
    # Тестовые данные
    test_data = {
        # Для main слайда
        "dyno.propertyimage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1080&h=600&fit=crop",
        "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
        
        # Для photo слайда
        "dyno.propertyimage2": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop",
        
        # Общие поля
        "dyno.propertyaddress": "123 Main Street, Beverly Hills, CA 90210",
        "dyno.price": "$450,000",
        "dyno.name": "John Smith",
        "dyno.phone": "(555) 123-4567"
    }
    
    carousel_id = str(uuid.uuid4())
    
    print(f"\n🔄 Генерирую main слайд...")
    
    # Обрабатываем main слайд
    main_replacements = {k: v for k, v in test_data.items() if k != 'dyno.propertyimage2'}
    processed_main_svg = simple_process_svg(main_svg, main_replacements)
    
    main_filename = f"carousel_{carousel_id}_main.svg"
    main_path = f"{OUTPUT_DIR}/carousel/{main_filename}"
    
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(processed_main_svg)
    
    print(f"✅ Main слайд сохранен: {main_filename}")
    
    print(f"\n🔄 Генерирую photo слайд...")
    
    # Обрабатываем photo слайд
    photo_replacements = test_data.copy()  # Все поля, включая dyno.propertyimage2
    processed_photo_svg = simple_process_svg(photo_svg, photo_replacements)
    
    photo_filename = f"carousel_{carousel_id}_photo.svg"
    photo_path = f"{OUTPUT_DIR}/carousel/{photo_filename}"
    
    with open(photo_path, 'w', encoding='utf-8') as f:
        f.write(processed_photo_svg)
    
    print(f"✅ Photo слайд сохранен: {photo_filename}")
    
    # Проверяем результат
    print(f"\n🔍 Проверяю результат photo слайда...")
    
    if test_data['dyno.propertyimage2'].replace('&', '&amp;') in processed_photo_svg:
        print(f"✅ dyno.propertyimage2 найден в photo слайде!")
    else:
        print(f"❌ dyno.propertyimage2 НЕ найден в photo слайде")
        
        # Ищем что там есть
        import re
        image_urls = re.findall(r'href="([^"]*)"', processed_photo_svg)
        print(f"   Найденные URL изображений: {image_urls}")
    
    # Сохраняем информацию о карусели
    result = {
        "carousel_id": carousel_id,
        "slides": [
            {"filename": main_filename, "path": main_path, "type": "main"},
            {"filename": photo_filename, "path": photo_path, "type": "photo"}
        ]
    }
    
    result_filename = f"carousel_{carousel_id}_info.json"
    with open(f"{OUTPUT_DIR}/carousel/{result_filename}", 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Карусель создана!")
    print(f"   ID: {carousel_id}")
    print(f"   Main слайд: {main_filename}")
    print(f"   Photo слайд: {photo_filename}")
    print(f"   Информация: {result_filename}")
    
    conn.close()
    return result

if __name__ == "__main__":
    generate_carousel_simple()