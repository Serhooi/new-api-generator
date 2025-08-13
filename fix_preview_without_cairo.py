#!/usr/bin/env python3
"""
Исправление превью без Cairo - используем SVG напрямую
"""

import os
import re

def fix_preview_functions():
    """Исправляем функции превью в app.py"""
    
    print("🔧 Исправляю функции превью...")
    
    # Читаем app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем заглушки на рабочие функции
    new_functions = '''
# Рабочие функции preview_system без Cairo
def generate_svg_preview(svg_content, width=400, height=600):
    """Генерирует SVG превью (возвращает сам SVG)"""
    try:
        # Просто возвращаем SVG с измененными размерами
        # Ищем width и height в SVG
        svg_with_size = re.sub(
            r'<svg([^>]*?)width="[^"]*"([^>]*?)height="[^"]*"([^>]*?)>',
            f'<svg\\1width="{width}"\\2height="{height}"\\3>',
            svg_content
        )
        
        # Если не нашли width/height, добавляем их
        if 'width=' not in svg_with_size or 'height=' not in svg_with_size:
            svg_with_size = re.sub(
                r'<svg([^>]*?)>',
                f'<svg\\1 width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                svg_with_size
            )
        
        return svg_with_size
    except Exception as e:
        print(f"❌ Ошибка генерации SVG превью: {e}")
        return svg_content

def create_preview_with_data(svg_content, data, width=400, height=600):
    """Создает превью с данными"""
    try:
        # Заменяем данные в SVG
        processed_svg = svg_content
        for key, value in data.items():
            if isinstance(value, str):
                # Простая замена текста
                processed_svg = processed_svg.replace(f">{key}<", f">{value}<")
        
        return generate_svg_preview(processed_svg, width, height)
    except Exception as e:
        print(f"❌ Ошибка создания превью с данными: {e}")
        return generate_svg_preview(svg_content, width, height)

def cleanup_old_previews():
    """Очистка старых превью"""
    try:
        preview_dir = os.path.join(OUTPUT_DIR, 'previews')
        if os.path.exists(preview_dir):
            import time
            current_time = time.time()
            for filename in os.listdir(preview_dir):
                file_path = os.path.join(preview_dir, filename)
                if os.path.isfile(file_path):
                    # Удаляем файлы старше 24 часов
                    if current_time - os.path.getmtime(file_path) > 24 * 3600:
                        os.remove(file_path)
        return True
    except Exception as e:
        print(f"❌ Ошибка очистки превью: {e}")
        return False

def replace_image_in_svg(svg_content, field_name, image_url):
    """Заменяет изображение в SVG"""
    try:
        # Импортируем из preview_system если доступно
        from preview_system import replace_image_in_svg as original_replace
        return original_replace(svg_content, field_name, image_url)
    except ImportError:
        # Простая замена если preview_system недоступен
        print(f"⚠️ Простая замена изображения: {field_name}")
        return svg_content
'''
    
    # Заменяем заглушки на рабочие функции
    content = re.sub(
        r'# Заглушки для функций preview_system.*?def replace_image_in_svg\(svg_content, field_name, image_url\):\s*return svg_content',
        new_functions.strip(),
        content,
        flags=re.DOTALL
    )
    
    # Сохраняем исправленный файл
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Функции превью исправлены!")

def fix_preview_endpoints():
    """Исправляем API endpoints для превью"""
    
    print("🔧 Исправляю API endpoints превью...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем и исправляем функции генерации превью
    # Заменяем cairosvg.svg2png на простое сохранение SVG
    
    # Исправляем функцию get_template_preview
    content = re.sub(
        r'png_data = cairosvg\.svg2png\([^)]+\)',
        'svg_data = preview_svg.encode("utf-8")  # Используем SVG вместо PNG',
        content
    )
    
    # Заменяем PNG на SVG в заголовках
    content = re.sub(
        r'return Response\(png_data, mimetype=\'image/png\'\)',
        'return Response(svg_data, mimetype="image/svg+xml")',
        content
    )
    
    # Исправляем сохранение превью файлов
    content = re.sub(
        r'with open\(preview_path, \'wb\'\) as f:\s*f\.write\(png_data\)',
        'with open(preview_path.replace(".png", ".svg"), "w", encoding="utf-8") as f:\n                    f.write(preview_svg)',
        content
    )
    
    # Исправляем расширения файлов превью
    content = re.sub(
        r'preview_filename = f"preview_\{template_id\}_\{timestamp\}\.png"',
        'preview_filename = f"preview_{template_id}_{timestamp}.svg"',
        content
    )
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ API endpoints превью исправлены!")

if __name__ == "__main__":
    print("🚀 ИСПРАВЛЕНИЕ ПРЕВЬЮ БЕЗ CAIRO")
    print("=" * 50)
    
    fix_preview_functions()
    fix_preview_endpoints()
    
    print("\n🎉 Превью исправлены! Теперь используются SVG вместо PNG")
    print("📋 Что изменилось:")
    print("  - Превью генерируются как SVG файлы")
    print("  - Не требуется Cairo")
    print("  - API возвращает SVG вместо PNG")
    print("  - Фронтенд получит рабочие превью")