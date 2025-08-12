#!/usr/bin/env python3
"""
Скрипт для исправления логики URL в app.py - убираем JPG, используем только SVG
"""

def fix_url_logic():
    """
    Исправляет логику URL в app.py для использования только SVG
    """
    
    # Читаем файл
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем логику URL - убираем JPG, используем только SVG
    old_logic = '''        # Создаем URL для изображений (используем Supabase URL если на Render, иначе локальные)
        if is_render and supabase:
            # На Render - используем Supabase URL
            main_image_url = main_url if main_jpg_success else main_url.replace('.jpg', '.svg')
            photo_image_url = photo_url if photo_jpg_success else photo_url.replace('.jpg', '.svg')
        else:
            # Локально - используем локальные URL
            main_image_url = f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}'
            photo_image_url = f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}')'''
    
    new_logic = '''        # Создаем URL для изображений - используем только SVG
        if is_render and supabase:
            # На Render - используем SVG URL из Supabase
            main_image_url = main_url
            photo_image_url = photo_url
        else:
            # Локально - используем SVG URL
            main_image_url = f'/output/carousel/{main_svg_filename}'
            photo_image_url = f'/output/carousel/{photo_svg_filename}')'''
    
    # Заменяем все вхождения
    content = content.replace(old_logic, new_logic)
    
    # Также заменяем поле format - всегда SVG
    content = content.replace("'format': 'svg' if is_render and supabase else ('jpg' if main_jpg_success and photo_jpg_success else 'svg')", "'format': 'svg'")
    
    # Записываем исправленный файл
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Логика URL в app.py исправлена! Теперь используется только SVG.")

if __name__ == '__main__':
    fix_url_logic()
