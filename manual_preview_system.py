#!/usr/bin/env python3
"""
СИСТЕМА РУЧНОЙ ЗАГРУЗКИ ПРЕВЬЮ
=============================

Позволяет загружать превью изображения вместе с SVG шаблонами
"""

import os
import uuid
from PIL import Image
import io

def save_preview_image(preview_file, template_id):
    """
    Сохраняет загруженное превью изображение
    
    Args:
        preview_file: Файл изображения (из Flask request.files)
        template_id: ID шаблона
    
    Returns:
        dict с информацией о сохраненном превью
    """
    try:
        print(f"💾 Сохраняю превью для шаблона {template_id}")
        
        # Создаем директорию для превью если не существует
        preview_dir = os.path.join('output', 'template_previews')
        os.makedirs(preview_dir, exist_ok=True)
        
        # Генерируем имя файла
        file_extension = preview_file.filename.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
            file_extension = 'png'
        
        preview_filename = f"template_{template_id}_preview.{file_extension}"
        preview_path = os.path.join(preview_dir, preview_filename)
        
        # Читаем и обрабатываем изображение
        image_data = preview_file.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
        
        # Оптимизируем размер (максимум 800x600)
        max_size = (800, 600)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"   📏 Изображение изменено до {img.size}")
        
        # Сохраняем как PNG для лучшего качества
        img.save(preview_path, 'PNG', optimize=True)
        
        file_size = os.path.getsize(preview_path)
        
        print(f"✅ Превью сохранено: {preview_path} ({file_size} байт)")
        
        return {
            'success': True,
            'filename': preview_filename,
            'path': preview_path,
            'url': f'/output/template_previews/{preview_filename}',
            'width': img.size[0],
            'height': img.size[1],
            'file_size': file_size
        }
        
    except Exception as e:
        print(f"❌ Ошибка сохранения превью: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_template_preview_url(template_id):
    """
    Получает URL превью для шаблона
    
    Args:
        template_id: ID шаблона
    
    Returns:
        URL превью или None если не найдено
    """
    preview_dir = os.path.join('output', 'template_previews')
    
    # Ищем файл превью для этого шаблона
    possible_extensions = ['png', 'jpg', 'jpeg', 'webp']
    
    for ext in possible_extensions:
        preview_filename = f"template_{template_id}_preview.{ext}"
        preview_path = os.path.join(preview_dir, preview_filename)
        
        if os.path.exists(preview_path):
            return f'/output/template_previews/{preview_filename}'
    
    return None

def delete_template_preview(template_id):
    """
    Удаляет превью шаблона
    
    Args:
        template_id: ID шаблона
    
    Returns:
        bool - успешность удаления
    """
    try:
        preview_dir = os.path.join('output', 'template_previews')
        possible_extensions = ['png', 'jpg', 'jpeg', 'webp']
        
        deleted = False
        for ext in possible_extensions:
            preview_filename = f"template_{template_id}_preview.{ext}"
            preview_path = os.path.join(preview_dir, preview_filename)
            
            if os.path.exists(preview_path):
                os.remove(preview_path)
                print(f"🗑️ Удалено превью: {preview_filename}")
                deleted = True
        
        return deleted
        
    except Exception as e:
        print(f"❌ Ошибка удаления превью: {e}")
        return False

def validate_preview_image(preview_file):
    """
    Валидирует загружаемое изображение превью
    
    Args:
        preview_file: Файл изображения
    
    Returns:
        dict с результатом валидации
    """
    try:
        # Проверяем размер файла (максимум 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        preview_file.seek(0, 2)  # Переходим в конец файла
        file_size = preview_file.tell()
        preview_file.seek(0)  # Возвращаемся в начало
        
        if file_size > max_size:
            return {
                'valid': False,
                'error': f'Файл слишком большой: {file_size / 1024 / 1024:.1f}MB (максимум 5MB)'
            }
        
        # Проверяем что это изображение
        try:
            img = Image.open(preview_file)
            width, height = img.size
            format_name = img.format
            preview_file.seek(0)  # Возвращаемся в начало для дальнейшего использования
            
            # Проверяем минимальные размеры
            if width < 100 or height < 100:
                return {
                    'valid': False,
                    'error': f'Изображение слишком маленькое: {width}x{height} (минимум 100x100)'
                }
            
            return {
                'valid': True,
                'width': width,
                'height': height,
                'format': format_name,
                'file_size': file_size
            }
            
        except Exception as img_error:
            return {
                'valid': False,
                'error': f'Некорректный файл изображения: {str(img_error)}'
            }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Ошибка валидации: {str(e)}'
        }

def create_default_preview(template_name, template_id):
    """
    Создает дефолтное превью если не загружено
    
    Args:
        template_name: Название шаблона
        template_id: ID шаблона
    
    Returns:
        dict с информацией о созданном превью
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем простое изображение-заглушку
        width, height = 400, 300
        img = Image.new('RGB', (width, height), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Добавляем текст
        try:
            # Пытаемся использовать системный шрифт
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
        except:
            try:
                font = ImageFont.truetype('arial.ttf', 24)
            except:
                font = ImageFont.load_default()
        
        # Рисуем рамку
        draw.rectangle([10, 10, width-10, height-10], outline='#dee2e6', width=2)
        
        # Добавляем название шаблона
        text_lines = [
            "📄 Template Preview",
            template_name[:30] + "..." if len(template_name) > 30 else template_name,
            "Upload custom preview image"
        ]
        
        y_offset = height // 2 - 40
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='#6c757d', font=font)
            y_offset += 30
        
        # Сохраняем
        preview_dir = os.path.join('output', 'template_previews')
        os.makedirs(preview_dir, exist_ok=True)
        
        preview_filename = f"template_{template_id}_preview.png"
        preview_path = os.path.join(preview_dir, preview_filename)
        
        img.save(preview_path, 'PNG')
        file_size = os.path.getsize(preview_path)
        
        print(f"✅ Создано дефолтное превью: {preview_filename}")
        
        return {
            'success': True,
            'filename': preview_filename,
            'url': f'/output/template_previews/{preview_filename}',
            'is_default': True,
            'file_size': file_size
        }
        
    except Exception as e:
        print(f"❌ Ошибка создания дефолтного превью: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Тестирование системы ручных превью"""
    print("🧪 ТЕСТ СИСТЕМЫ РУЧНЫХ ПРЕВЬЮ")
    print("=" * 50)
    
    # Создаем тестовое дефолтное превью
    test_template_id = "test-template-123"
    test_template_name = "Test Template Name"
    
    result = create_default_preview(test_template_name, test_template_id)
    print(f"Результат создания дефолтного превью: {result}")
    
    # Проверяем получение URL
    preview_url = get_template_preview_url(test_template_id)
    print(f"URL превью: {preview_url}")

if __name__ == "__main__":
    main()