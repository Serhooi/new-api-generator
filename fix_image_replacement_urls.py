#!/usr/bin/env python3
"""
Исправленная система замены изображений в SVG с поддержкой URL'ов.
Правильно обрабатывает связи pattern -> image.
"""

import re
import requests
import base64
from PIL import Image
import io

def download_and_convert_image(url):
    """Скачивает изображение по URL и конвертирует в base64"""
    try:
        print(f"📥 Скачиваю изображение: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Открываем изображение
        img = Image.open(io.BytesIO(response.content))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Сохраняем в буфер как JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Кодируем в base64
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        base64_url = f"data:image/jpeg;base64,{img_base64}"
        
        print(f"✅ Изображение конвертировано в base64 ({len(base64_url)} символов)")
        return base64_url
        
    except Exception as e:
        print(f"❌ Ошибка при скачивании/конвертации изображения {url}: {e}")
        return None

def replace_image_url_in_svg(svg_content, field_name, new_image_url):
    """
    Заменяет изображение в SVG файле на URL или base64.
    Поддерживает как прямую замену URL, так и конвертацию в base64.
    """
    print(f"🖼️ Обрабатываю изображение: {field_name}")
    
    # Сначала ищем элемент с id равным field_name (прямое соответствие)
    direct_element_regex = rf'(<[^>]*id="{re.escape(field_name)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    direct_match = re.search(direct_element_regex, svg_content)
    
    if direct_match:
        print(f"✅ Найден прямой элемент с id: {field_name}")
        # Прямая замена URL
        new_svg_content = re.sub(direct_element_regex, 
                                lambda m: m.group(1) + new_image_url + m.group(2), 
                                svg_content)
        
        if new_svg_content != svg_content:
            print(f"✅ Изображение {field_name} заменено на: {new_image_url}")
            return new_svg_content
    
    # Если прямого элемента нет, ищем через pattern
    print(f"🔍 Ищу через pattern для поля: {field_name}")
    
    # Ищем элемент с id содержащим field_name и fill="url(#pattern_id)"
    element_regex = rf'<[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*fill="url\(#([^)]+)\)"[^>]*>'
    element_match = re.search(element_regex, svg_content, re.IGNORECASE)
    
    if not element_match:
        print(f"❌ Элемент с id содержащим {field_name} не найден")
        return svg_content
    
    pattern_id = element_match.group(1)
    print(f"✅ Найден pattern: {pattern_id}")
    
    # Ищем pattern с этим ID
    pattern_regex = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
    pattern_match = re.search(pattern_regex, svg_content, re.DOTALL)
    
    if not pattern_match:
        print(f"❌ Pattern с ID {pattern_id} не найден")
        return svg_content
    
    pattern_content = pattern_match.group(1)
    
    # Ищем use элемент в pattern
    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
    if not use_match:
        print(f"❌ Use элемент не найден в pattern {pattern_id}")
        return svg_content
    
    image_id = use_match.group(1)
    print(f"✅ Найден image ID: {image_id}")
    
    # Ищем и заменяем image элемент с этим ID
    image_regex = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    
    # Определяем что делать с изображением
    if new_image_url.startswith('http'):
        # Если это URL, можем либо оставить URL, либо конвертировать в base64
        # Для совместимости конвертируем в base64
        base64_data = download_and_convert_image(new_image_url)
        if base64_data:
            replacement_url = base64_data
        else:
            # Если конвертация не удалась, используем исходный URL
            replacement_url = new_image_url
    else:
        # Если это уже base64 или локальный файл
        replacement_url = new_image_url
    
    def replace_image_href(match):
        return match.group(1) + replacement_url + match.group(2)
    
    new_svg_content = re.sub(image_regex, replace_image_href, svg_content)
    
    if new_svg_content != svg_content:
        print(f"✅ Изображение {field_name} заменено на: {replacement_url[:50]}...")
        return new_svg_content
    else:
        print(f"❌ Изображение {field_name} не было заменено")
        return svg_content

def test_main_svg_replacement():
    """Тестируем замену изображений в main.svg"""
    
    print("🧪 ТЕСТ: Замена изображений в main.svg")
    print("=" * 60)
    
    # Читаем SVG файл
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print("❌ Файл main.svg не найден")
        return
    
    print(f"📄 Размер SVG файла: {len(svg_content)} символов")
    
    # Тестовые данные
    test_data = {
        'dyno.propertyimage': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop',
        'dyno.agentheadshot': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face',
        'dyno.logo': 'https://via.placeholder.com/142x56/4F46E5/FFFFFF?text=LOGO'
    }
    
    # Заменяем изображения
    modified_svg = svg_content
    successful_replacements = 0
    
    for field_name, image_url in test_data.items():
        print(f"\n🔄 Обрабатываю поле: {field_name} = {image_url}")
        
        original_size = len(modified_svg)
        modified_svg = replace_image_url_in_svg(modified_svg, field_name, image_url)
        new_size = len(modified_svg)
        
        if new_size != original_size:
            successful_replacements += 1
            print(f"📊 Изменение размера: {new_size - original_size:+d} символов")
    
    # Сохраняем результат
    output_file = 'main_fixed_images.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_svg)
    
    print(f"\n✅ Результат сохранен в: {output_file}")
    print(f"📊 Всего заменено: {successful_replacements}/{len(test_data)} изображений")
    
    # Проверяем каждое поле
    for field_name in test_data.keys():
        if field_name in ['dyno.propertyimage', 'dyno.agentheadshot', 'dyno.logo']:
            # Проверяем что URL заменен
            if 'unsplash.com' in modified_svg or 'placeholder.com' in modified_svg:
                print(f"✅ {field_name}: URL успешно заменен!")
            else:
                print(f"❌ {field_name}: URL НЕ заменен")

def analyze_svg_structure(filename):
    """Анализирует структуру SVG файла"""
    
    print(f"\n🔍 АНАЛИЗ СТРУКТУРЫ: {filename}")
    print("=" * 60)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден")
        return
    
    # Ищем dyno поля
    dyno_fields = re.findall(r'id="(dyno\.[^"]+)"', svg_content)
    print(f"🔍 Найдены dyno поля: {dyno_fields}")
    
    # Ищем image элементы
    image_elements = re.findall(r'<image[^>]*id="([^"]+)"', svg_content)
    print(f"🖼️ Найдены image элементы: {image_elements}")
    
    # Ищем pattern элементы
    pattern_elements = re.findall(r'<pattern[^>]*id="([^"]+)"', svg_content)
    print(f"🎨 Найдены pattern элементы: {pattern_elements}")
    
    # Анализируем связи pattern -> image
    print(f"\n🔗 АНАЛИЗ СВЯЗЕЙ PATTERN -> IMAGE:")
    for pattern_id in pattern_elements:
        pattern_regex = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
        pattern_match = re.search(pattern_regex, svg_content, re.DOTALL)
        if pattern_match:
            pattern_content = pattern_match.group(1)
            use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"', pattern_content)
            if use_match:
                image_id = use_match.group(1)
                print(f"  {pattern_id} -> {image_id}")

if __name__ == "__main__":
    print("🚀 ИСПРАВЛЕННАЯ СИСТЕМА ЗАМЕНЫ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    
    # Анализируем структуру
    analyze_svg_structure('main.svg')
    
    # Тестируем замену
    test_main_svg_replacement()
    
    print("\n🎯 ТЕСТ ЗАВЕРШЕН!")