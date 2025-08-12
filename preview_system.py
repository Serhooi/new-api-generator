#!/usr/bin/env python3
"""
СИСТЕМА ПРЕВЬЮ ДЛЯ SVG ФЛАЕРОВ
=============================

Позволяет пользователю видеть превью SVG перед финальной генерацией
Включает систему замены изображений с поддержкой URL и base64
"""

import os
import uuid
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import re
import requests
import time

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
        print(f"📋 Поля для замены: {list(replacements.keys())}")
        
        # Сначала обрабатываем замену изображений
        print("🖼️ Обрабатываю замену изображений...")
        processed_svg = process_image_replacements(svg_content, replacements)
        
        # Затем импортируем функцию обработки SVG для текста
        try:
            from app import process_svg_font_perfect
            print("✅ Импорт process_svg_font_perfect успешен")
        except ImportError as e:
            print(f"❌ Ошибка импорта process_svg_font_perfect: {e}")
            # Fallback - простая замена без сложной обработки
            processed_svg = simple_svg_replacement(processed_svg, replacements)
        else:
            # Обрабатываем SVG с заменами текста
            print("🔄 Применяю замены текста через process_svg_font_perfect...")
            processed_svg = process_svg_font_perfect(processed_svg, replacements)
            print("✅ Замены применены")
        
        # Генерируем превью
        preview_result = generate_svg_preview(processed_svg, preview_type)
        
        if preview_result['success']:
            preview_result['replacements_count'] = len(replacements)
            preview_result['has_data'] = True
            print(f"✅ Превью с данными создано успешно")
        
        return preview_result
        
    except Exception as e:
        print(f"❌ Ошибка создания превью с данными: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

def simple_svg_replacement(svg_content, replacements):
    """
    Простая замена dyno полей в SVG (fallback функция)
    """
    print("⚠️ Использую простую замену (fallback)")
    
    processed_svg = svg_content
    
    for dyno_field, replacement in replacements.items():
        print(f"🔄 Заменяю {dyno_field} → {str(replacement)[:50]}...")
        
        # Безопасное экранирование
        safe_replacement = str(replacement).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Простые паттерны замены
        patterns = [
            dyno_field,  # Прямая замена
            f'{{{{{dyno_field}}}}}',  # {{dyno.field}}
            f'{{{dyno_field}}}',     # {dyno.field}
        ]
        
        for pattern in patterns:
            if pattern in processed_svg:
                processed_svg = processed_svg.replace(pattern, safe_replacement)
                print(f"   ✅ Заменен паттерн: {pattern}")
    
    return processed_svg

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

# ========================================
# СИСТЕМА ЗАМЕНЫ ИЗОБРАЖЕНИЙ
# ========================================

def create_placeholder_image(width=142, height=56, color='#4F46E5', text='LOGO'):
    """Создает placeholder изображение локально"""
    try:
        # Создаем изображение
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        
        # Пытаемся использовать системный шрифт
        try:
            # Для macOS
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 20)
        except:
            try:
                # Для Linux
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
            except:
                # Fallback на стандартный шрифт
                font = ImageFont.load_default()
        
        # Вычисляем позицию текста по центру
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Рисуем текст
        draw.text((x, y), text, fill='white', font=font)
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"⚠️ Ошибка создания placeholder: {e}")
        return None

def download_and_convert_image(url, timeout=10, retries=3):
    """Скачивает изображение по URL с повторными попытками и fallback'ами"""
    
    # Список альтернативных сервисов placeholder'ов
    placeholder_alternatives = [
        'https://picsum.photos/142/56',  # Lorem Picsum
        'https://dummyimage.com/142x56/4F46E5/FFFFFF&text=LOGO',  # DummyImage
        'https://fakeimg.pl/142x56/4F46E5/FFFFFF/?text=LOGO'  # FakeImg
    ]
    
    urls_to_try = [url]
    
    # Если это via.placeholder.com, добавляем альтернативы
    if 'via.placeholder.com' in url:
        print(f"🔄 via.placeholder.com недоступен, пробую альтернативы...")
        urls_to_try.extend(placeholder_alternatives)
    
    for attempt_url in urls_to_try:
        for attempt in range(retries):
            try:
                print(f"📥 Попытка {attempt + 1}/{retries}: {attempt_url[:50]}...")
                
                response = requests.get(attempt_url, timeout=timeout, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
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
                
                print(f"✅ Изображение скачано и конвертировано ({len(base64_url)} символов)")
                return base64_url
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка сети (попытка {attempt + 1}): {str(e)[:100]}...")
                if attempt < retries - 1:
                    time.sleep(1)  # Пауза перед повтором
                continue
            except Exception as e:
                print(f"❌ Ошибка обработки изображения: {e}")
                break
    
    # Если все попытки неудачны, создаем placeholder локально
    print(f"🎨 Создаю placeholder изображение локально...")
    if 'placeholder' in url.lower() or 'logo' in url.lower():
        return create_placeholder_image()
    
    return None

def replace_image_in_svg(svg_content, field_name, new_image_url):
    """
    Заменяет изображение в SVG файле.
    Поддерживает как прямую замену URL, так и замену через pattern -> image связи.
    
    Args:
        svg_content: Содержимое SVG
        field_name: Имя поля (например, 'dyno.propertyimage')
        new_image_url: URL нового изображения или base64 данные
    
    Returns:
        Обновленное содержимое SVG
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
            print(f"✅ Изображение {field_name} заменено!")
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
    
    # Определяем что делать с изображением
    if new_image_url.startswith('http'):
        # Пытаемся скачать и конвертировать
        replacement_url = download_and_convert_image(new_image_url)
        if not replacement_url:
            print(f"⚠️ Не удалось обработать изображение, использую исходный URL")
            replacement_url = new_image_url
    else:
        # Если это уже base64 или локальный файл
        replacement_url = new_image_url
    
    # Ищем и заменяем image элемент с этим ID
    image_regex = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    
    def replace_image_href(match):
        return match.group(1) + replacement_url + match.group(2)
    
    new_svg_content = re.sub(image_regex, replace_image_href, svg_content)
    
    if new_svg_content != svg_content:
        print(f"✅ Изображение {field_name} успешно заменено!")
        return new_svg_content
    else:
        print(f"❌ Изображение {field_name} не было заменено")
        return svg_content

def process_image_replacements(svg_content, image_data):
    """
    Обрабатывает замену всех изображений в SVG
    
    Args:
        svg_content: Содержимое SVG
        image_data: Словарь {field_name: image_url}
    
    Returns:
        Обновленное содержимое SVG
    """
    if not image_data:
        return svg_content
    
    print(f"🖼️ Обрабатываю {len(image_data)} изображений...")
    
    modified_svg = svg_content
    successful_replacements = 0
    
    # Определяем поля изображений
    image_fields = {k: v for k, v in image_data.items() 
                   if any(word in k.lower() for word in ['image', 'photo', 'picture', 'logo', 'headshot'])}
    
    for field_name, image_url in image_fields.items():
        print(f"\n🔄 Обрабатываю: {field_name}")
        
        original_size = len(modified_svg)
        modified_svg = replace_image_in_svg(modified_svg, field_name, image_url)
        new_size = len(modified_svg)
        
        if new_size != original_size:
            successful_replacements += 1
            print(f"📊 Изменение размера: {new_size - original_size:+d} символов")
    
    print(f"\n✅ Заменено изображений: {successful_replacements}/{len(image_fields)}")
    return modified_svg

# ========================================
# ТЕСТИРОВАНИЕ СИСТЕМЫ ПРЕВЬЮ
# ========================================

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