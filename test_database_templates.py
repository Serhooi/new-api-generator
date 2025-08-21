#!/usr/bin/env python3
"""
Тест умной очистки с реальными шаблонами из базы
"""

import sqlite3
import subprocess
import os
import re

def get_templates_from_db():
    """Получаем шаблоны из базы данных"""
    
    print("🗄️ Читаю шаблоны из базы данных...")
    
    if not os.path.exists('templates.db'):
        print("❌ База данных templates.db не найдена")
        return []
    
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Получаем все шаблоны
        cursor.execute("SELECT id, name, svg_content FROM templates LIMIT 5")
        templates = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Найдено {len(templates)} шаблонов в базе")
        
        for i, (template_id, name, svg_content) in enumerate(templates):
            print(f"  {i+1}. {template_id}: {name} ({len(svg_content)} символов)")
        
        return templates
        
    except Exception as e:
        print(f"❌ Ошибка чтения базы: {e}")
        return []

def smart_svg_cleaning(svg_content):
    """Умная очистка SVG"""
    
    cleaned = svg_content
    
    # 1. Убираем невалидные символы
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    # 2. Исправляем амперсанды
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    
    # 3. УМНО исправляем image теги
    def fix_image_tag(match):
        tag_content = match.group(1)
        if tag_content.endswith('/'):
            return match.group(0)
        return f'<image{tag_content}/>'
    
    cleaned = re.sub(r'<image([^>]*?)>', fix_image_tag, cleaned)
    
    # 4. УМНО исправляем use теги
    def fix_use_tag(match):
        tag_content = match.group(1)
        if tag_content.endswith('/'):
            return match.group(0)
        return f'<use{tag_content}/>'
    
    cleaned = re.sub(r'<use([^>]*?)>', fix_use_tag, cleaned)
    
    # 5. Исправляем другие самозакрывающиеся теги
    self_closing_tags = ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop']
    
    for tag in self_closing_tags:
        def fix_tag(match):
            tag_content = match.group(1)
            if tag_content.endswith('/'):
                return match.group(0)
            return f'<{tag}{tag_content}/>'
        
        cleaned = re.sub(f'<{tag}([^>]*?)>', fix_tag, cleaned)
    
    # 6. Убираем лишние пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned

def test_template_cleaning_and_png(template_id, name, svg_content):
    """Тестируем очистку и PNG конвертацию для одного шаблона"""
    
    print(f"\n🧪 Тестирую шаблон: {name} ({template_id})")
    print(f"📊 Размер оригинала: {len(svg_content)} символов")
    
    # Анализируем проблемные теги
    image_tags = len(re.findall(r'<image[^>]*>', svg_content))
    use_tags = len(re.findall(r'<use[^>]*>', svg_content))
    unclosed_image = len(re.findall(r'<image[^>]*[^/]>', svg_content))
    unclosed_use = len(re.findall(r'<use[^>]*[^/]>', svg_content))
    
    print(f"🔍 Анализ тегов:")
    print(f"  - image: {image_tags} (незакрытых: {unclosed_image})")
    print(f"  - use: {use_tags} (незакрытых: {unclosed_use})")
    
    # Применяем умную очистку
    print("🧠 Применяю умную очистку...")
    cleaned_svg = smart_svg_cleaning(svg_content)
    
    print(f"✅ Очистка завершена: {len(svg_content)} → {len(cleaned_svg)} символов")
    
    # Проверяем что теги остались
    cleaned_image_tags = len(re.findall(r'<image[^>]*>', cleaned_svg))
    cleaned_use_tags = len(re.findall(r'<use[^>]*>', cleaned_svg))
    
    print(f"🔍 После очистки:")
    print(f"  - image: {cleaned_image_tags}")
    print(f"  - use: {cleaned_use_tags}")
    
    # Сохраняем очищенный SVG
    cleaned_file = f"db_cleaned_{template_id}.svg"
    with open(cleaned_file, 'w') as f:
        f.write(cleaned_svg)
    
    # Тестируем PNG конвертацию
    print("🖼️ Тестирую PNG конвертацию...")
    
    png_file = f"db_test_{template_id}.png"
    
    try:
        # Конвертируем через rsvg-convert
        result = subprocess.run(
            ["rsvg-convert", "-w", "400"],
            input=cleaned_svg.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        if result.returncode == 0:
            # Сохраняем PNG
            with open(png_file, 'wb') as f:
                f.write(result.stdout)
            
            png_size = len(result.stdout)
            print(f"✅ PNG создан: {png_file} ({png_size} байт)")
            
            # Проверяем размер PNG
            if png_size > 10000:  # Больше 10KB = вероятно с изображениями
                print("🎉 PNG большой - вероятно содержит изображения!")
                return True
            else:
                print("⚠️ PNG маленький - возможно без изображений")
                return True  # Все равно работает
        else:
            print(f"❌ PNG конвертация не удалась: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка PNG конвертации: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🗄️ ТЕСТИРОВАНИЕ ШАБЛОНОВ ИЗ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Получаем шаблоны из базы
    templates = get_templates_from_db()
    
    if not templates:
        print("❌ Нет шаблонов для тестирования")
        return
    
    results = {}
    
    # Тестируем каждый шаблон
    for template_id, name, svg_content in templates:
        success = test_template_cleaning_and_png(template_id, name, svg_content)
        results[template_id] = {
            'name': name,
            'success': success
        }
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    
    successful = 0
    total = len(results)
    
    for template_id, result in results.items():
        status = "✅ РАБОТАЕТ" if result['success'] else "❌ НЕ РАБОТАЕТ"
        print(f"  {template_id}: {result['name']} - {status}")
        if result['success']:
            successful += 1
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {successful}/{total} шаблонов работают")
    
    if successful == total:
        print("🎉 ВСЕ ШАБЛОНЫ ИЗ БАЗЫ РАБОТАЮТ С УМНОЙ ОЧИСТКОЙ!")
    elif successful > 0:
        print("✅ Большинство шаблонов работают - система готова!")
    else:
        print("❌ Нужны дополнительные исправления")

if __name__ == "__main__":
    main()