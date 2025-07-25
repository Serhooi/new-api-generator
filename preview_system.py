#!/usr/bin/env python3
"""
СИСТЕМА ПРЕВЬЮ ДЛЯ SVG ФЛАЕРОВ
=============================

Позволяет пользователю видеть превью SVG перед финальной генерацией
"""

import os
import uuid
import cairosvg
from PIL import Image
import io
import base64

def generate_svg_preview(svg_content, preview_type='png', width=400, height=300):
    """
    Генерирует превью SVG в разных форматах
    
    Args:
        svg_content: Содержимое SVG
        preview_type: 'png', 'base64', 'thumbnail'
        width: Ширина превью
        height: Высота превью
    
    Returns:
        dict с данными превью
    """
    try:
        print(f"🖼️ Генерирую превью SVG ({preview_type}, {width}x{height})")
        
        # Убеждаемся что SVG валидный
        if not svg_content.strip().startswith('<svg'):
            raise ValueError("Некорректный SVG контент")
        
        # Добавляем namespace если отсутствует
        if 'xmlns=' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
        
        if preview_type == 'png':
            return generate_png_preview(svg_content, width, height)
        elif preview_type == 'base64':
            return generate_base64_preview(svg_content, width, height)
        elif preview_type == 'thumbnail':
            return generate_thumbnail_preview(svg_content)
        else:
            raise ValueError(f"Неподдерживаемый тип превью: {preview_type}")
            
    except Exception as e:
        print(f"❌ Ошибка генерации превью: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def generate_png_preview(svg_content, width=400, height=300):
    """Генерирует PNG превью и сохраняет в файл"""
    try:
        # Генерируем уникальное имя файла
        preview_id = str(uuid.uuid4())
        preview_filename = f"preview_{preview_id}.png"
        preview_path = os.path.join('output', 'previews', preview_filename)
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(preview_path), exist_ok=True)
        
        # Конвертируем SVG в PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            background_color='white'
        )
        
        # Сохраняем файл
        with open(preview_path, 'wb') as f:
            f.write(png_data)
        
        # Получаем размер файла
        file_size = os.path.getsize(preview_path)
        
        print(f"✅ PNG превью создано: {preview_path} ({file_size} байт)")
        
        return {
            'success': True,
            'preview_id': preview_id,
            'filename': preview_filename,
            'path': preview_path,
            'url': f'/output/previews/{preview_filename}',
            'width': width,
            'height': height,
            'file_size': file_size,
            'format': 'png'
        }
        
    except Exception as e:
        print(f"❌ Ошибка создания PNG превью: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def generate_base64_preview(svg_content, width=400, height=300):
    """Генерирует base64 превью для встраивания в HTML"""
    try:
        # Конвертируем SVG в PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            background_color='white'
        )
        
        # Конвертируем в base64
        base64_data = base64.b64encode(png_data).decode('utf-8')
        data_url = f"data:image/png;base64,{base64_data}"
        
        print(f"✅ Base64 превью создано ({len(base64_data)} символов)")
        
        return {
            'success': True,
            'base64': base64_data,
            'data_url': data_url,
            'width': width,
            'height': height,
            'format': 'base64'
        }
        
    except Exception as e:
        print(f"❌ Ошибка создания base64 превью: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def generate_thumbnail_preview(svg_content):
    """Генерирует маленький thumbnail для списков"""
    try:
        # Маленький размер для thumbnail
        width, height = 150, 100
        
        # Конвертируем SVG в PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            background_color='white'
        )
        
        # Дополнительно оптимизируем через PIL
        img = Image.open(io.BytesIO(png_data))
        
        # Оптимизируем для веба
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='PNG', optimize=True, quality=85)
        optimized_data = output_buffer.getvalue()
        
        # Генерируем уникальное имя файла
        thumbnail_id = str(uuid.uuid4())
        thumbnail_filename = f"thumb_{thumbnail_id}.png"
        thumbnail_path = os.path.join('output', 'previews', thumbnail_filename)
        
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        # Сохраняем оптимизированный thumbnail
        with open(thumbnail_path, 'wb') as f:
            f.write(optimized_data)
        
        file_size = os.path.getsize(thumbnail_path)
        
        print(f"✅ Thumbnail создан: {thumbnail_path} ({file_size} байт)")
        
        return {
            'success': True,
            'thumbnail_id': thumbnail_id,
            'filename': thumbnail_filename,
            'path': thumbnail_path,
            'url': f'/output/previews/{thumbnail_filename}',
            'width': width,
            'height': height,
            'file_size': file_size,
            'format': 'thumbnail'
        }
        
    except Exception as e:
        print(f"❌ Ошибка создания thumbnail: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def create_preview_with_data(svg_content, replacements, preview_type='png'):
    """
    Создает превью SVG с заполненными данными
    
    Args:
        svg_content: Исходный SVG шаблон
        replacements: Словарь замен для dyno полей
        preview_type: Тип превью
    
    Returns:
        dict с данными превью
    """
    try:
        print(f"🎨 Создаю превью с данными ({len(replacements)} замен)")
        
        # Импортируем функцию обработки SVG
        from app import process_svg_font_perfect
        
        # Обрабатываем SVG с заменами
        processed_svg = process_svg_font_perfect(svg_content, replacements)
        
        # Генерируем превью
        preview_result = generate_svg_preview(processed_svg, preview_type)
        
        if preview_result['success']:
            preview_result['replacements_count'] = len(replacements)
            preview_result['has_data'] = True
            print(f"✅ Превью с данными создано успешно")
        
        return preview_result
        
    except Exception as e:
        print(f"❌ Ошибка создания превью с данными: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def cleanup_old_previews(max_age_hours=24):
    """Очищает старые превью файлы"""
    try:
        import time
        
        preview_dir = os.path.join('output', 'previews')
        if not os.path.exists(preview_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for filename in os.listdir(preview_dir):
            file_path = os.path.join(preview_dir, filename)
            
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 Удалено {deleted_count} старых превью файлов")
        
    except Exception as e:
        print(f"❌ Ошибка очистки превью: {e}")

# Тестирование системы превью
def test_preview_system():
    """Тестирует систему превью"""
    print("🧪 ТЕСТ СИСТЕМЫ ПРЕВЬЮ")
    print("=" * 50)
    
    # Тестовый SVG
    test_svg = '''<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#f8f9fa"/>
        <circle cx="200" cy="100" r="50" fill="#007bff"/>
        <text x="200" y="200" text-anchor="middle" fill="#333" font-family="Arial" font-size="18">
            Test Preview
        </text>
        <text x="200" y="230" text-anchor="middle" fill="#666" font-family="Arial" font-size="14">
            dyno.agentName
        </text>
    </svg>'''
    
    # Тест 1: PNG превью
    print("\n1. Тест PNG превью:")
    png_result = generate_svg_preview(test_svg, 'png')
    print(f"   Результат: {png_result}")
    
    # Тест 2: Base64 превью
    print("\n2. Тест Base64 превью:")
    base64_result = generate_svg_preview(test_svg, 'base64')
    if base64_result['success']:
        print(f"   Успех: {len(base64_result['base64'])} символов base64")
    else:
        print(f"   Ошибка: {base64_result['error']}")
    
    # Тест 3: Thumbnail превью
    print("\n3. Тест Thumbnail превью:")
    thumb_result = generate_svg_preview(test_svg, 'thumbnail')
    print(f"   Результат: {thumb_result}")
    
    # Тест 4: Превью с данными
    print("\n4. Тест превью с данными:")
    test_replacements = {
        'dyno.agentName': 'John Smith'
    }
    data_result = create_preview_with_data(test_svg, test_replacements)
    print(f"   Результат: {data_result}")

if __name__ == "__main__":
    test_preview_system()