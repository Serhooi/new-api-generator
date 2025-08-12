#!/usr/bin/env python3
"""
Тест улучшенной системы замены изображений с поддержкой разных форматов и размеров.
"""

from final_image_replacement_solution import replace_image_in_svg, image_to_base64
from PIL import Image
import os

def create_test_images():
    """Создает тестовые изображения разных размеров и цветов"""
    
    test_images = [
        ("test_red.jpg", (200, 300), "red"),
        ("test_blue.jpg", (400, 600), "blue"), 
        ("test_green.jpg", (100, 150), "green"),
        ("test_large.jpg", (800, 1200), "yellow")
    ]
    
    for filename, size, color in test_images:
        if not os.path.exists(filename):
            print(f"Создаем {filename} размером {size} цвета {color}")
            img = Image.new('RGB', size, color=color)
            img.save(filename, 'JPEG', quality=85)
    
    return [img[0] for img in test_images]

def test_multiple_replacements():
    """Тестируем замену изображения несколько раз подряд"""
    
    # Создаем тестовые изображения
    test_images = create_test_images()
    
    # Читаем исходный SVG
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            original_svg = f.read()
    except FileNotFoundError:
        print("Файл photo.svg не найден")
        return
    
    current_svg = original_svg
    
    # Тестируем замену разными изображениями
    for i, test_image in enumerate(test_images):
        print(f"\n=== Тест {i+1}: Замена на {test_image} ===")
        
        # Заменяем изображение
        new_svg = replace_image_in_svg(current_svg, 'propertyimage2', test_image)
        
        # Сохраняем результат
        output_file = f'photo_test_{i+1}.svg'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_svg)
        
        print(f"Результат сохранен в: {output_file}")
        
        # Проверяем изменения
        if new_svg != current_svg:
            size_diff = len(new_svg) - len(current_svg)
            print(f"✅ Изображение заменено! Изменение размера: {size_diff:+d} символов")
            current_svg = new_svg
        else:
            print("❌ Изображение не было заменено")
    
    print(f"\n=== Итоговая статистика ===")
    final_size_diff = len(current_svg) - len(original_svg)
    print(f"Общее изменение размера файла: {final_size_diff:+d} символов")
    print(f"Исходный размер: {len(original_svg)} символов")
    print(f"Финальный размер: {len(current_svg)} символов")

def test_base64_conversion():
    """Тестируем конвертацию изображений в base64"""
    
    test_images = create_test_images()
    
    print("\n=== Тест конвертации в base64 ===")
    
    for test_image in test_images:
        print(f"\nТестируем {test_image}:")
        
        # Получаем информацию об изображении
        try:
            with Image.open(test_image) as img:
                print(f"  Размер: {img.size}")
                print(f"  Режим: {img.mode}")
                print(f"  Формат: {img.format}")
        except Exception as e:
            print(f"  Ошибка при чтении: {e}")
            continue
        
        # Конвертируем в base64
        base64_data = image_to_base64(test_image)
        if base64_data:
            print(f"  ✅ Base64 длина: {len(base64_data)} символов")
            print(f"  Начало: {base64_data[:50]}...")
        else:
            print(f"  ❌ Ошибка конвертации")

if __name__ == "__main__":
    print("Запуск расширенных тестов замены изображений...")
    
    # Тест конвертации
    test_base64_conversion()
    
    # Тест множественных замен
    test_multiple_replacements()
    
    print("\nВсе тесты завершены!")