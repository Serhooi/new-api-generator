#!/usr/bin/env python3
"""
Финальное решение для замены изображений в SVG файлах.
Правильно обрабатывает как pattern, так и image элементы с base64 данными.
"""

import re
import base64
from PIL import Image
import io

def image_to_base64(image_path):
    """Конвертирует изображение в base64 строку"""
    try:
        with Image.open(image_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Сохраняем в буфер как JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # Кодируем в base64
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{img_base64}"
    except Exception as e:
        print(f"Ошибка при конвертации изображения {image_path}: {e}")
        return None

def replace_image_in_svg(svg_content, field_name, new_image_path):
    """
    Заменяет изображение в SVG файле.
    Ищет группу с именем поля, находит связанный pattern и заменяет соответствующий image элемент.
    """
    print(f"Заменяем изображение для поля: {field_name}")
    
    # Конвертируем новое изображение в base64
    new_base64 = image_to_base64(new_image_path)
    if not new_base64:
        print(f"Не удалось конвертировать изображение: {new_image_path}")
        return svg_content
    
    # Ищем группу с именем поля
    group_regex = rf'<g[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*>'
    group_match = re.search(group_regex, svg_content, re.IGNORECASE)
    
    if not group_match:
        print(f"Группа для поля {field_name} не найдена")
        return svg_content
    
    print(f"Найдена группа: {group_match.group()}")
    
    # Извлекаем содержимое группы до закрывающего тега
    group_start = group_match.end()
    group_end_match = re.search(r'</g>', svg_content[group_start:])
    
    if not group_end_match:
        print("Не найден закрывающий тег </g>")
        return svg_content
    
    group_content = svg_content[group_start:group_start + group_end_match.start()]
    print(f"Содержимое группы: {group_content}")
    
    # Ищем fill="url(#pattern_id)" в группе
    pattern_ref_match = re.search(r'fill="url\(#([^)]+)\)"', group_content)
    if not pattern_ref_match:
        print("Ссылка на pattern не найдена в группе")
        return svg_content
    
    pattern_id = pattern_ref_match.group(1)
    print(f"Найден pattern ID: {pattern_id}")
    
    # Ищем pattern с этим ID
    pattern_regex = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>'
    pattern_match = re.search(pattern_regex, svg_content)
    
    if not pattern_match:
        print(f"Pattern с ID {pattern_id} не найден")
        return svg_content
    
    print(f"Найден pattern: {pattern_match.group()}")
    
    # Извлекаем содержимое pattern до закрывающего тега
    pattern_start = pattern_match.end()
    pattern_end_match = re.search(r'</pattern>', svg_content[pattern_start:])
    
    if not pattern_end_match:
        print("Не найден закрывающий тег </pattern>")
        return svg_content
    
    pattern_content = svg_content[pattern_start:pattern_start + pattern_end_match.start()]
    print(f"Содержимое pattern: {pattern_content}")
    
    # Ищем use элемент в pattern
    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
    if not use_match:
        print("Use элемент не найден в pattern")
        return svg_content
    
    image_id = use_match.group(1)
    print(f"Найден image ID: {image_id}")
    
    # Ищем и заменяем image элемент с этим ID
    image_regex = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*xlink:href=")[^"]*("[^>]*>)'
    
    def replace_image_href(match):
        return match.group(1) + new_base64 + match.group(2)
    
    new_svg_content = re.sub(image_regex, replace_image_href, svg_content)
    
    if new_svg_content != svg_content:
        print(f"✅ Изображение для поля {field_name} успешно заменено!")
        return new_svg_content
    else:
        print(f"❌ Изображение для поля {field_name} не было заменено")
        return svg_content

def test_image_replacement():
    """Тестируем замену изображения в photo.svg"""
    
    # Читаем SVG файл
    try:
        with open('photo.svg', 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print("Файл photo.svg не найден")
        return
    
    print("Исходный SVG загружен")
    print(f"Размер файла: {len(svg_content)} символов")
    
    # Заменяем изображение (используем любое доступное изображение для теста)
    test_image = "test_image.jpg"  # Замените на путь к реальному изображению
    
    # Создаем тестовое изображение если его нет
    try:
        # Проверяем существует ли файл
        with open(test_image, 'rb'):
            pass
    except FileNotFoundError:
        print("Создаем тестовое изображение...")
        # Создаем простое тестовое изображение
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image, 'JPEG')
        print(f"Создано тестовое изображение: {test_image}")
    
    # Заменяем изображение
    new_svg_content = replace_image_in_svg(svg_content, 'propertyimage2', test_image)
    
    # Сохраняем результат
    output_file = 'photo_modified.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_svg_content)
    
    print(f"Результат сохранен в: {output_file}")
    
    # Проверяем изменения
    if new_svg_content != svg_content:
        print("✅ Файл был изменен!")
        
        # Показываем разницу в размерах
        size_diff = len(new_svg_content) - len(svg_content)
        print(f"Изменение размера: {size_diff:+d} символов")
    else:
        print("❌ Файл не был изменен")

if __name__ == "__main__":
    test_image_replacement()