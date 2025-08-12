#!/usr/bin/env python3
"""
Интеграционный тест системы замены изображений с основной системой preview.
"""

from final_image_replacement_solution import replace_image_in_svg
from PIL import Image
import json
import os

def test_integration_with_preview_system():
    """Тестируем интеграцию с системой preview"""
    
    # Создаем тестовое изображение
    test_image = "integration_test.jpg"
    if not os.path.exists(test_image):
        img = Image.new('RGB', (300, 400), color='purple')
        img.save(test_image, 'JPEG', quality=85)
        print(f"Создано тестовое изображение: {test_image}")
    
    # Читаем исходный SVG
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print("Файл photo.svg не найден")
        return False
    
    # Тестовые данные как в реальной системе
    test_data = {
        "propertyimage2": test_image
    }
    
    print("=== Тест интеграции с системой preview ===")
    print(f"Исходный размер SVG: {len(svg_content)} символов")
    
    # Заменяем изображения
    modified_svg = svg_content
    for field_name, image_path in test_data.items():
        print(f"\nОбрабатываем поле: {field_name}")
        print(f"Путь к изображению: {image_path}")
        
        if os.path.exists(image_path):
            modified_svg = replace_image_in_svg(modified_svg, field_name, image_path)
        else:
            print(f"❌ Файл изображения не найден: {image_path}")
    
    # Сохраняем результат
    output_file = 'photo_integration_test.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_svg)
    
    print(f"\n=== Результаты ===")
    print(f"Результат сохранен в: {output_file}")
    print(f"Финальный размер SVG: {len(modified_svg)} символов")
    
    size_diff = len(modified_svg) - len(svg_content)
    print(f"Изменение размера: {size_diff:+d} символов")
    
    # Проверяем что изменения применились
    if modified_svg != svg_content:
        print("✅ SVG был успешно модифицирован!")
        return True
    else:
        print("❌ SVG не был изменен")
        return False

def simulate_preview_api_call():
    """Симулируем вызов API preview с заменой изображений"""
    
    print("\n=== Симуляция API вызова ===")
    
    # Создаем тестовые данные как в реальном API
    api_data = {
        "template": "photo.svg",
        "data": {
            "propertyimage2": "integration_test.jpg"
        }
    }
    
    print(f"API данные: {json.dumps(api_data, indent=2)}")
    
    # Читаем шаблон
    template_file = api_data["template"]
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print(f"❌ Шаблон не найден: {template_file}")
        return False
    
    print(f"Загружен шаблон: {template_file}")
    
    # Применяем замены изображений
    modified_svg = svg_content
    image_fields = {k: v for k, v in api_data["data"].items() if any(word in k.lower() for word in ['image', 'photo', 'picture'])}
    
    print(f"Найдено полей изображений: {len(image_fields)}")
    print(f"Поля изображений: {list(image_fields.keys())}")
    
    for field_name, image_path in image_fields.items():
        print(f"Заменяем {field_name} -> {image_path}")
        
        if os.path.exists(image_path):
            modified_svg = replace_image_in_svg(modified_svg, field_name, image_path)
        else:
            print(f"⚠️  Изображение не найдено: {image_path}")
    
    # Возвращаем результат (как в реальном API)
    result = {
        "success": modified_svg != svg_content,
        "svg": modified_svg,
        "original_size": len(svg_content),
        "modified_size": len(modified_svg),
        "size_diff": len(modified_svg) - len(svg_content)
    }
    
    print(f"\n=== API Response ===")
    print(f"Success: {result['success']}")
    print(f"Size change: {result['size_diff']:+d} bytes")
    
    return result

if __name__ == "__main__":
    print("Запуск интеграционных тестов...")
    
    # Тест интеграции
    integration_success = test_integration_with_preview_system()
    
    # Симуляция API
    api_result = simulate_preview_api_call()
    
    print(f"\n=== Итоговые результаты ===")
    print(f"Интеграционный тест: {'✅ ПРОЙДЕН' if integration_success else '❌ ПРОВАЛЕН'}")
    print(f"API симуляция: {'✅ ПРОЙДЕНА' if api_result['success'] else '❌ ПРОВАЛЕНА'}")
    
    if integration_success and api_result['success']:
        print("\n🎉 Все тесты успешно пройдены!")
        print("Система замены изображений готова к интеграции!")
    else:
        print("\n⚠️  Некоторые тесты провалены. Требуется доработка.")