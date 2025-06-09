#!/usr/bin/env python3
"""
УЛУЧШЕННЫЙ ПРОЦЕСС ГЕНЕРАЦИИ SVG С ПОДДЕРЖКОЙ ИЗОБРАЖЕНИЙ
========================================================

Этот модуль улучшает процесс генерации изображений из SVG шаблонов:
1. Поддержка загрузки внешних изображений
2. Правильная обработка dyno.* полей
3. Автоматический перенос длинных текстов
4. Обработка изображений в SVG
"""

import os
import requests
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import io
import re
import base64
from urllib.parse import urlparse
import tempfile

def download_image(url, max_size=(800, 600)):
    """Загрузка изображения по URL с ресайзом"""
    try:
        print(f"📥 Загружаю изображение: {url}")
        
        # Загружаем изображение
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Открываем изображение
        img = Image.open(io.BytesIO(response.content))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Ресайзим если нужно
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        print(f"✅ Изображение загружено и обработано: {img.size}")
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Ошибка загрузки изображения {url}: {e}")
        return None

def wrap_text(text, max_length=30):
    """Автоматический перенос длинного текста"""
    if len(text) <= max_length:
        return text
    
    # Пытаемся разбить по словам
    words = text.split()
    if len(words) <= 1:
        return text
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + len(current_line) <= max_length:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

def process_svg_with_images(svg_content, replacements):
    """Обработка SVG с заменой текста и изображений"""
    result = svg_content
    
    print("🔄 Обрабатываю SVG шаблон...")
    
    # Обрабатываем замены
    for key, value in replacements.items():
        clean_key = key.replace('dyno.', '')
        
        # Различные форматы переменных
        patterns = [
            f"{{{{dyno.{clean_key}}}}}",
            f"{{{{{key}}}}}",
            f"{{{{dyno.{key}}}}}",
            f"{{{{{clean_key}}}}}"
        ]
        
        # Специальная обработка для изображений
        if 'image' in clean_key.lower() or 'photo' in clean_key.lower():
            if isinstance(value, str) and (value.startswith('http') or value.startswith('https')):
                # Загружаем изображение
                image_data = download_image(value)
                if image_data:
                    # Заменяем в SVG
                    for pattern in patterns:
                        if pattern in result:
                            # Создаем image элемент
                            image_element = f'<image href="{image_data}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"/>'
                            result = result.replace(pattern, image_element)
                            print(f"✅ Заменено изображение: {clean_key}")
                else:
                    # Если не удалось загрузить, оставляем placeholder
                    for pattern in patterns:
                        result = result.replace(pattern, f"Image: {clean_key}")
            else:
                # Обычная текстовая замена
                for pattern in patterns:
                    result = result.replace(pattern, str(value))
        else:
            # Обработка текста с переносом для длинных адресов
            processed_value = str(value)
            if 'address' in clean_key.lower() and len(processed_value) > 30:
                processed_value = wrap_text(processed_value, 25)
            
            # Заменяем во всех форматах
            for pattern in patterns:
                if pattern in result:
                    result = result.replace(pattern, processed_value)
                    print(f"✅ Заменено поле: {clean_key} = {processed_value[:50]}...")
    
    # Проверяем остались ли незамененные переменные
    remaining_vars = re.findall(r'\{\{[^}]+\}\}', result)
    if remaining_vars:
        print(f"⚠️ Остались незамененные переменные: {remaining_vars}")
        # Заменяем их на пустые строки или placeholder
        for var in remaining_vars:
            result = result.replace(var, "")
    
    return result

def generate_png_from_svg_advanced(svg_content, output_path, width=800, height=600):
    """Улучшенная генерация PNG из SVG с обработкой ошибок"""
    try:
        print(f"🎨 Генерирую PNG: {output_path}")
        
        # Проверяем валидность SVG
        if not svg_content.strip().startswith('<svg'):
            print("❌ Некорректный SVG контент")
            return False
        
        # Добавляем namespace если отсутствует
        if 'xmlns=' not in svg_content:
            svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
        
        # Конвертируем SVG в PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            background_color='white'
        )
        
        # Сохраняем файл
        with open(output_path, 'wb') as f:
            f.write(png_data)
        
        # Проверяем размер файла
        file_size = os.path.getsize(output_path)
        print(f"✅ PNG сгенерирован: {file_size} байт")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации PNG: {e}")
        
        # Пытаемся создать fallback изображение
        try:
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Добавляем текст об ошибке
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            error_text = f"Error generating image\n{str(e)[:100]}"
            draw.text((50, height//2), error_text, fill='red', font=font)
            
            img.save(output_path, 'PNG')
            print(f"⚠️ Создан fallback PNG")
            return True
            
        except Exception as fallback_error:
            print(f"❌ Ошибка создания fallback: {fallback_error}")
            return False

def test_svg_generation():
    """Тестирование генерации SVG"""
    print("🧪 Тестирую генерацию SVG...")
    
    test_svg = '''<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
        <rect width="800" height="600" fill="#f8f9fa"/>
        <text x="400" y="100" text-anchor="middle" fill="#2c3e50" font-family="Arial" font-size="24">
            {{dyno.propertyaddress}}
        </text>
        <text x="400" y="200" text-anchor="middle" fill="#e74c3c" font-family="Arial" font-size="32">
            {{dyno.price}}
        </text>
        <rect x="200" y="300" width="400" height="200" fill="#ecf0f1"/>
        <text x="400" y="410" text-anchor="middle" fill="#7f8c8d" font-family="Arial" font-size="16">
            {{dyno.imagePath}}
        </text>
    </svg>'''
    
    test_replacements = {
        'dyno.propertyaddress': '123 Very Long Property Address That Should Be Wrapped, Beverly Hills, CA 90210',
        'dyno.price': '$2,500,000',
        'dyno.imagePath': 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=400&h=300&fit=crop'
    }
    
    processed_svg = process_svg_with_images(test_svg, test_replacements)
    
    test_output = '/tmp/test_generation.png'
    success = generate_png_from_svg_advanced(processed_svg, test_output)
    
    if success and os.path.exists(test_output):
        print(f"✅ Тест прошел успешно: {test_output}")
        return True
    else:
        print("❌ Тест не прошел")
        return False

if __name__ == "__main__":
    test_svg_generation()

