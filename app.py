"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИДЕАЛЬНАЯ ОБРАБОТКА ШРИФТОВ И МАСШТАБИРОВАНИЕ ХЕДШОТОВ
================================================================

Версия 11.0 - Полная версия с АБСОЛЮТНЫМ сохранением шрифтов Montserrat, исправлением экранирования спецсимволов
и улучшенным масштабированием и центрированием круглых хедшотов
"""

import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import xml.etree.ElementTree as ET
import re
import requests
import base64
import tempfile
import io
import html
import cairosvg
from PIL import Image
from supabase import create_client, Client
from preview_system import generate_svg_preview, create_preview_with_data, cleanup_old_previews

app = Flask(__name__)
CORS(app, origins="*")

# Устанавливаем максимальный размер загружаемого файла (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Конфигурация
DATABASE_PATH = 'templates.db'
OUTPUT_DIR = 'output'
ALLOWED_EXTENSIONS = {'svg'}

# Supabase конфигурация
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', 'your-anon-key')

# Инициализация Supabase клиента
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase клиент инициализирован")
except Exception as e:
    print(f"❌ Ошибка инициализации Supabase: {e}")
    supabase = None

# Создаем директории (для локальной разработки)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('output/single', exist_ok=True)
os.makedirs('output/carousel', exist_ok=True)
os.makedirs('output/previews', exist_ok=True)

field_mapping = {
    # Маппинг для main template
    'dyno.agentName': 'dyno.name',
    'dyno.agentPhone': 'dyno.phone',
    'dyno.agentEmail': 'dyno.email',
    'dyno.agentPhoto': 'dyno.agentheadshot',
    'dyno.propertyAddress': 'dyno.propertyaddress',
    'dyno.propertyfeatures': 'dyno.propertyfeatures',
    
    # Обратный маппинг для совместимости
    'dyno.agentname': 'dyno.name',
    'dyno.agentemail': 'dyno.email', 
    'dyno.agentphone': 'dyno.phone',
    'dyno.agentphoto': 'dyno.agentheadshot',
    'dyno.propertyaddress': 'dyno.propertyaddress',
    
    # Маппинг для множественных изображений недвижимости
    'dyno.propertyimage1': 'dyno.propertyimage',  # Первое изображение на main слайде
}

# Специальный маппинг для photo template
photo_field_mapping = {
    'dyno.propertyimage': 'dyno.propertyimage2',  # В photo template используется propertyimage2
    'dyno.agentphoto': 'dyno.agentheadshot'       # В photo template может быть agentheadshot
}

def has_dyno_fields_simple(svg_content):
    """
    Простая проверка наличия dyno полей в SVG
    """
    patterns = [
        r'\{\{dyno\.[^}]+\}\}',     # {{dyno.field}}
        r'\{dyno\.[^}]+\}',         # {dyno.field}
        r'id="dyno\.[^"]*"',        # id="dyno.field"
        r"id='dyno\.[^']*'",        # id='dyno.field'
        r'dyno\.[a-zA-Z][a-zA-Z0-9]*'  # dyno.field
    ]
    
    for pattern in patterns:
        if re.search(pattern, svg_content):
            return True
    return False

def extract_dyno_fields_simple(svg_content):
    """
    Простое извлечение dyno полей из SVG
    """
    fields = set()
    
    # Паттерны для поиска dyno полей
    patterns = [
        r'\{\{(dyno\.[^}]+)\}\}',     # {{dyno.field}}
        r'\{(dyno\.[^}]+)\}',         # {dyno.field}
        r'id="(dyno\.[^"]*)"',        # id="dyno.field"
        r"id='(dyno\.[^']*)'",        # id='dyno.field'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, svg_content)
        for match in matches:
            fields.add(match)
    
    return list(fields)

def safe_escape_for_svg(text):
    """
    Безопасное экранирование для SVG - ВСЕ опасные символы включая &
    """
    if not text:
        return text
    
    # Заменяем ВСЕ опасные символы для XML/SVG
    text = str(text)
    text = text.replace('&', '&amp;')  # ВАЖНО: & должен быть первым!
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

def generate_svg_preview(svg_content, template_id, width=400, height=300):
    """
    Генерирует PNG превью из SVG шаблона
    """
    try:
        print(f"🖼️ Генерирую превью для шаблона: {template_id}")
        
        # Создаем директорию для превью если не существует
        preview_dir = os.path.join(OUTPUT_DIR, 'previews')
        os.makedirs(preview_dir, exist_ok=True)
        
        # Путь для сохранения PNG превью
        png_filename = f"{template_id}_preview.png"
        png_path = os.path.join(preview_dir, png_filename)
        
        # Создаем превью SVG с заменой dyno полей на примеры
        preview_svg = create_preview_svg(svg_content)
        
        # Конвертируем SVG в PNG
        png_data = cairosvg.svg2png(
            bytestring=preview_svg.encode('utf-8'),
            output_width=width,
            output_height=height,
            background_color='white'
        )
        
        # Сохраняем PNG файл
        with open(png_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Превью создано: {png_filename}")
        
        return {
            'success': True,
            'filename': png_filename,
            'url': f'/output/previews/{png_filename}',
            'path': png_path
        }
        
    except Exception as e:
        print(f"❌ Ошибка создания превью: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def create_preview_svg(svg_content):
    """
    Создает превью SVG заменяя dyno поля на примеры данных
    """
    preview_svg = svg_content
    
    # Примеры данных для превью
    preview_data = {
        'dyno.agentName': 'John Smith',
        'dyno.propertyAddress': '123 Main Street, Beverly Hills, CA 90210',
        'dyno.price': '$450,000',
        'dyno.bedrooms': '3',
        'dyno.bathrooms': '2',
        'dyno.sqft': '1,850',
        'dyno.agentPhone': '(555) 123-4567',
        'dyno.agentEmail': 'john@realty.com',
        'dyno.openHouseDate': 'Saturday, June 8th',
        'dyno.openHouseTime': '2:00 PM - 4:00 PM',
        'dyno.agentPhoto': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
        'dyno.propertyImage': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop',
        'dyno.propertyimage2': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300&fit=crop',
        'dyno.propertyimage3': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop',
        'dyno.propertyimage4': 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300&fit=crop',
        'dyno.propertyimage5': 'https://images.unsplash.com/photo-1560448075-bb485b067938?w=400&h=300&fit=crop',
        'dyno.companyLogo': 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=200&h=100&fit=crop'
    }
    
    # Заменяем dyno поля на примеры
    for field, value in preview_data.items():
        # Различные форматы dyno полей
        patterns = [
            f'{{{{{field}}}}}',           # {{dyno.field}}
            f'{{{field}}}',               # {dyno.field}
            f'>{field}<',                 # >dyno.field<
        ]
        
        for pattern in patterns:
            if pattern.startswith('>') and pattern.endswith('<'):
                preview_svg = preview_svg.replace(pattern, f'>{value}<')
            else:
                preview_svg = preview_svg.replace(pattern, value)
    
    return preview_svg

def process_svg_font_perfect(svg_content, replacements):
    """
    ФИНАЛЬНАЯ функция с исправлением круглых хедшотов
    - Автоматическое определение формы элемента (круглый vs прямоугольный)
    - Правильный aspect ratio для каждого типа
    - Поддержка use элементов в pattern блоках
    - Сохранение оригинальных шрифтов Inter и Montserrat
    - Автоматический перенос длинных адресов на две строки
    - ПОЛНОЕ экранирование всех спецсимволов для URL и текстов
    - Улучшенное масштабирование и центрирование круглых хедшотов
    """
    print("🎨 ЗАПУСК ФИНАЛЬНОЙ ОБРАБОТКИ SVG (с исправлением круглых хедшотов)")
    
    processed_svg = svg_content
    
    def determine_element_shape(svg_content, pattern_id):
        """Определяет форму элемента (круглый или прямоугольный)"""
        
        # Ищем clipPath связанный с pattern
        clip_pattern = f'<clipPath[^>]*id="[^"]*{re.escape(pattern_id)}[^"]*"[^>]*>(.*?)</clipPath>'
        clip_match = re.search(clip_pattern, svg_content, re.DOTALL)
        
        if clip_match:
            clip_content = clip_match.group(1)
            
            # Проверяем наличие circle или ellipse
            if '<circle' in clip_content or '<ellipse' in clip_content:
                return 'circular'
            
            # Проверяем наличие rect с rx/ry (скругленные углы)
            rect_pattern = r'<rect[^>]*rx="([^"]*)"[^>]*ry="([^"]*)"[^>]*>'
            rect_match = re.search(rect_pattern, clip_content)
            if rect_match:
                rx = float(rect_match.group(1) or 0)
                ry = float(rect_match.group(2) or 0)
                
                # Если радиус скругления большой, считаем круглым
                if rx > 20 or ry > 20:
                    return 'circular'
            
            # Проверяем path с круглыми формами
            if '<path' in clip_content:
                path_pattern = r'd="([^"]*)"'
                path_match = re.search(path_pattern, clip_content)
                if path_match:
                    path_data = path_match.group(1)
                    # Ищем команды дуг (A) или много кривых (C)
                    if 'A' in path_data or path_data.count('C') > 4:
                        return 'circular'
        
        # Альтернативный способ - анализ размеров pattern
        pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*width="([^"]*)"[^>]*height="([^"]*)"[^>]*>'
        pattern_match = re.search(pattern_pattern, svg_content)
        
        if pattern_match:
            width = float(pattern_match.group(1) or 0)
            height = float(pattern_match.group(2) or 0)
            
            # Если ширина и высота примерно равны, скорее всего круглый
            if abs(width - height) < 5:
                return 'circular'
        
        # По умолчанию считаем прямоугольным
        return 'rectangular'
    
    def determine_image_type(dyno_field):
        """Определяет тип изображения по названию поля"""
        field_lower = dyno_field.lower()
        
        if 'headshot' in field_lower or 'agent' in field_lower or 'profile' in field_lower:
            return 'headshot'
        elif 'propertyimage' in field_lower or 'property' in field_lower:
            return 'property'
        elif 'logo' in field_lower or 'company' in field_lower:
            return 'logo'
        else:
            return 'general'
    
    def get_aspect_ratio_for_image(image_type, element_shape):
        """Возвращает правильный preserveAspectRatio для типа изображения"""
        if image_type == 'headshot':
            # Для headshot - показываем всё лицо, центрируем
            return 'xMidYMid meet'
        elif image_type == 'property':
            # Для property images - заполняем весь блок, обрезаем если нужно
            return 'xMidYMid slice'
        elif image_type == 'logo':
            # Для лого - показываем полностью, центрируем
            return 'xMidYMid meet'
        else:
            # По умолчанию - центрируем
            return 'xMidYMid meet'
    
    def is_image_field(dyno_field):
        """Проверяет, является ли поле изображением"""
        field_lower = dyno_field.lower()
        return any(keyword in field_lower for keyword in ['image', 'photo', 'headshot', 'logo', 'picture'])
    
    def find_headshot_field(replacements):
        """Ищет поле headshot в replacements (поддерживает разные названия)"""
        headshot_fields = ['dyno.agentheadshot', 'dyno.agentphoto', 'dyno.headshot', 'dyno.agent', 'dyno.photo']
        
        for field in headshot_fields:
            if field in replacements:
                return field
        
        # Если не нашли точное совпадение, ищем по ключевым словам
        for field in replacements.keys():
            if any(keyword in field.lower() for keyword in ['headshot', 'agent', 'photo', 'profile']):
                return field
        
        return None
    
    def is_address_field(dyno_field):
        """Определяет, является ли поле адресом"""
        field_lower = dyno_field.lower()
        address_keywords = ['address', 'location', 'addr', 'street', 'propertyaddress']
        
        for keyword in address_keywords:
            if keyword in field_lower:
                return True
        
        return False
    
    def wrap_address_text(address_text, max_length=35):
        """Автоматически переносит длинный адрес на строки"""
        if len(address_text) <= max_length:
            return address_text, ""
        
        # Разбиваем по запятым
        parts = address_text.split(', ')
        if len(parts) >= 2:
            # Первая строка: номер дома + улица
            line1 = parts[0]
            # Вторая строка: остальное
            line2 = ', '.join(parts[1:])
            return line1, line2
        
        # Если нет запятых, разбиваем по словам
        words = address_text.split()
        if len(words) <= 3:
            return address_text, ""
        
        # Ищем середину для разбивки
        mid = len(words) // 2
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        return line1, line2
    
    def wrap_address_text(address_text, max_length=35):
        """
        Автоматический перенос адреса на две строки
        """
        if not address_text or len(address_text) <= max_length:
            return address_text, ""
        
        # Пытаемся найти хорошее место для разрыва
        words = address_text.split()
        
        if len(words) <= 1:
            return address_text, ""
        
        # Ищем оптимальное место для разрыва
        best_break = len(words) // 2
        
        # Пытаемся найти запятую для естественного разрыва
        for i, word in enumerate(words):
            if ',' in word and i > 0 and i < len(words) - 1:
                # Проверяем, не слишком ли короткая первая строка
                first_part = ' '.join(words[:i+1])
                if len(first_part) >= 15:  # Минимум 15 символов в первой строке
                    best_break = i + 1
                    break
        
        # Если не нашли запятую, ищем другие разделители
        if best_break == len(words) // 2:
            for i, word in enumerate(words):
                if i > 0 and i < len(words) - 1:
                    first_part = ' '.join(words[:i+1])
                    if 20 <= len(first_part) <= max_length:
                        best_break = i + 1
                        break
        
        first_line = ' '.join(words[:best_break])
        second_line = ' '.join(words[best_break:])
        
        # Если вторая строка слишком длинная, возвращаем оригинал
        if len(second_line) > max_length:
            return address_text, ""
        
        return first_line, second_line
    
    # Обрабатываем каждое поле
    successful_replacements = 0
    total_fields = len(replacements)
    
    # Обрабатываем каждое поле с учетом маппинга
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Проверяем основное поле
        original_field = dyno_field
        
        # Проверяем альтернативные названия полей
        alternative_field = None
        
        # Проверяем точное совпадение
        if dyno_field in field_mapping:
            alternative_field = field_mapping[dyno_field]
            print(f"   🔄 Проверяю альтернативное название поля: {alternative_field}")
        else:
            # Проверяем регистронезависимое совпадение
            dyno_field_lower = dyno_field.lower()
            for key, value in field_mapping.items():
                if key.lower() == dyno_field_lower:
                    alternative_field = value
                    print(f"   🔄 Найдено регистронезависимое совпадение: {dyno_field} → {alternative_field}")
                    break
        
        if is_image_field(dyno_field):
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ
            print(f"🖼️ Обрабатываю изображение: {dyno_field}")
            
            safe_url = str(replacement).replace('&', '&amp;')
            
            # Определяем тип изображения и правильный aspect ratio
            image_type = determine_image_type(dyno_field)
            aspect_ratio = get_aspect_ratio_for_image(image_type, 'unknown')  # Пока не знаем форму
            
            print(f"   🎯 Тип изображения: {image_type}, aspect ratio: {aspect_ratio}")
            
            # Ищем элемент с id - УПРОЩЕННЫЙ ПОИСК
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            # Если не нашли по точному ID, ищем по альтернативным названиям для headshot
            if not match and image_type == 'headshot':
                print(f"   🔍 Headshot не найден по ID {dyno_field}, ищу альтернативные поля...")
                alternative_headshot_fields = ['dyno.agentheadshot', 'dyno.agentphoto', 'dyno.headshot', 'dyno.agent', 'dyno.photo', 'dyno.agentPhoto']
                
                for alt_field in alternative_headshot_fields:
                    alt_pattern = f'<[^>]*id="{re.escape(alt_field)}"[^>]*>'
                    alt_match = re.search(alt_pattern, processed_svg)
                    if alt_match:
                        print(f"   ✅ Найден альтернативный headshot элемент: {alt_field}")
                        element_pattern = alt_pattern
                        match = alt_match
                        dyno_field = alt_field  # Обновляем поле для дальнейшей обработки
                        break
            
            if match:
                print(f"   ✅ Найден элемент с id: {dyno_field}")
                
                # Ищем pattern в fill атрибуте
                fill_pattern = f'fill="url\\(#([^)]+)\\)"'
                fill_match = re.search(fill_pattern, match.group(0))
                
                if fill_match:
                    pattern_id = fill_match.group(1)
                    print(f"   🎯 Найден pattern: {pattern_id}")
                    
                    # Определяем форму элемента
                    element_shape = determine_element_shape(processed_svg, pattern_id)
                    print(f"   🔍 Форма элемента: {element_shape}")
                    
                    # Обновляем aspect ratio с учетом формы
                    aspect_ratio = get_aspect_ratio_for_image(image_type, element_shape)
                    print(f"   🎯 Финальный aspect ratio: {aspect_ratio}")
                    
                    # Ищем pattern блок
                    pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                    pattern_match = re.search(pattern_block_pattern, processed_svg, re.DOTALL)
                    
                    if pattern_match:
                        pattern_content = pattern_match.group(1)
                        pattern_full = pattern_match.group(0)
                        
                        # Для headshot - убираем фиксированные transform для лучшего центрирования
                        if image_type == 'headshot' and element_shape == 'circular':
                            print(f"   🔍 Обрабатываю круглый headshot БЕЗ фиксированных смещений")
                            
                            # Убираем любые существующие patternTransform для лучшего центрирования
                            old_pattern = pattern_full
                            new_pattern = re.sub(r'\s*patternTransform="[^"]*"', '', old_pattern)
                            new_pattern = re.sub(r'\s*transform="[^"]*"', '', new_pattern)
                            
                            if new_pattern != old_pattern:
                                processed_svg = processed_svg.replace(old_pattern, new_pattern)
                                print(f"   ✅ Удалены фиксированные transform - headshot будет центрироваться автоматически")
                        
                        # Ищем use элемент внутри pattern
                        use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
                        use_match = re.search(use_pattern, pattern_content)
                        
                        if use_match:
                            image_id = use_match.group(1)
                            print(f"   🔗 Найден use элемент: #{image_id}")
                            
                            # Ищем соответствующий image элемент
                            image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
                            image_match = re.search(image_pattern, processed_svg)
                            
                            if image_match:
                                old_image = image_match.group(0)
                                new_image = old_image
                                
                                # Заменяем URL
                                new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
                                new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                                
                                # Устанавливаем правильный preserveAspectRatio
                                if 'preserveAspectRatio=' in new_image:
                                    new_image = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', new_image)
                                else:
                                    if new_image.endswith('/>'):
                                        new_image = new_image.replace('/>', f' preserveAspectRatio="{aspect_ratio}"/>')
                                    else:
                                        new_image = new_image.replace('>', f' preserveAspectRatio="{aspect_ratio}">')
                                
                                # Применяем замену
                                processed_svg = processed_svg.replace(old_image, new_image)
                                print(f"   ✅ Изображение {image_id} заменено: {safe_url[:50]}...")
                                successful_replacements += 1
                            else:
                                print(f"   ⚠️ Image элемент {image_id} не найден")
                        else:
                            print(f"   ⚠️ Use элемент не найден в pattern")
                    else:
                        print(f"   ⚠️ Pattern блок {pattern_id} не найден")
                else:
                    print(f"   ⚠️ Элемент {dyno_field} найден, но не имеет fill с pattern")
            else:
                print(f"   ⚠️ Элемент с id {dyno_field} не найден")
        else:
            # ОБРАБОТКА ТЕКСТОВЫХ ПОЛЕЙ
            safe_replacement = safe_escape_for_svg(str(replacement))
            
            if is_address_field(dyno_field):
                print(f"   🏠 Обрабатываю адрес с переносом: {dyno_field}")
                
                # Разбиваем адрес на две строки
                first_line, second_line = wrap_address_text(str(replacement))
                
                print(f"      📝 Первая строка: {first_line}")
                print(f"      📝 Вторая строка: {second_line}")
                
                # Ищем text элемент
                element_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
                
                # Если не нашли по основному имени, пробуем альтернативное
                if not re.search(element_pattern, processed_svg) and alternative_field:
                    element_pattern = f'<text[^>]*id="{re.escape(alternative_field)}"[^>]*>(.*?)</text>'
                    if re.search(element_pattern, processed_svg):
                        print(f"      ✅ Найдено по альтернативному имени: {alternative_field}")
                        dyno_field = alternative_field
                
                def replace_address_element(match):
                    full_element = match.group(0)
                    element_content = match.group(1)
                    
                    # Ищем существующий tspan
                    tspan_pattern = r'<tspan[^>]*x="([^"]*)"[^>]*y="([^"]*)"[^>]*>([^<]*)</tspan>'
                    tspan_match = re.search(tspan_pattern, element_content)
                    
                    if tspan_match:
                        x_pos = tspan_match.group(1)
                        y_pos = tspan_match.group(2)
                        
                        # Создаем новый контент с двумя tspan элементами
                        if second_line:
                            # Вычисляем позицию для второй строки
                            try:
                                y_float = float(y_pos)
                                second_y = y_float + 35
                            except:
                                second_y = f"{y_pos}+35"
                            
                            new_content = f'<tspan x="{x_pos}" y="{y_pos}">{safe_escape_for_svg(first_line)}</tspan><tspan x="{x_pos}" y="{second_y}">{safe_escape_for_svg(second_line)}</tspan>'
                        else:
                            new_content = f'<tspan x="{x_pos}" y="{y_pos}">{safe_escape_for_svg(first_line)}</tspan>'
                        
                        return full_element.replace(element_content, new_content)
                    else:
                        return full_element
                
                new_svg = re.sub(element_pattern, replace_address_element, processed_svg, flags=re.DOTALL)
                
                if new_svg != processed_svg:
                    processed_svg = new_svg
                    print(f"      ✅ Адрес {dyno_field} заменен с переносом!")
                    successful_replacements += 1
                else:
                    print(f"      ⚠️ Адрес {dyno_field} не найден")
            else:
                print(f"   🔤 Обрабатываю текстовое поле: {dyno_field}")
                
                # Ищем элемент с id="dyno.field"
                element_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
                
                # Если не нашли по основному имени, пробуем альтернативное
                if not re.search(element_pattern, processed_svg) and alternative_field:
                    element_pattern = f'<text[^>]*id="{re.escape(alternative_field)}"[^>]*>(.*?)</text>'
                    if re.search(element_pattern, processed_svg):
                        print(f"      ✅ Найдено по альтернативному имени: {alternative_field}")
                        dyno_field = alternative_field
                
                def replace_element_content(match):
                    full_element = match.group(0)
                    element_content = match.group(1)
                    
                    print(f"      📝 Найден элемент с id: {dyno_field}")
                    
                    # Заменяем содержимое первого tspan
                    def replace_tspan_content(tspan_match):
                        opening_tag = tspan_match.group(1)  # <tspan ...>
                        old_content = tspan_match.group(2)  # старое содержимое
                        closing_tag = tspan_match.group(3)  # </tspan>
                        
                        print(f"         🎯 Заменяю: '{old_content}' → '{safe_replacement}'")
                        
                        return opening_tag + safe_replacement + closing_tag
                    
                    # Паттерн для первого tspan
                    tspan_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
                    new_content = re.sub(tspan_pattern, replace_tspan_content, element_content, count=1)
                    
                    print(f"      ✅ Содержимое заменено!")
                    return full_element.replace(element_content, new_content)
                
                # Применяем замену
                new_svg = re.sub(element_pattern, replace_element_content, processed_svg, flags=re.DOTALL)
                
                if new_svg != processed_svg:
                    processed_svg = new_svg
                    print(f"      ✅ Поле {dyno_field} успешно заменено!")
                    successful_replacements += 1
                else:
                    print(f"      ⚠️ Элемент с id='{dyno_field}' не найден")
    
    # СОХРАНЯЕМ ШРИФТЫ INTER И MONTSERRAT
    print("\n🔤 Сохраняем шрифты Inter и Montserrat...")
    
    # ДОБАВЛЯЕМ GOOGLE FONTS ИМПОРТ ДЛЯ INTER И MONTSERRAT
    print("📥 Добавляю Google Fonts импорт для Inter и Montserrat...")
    
    # Ищем тег <defs> или создаем его
    if '<defs>' in processed_svg:
        # Добавляем стиль в существующий <defs>
        defs_pattern = r'(<defs>)'
        font_style = r'\1\n<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Montserrat:wght@100;200;300;400;500;600;700;800;900&display=swap");</style>'
        processed_svg = re.sub(defs_pattern, font_style, processed_svg)
    else:
        # Создаем новый <defs> после открывающего <svg>
        svg_pattern = r'(<svg[^>]*>)'
        font_defs = r'\1\n<defs>\n<style>@import url("https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&family=Montserrat:wght@100;200;300;400;500;600;700;800;900&display=swap");</style>\n</defs>'
        processed_svg = re.sub(svg_pattern, font_defs, processed_svg)
    
    print("✅ Google Fonts импорт добавлен!")
    
    # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА НА НЕЭКРАНИРОВАННЫЕ АМПЕРСАНДЫ
    print("\n🔍 Проверка на неэкранированные амперсанды в SVG...")
    
    # Ищем неэкранированные амперсанды вне атрибутов
    unescaped_ampersands = re.findall(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', processed_svg)
    
    if unescaped_ampersands:
        print(f"⚠️ Найдено {len(unescaped_ampersands)} неэкранированных амперсандов, исправляю...")
        processed_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', processed_svg)
        print("✅ Все неэкранированные амперсанды исправлены!")
    else:
        print("✅ Неэкранированных амперсандов не найдено!")
    
    print(f"\n📊 РЕЗУЛЬТАТ: {successful_replacements}/{total_fields} полей заменено")
    print("🎉 ФИНАЛЬНАЯ обработка SVG завершена!")
    
    return processed_svg

def create_dynamic_template(template_id, template_role):
    """Создает динамический шаблон на лету, если его нет в базе"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Проверяем, существует ли шаблон
    cursor.execute('SELECT id FROM templates WHERE id = ?', (template_id,))
    if cursor.fetchone():
        conn.close()
        return True
    
    # Создаем динамический шаблон
    if template_role == 'main':
        content = '''<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white"/>
            <text x="600" y="200" text-anchor="middle" font-size="48" fill="black">Dynamic Main Template</text>
            <text id="dyno.agentName" x="600" y="300" text-anchor="middle" font-size="24" fill="blue">Agent: {dyno.agentName}</text>
            <text id="dyno.propertyAddress" x="600" y="350" text-anchor="middle" font-size="20" fill="green">Address: {dyno.propertyAddress}</text>
            <text id="dyno.price" x="600" y="400" text-anchor="middle" font-size="32" fill="red">Price: {dyno.price}</text>
            <text id="dyno.agentPhone" x="600" y="450" text-anchor="middle" font-size="18" fill="purple">Phone: {dyno.agentPhone}</text>
            <text id="dyno.agentEmail" x="600" y="500" text-anchor="middle" font-size="16" fill="orange">Email: {dyno.agentEmail}</text>
            <text id="dyno.bedrooms" x="600" y="550" text-anchor="middle" font-size="20" fill="brown">Bedrooms: {dyno.bedrooms}</text>
            <text id="dyno.bathrooms" x="600" y="580" text-anchor="middle" font-size="20" fill="brown">Bathrooms: {dyno.bathrooms}</text>
            <text id="dyno.date" x="600" y="620" text-anchor="middle" font-size="18" fill="darkgreen">Date: {dyno.date}</text>
            <text id="dyno.time" x="600" y="650" text-anchor="middle" font-size="18" fill="darkgreen">Time: {dyno.time}</text>
            <text id="dyno.propertyfeatures" x="600" y="680" text-anchor="middle" font-size="14" fill="gray">Features: {dyno.propertyfeatures}</text>
        </svg>'''
        name = f"Dynamic Main Template ({template_id[:8]})"
    else:
        content = '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="lightblue"/>
            <text x="400" y="200" text-anchor="middle" font-size="36" fill="black">Dynamic Photo Template</text>
            <rect id="dyno.propertyimage1" x="100" y="250" width="600" height="300" fill="url(#property_pattern)"/>
            <defs>
                <pattern id="property_pattern" patternUnits="objectBoundingBox" width="1" height="1">
                    <image id="property_image" href="https://via.placeholder.com/600x300/cccccc/666666?text=Property+Image" preserveAspectRatio="xMidYMid slice"/>
                </pattern>
            </defs>
        </svg>'''
        name = f"Dynamic Photo Template ({template_id[:8]})"
    
    cursor.execute('''
        INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (template_id, name, 'dynamic', template_role, content, 'dyno.agentName,dyno.agentPhone,dyno.agentEmail,dyno.propertyAddress,dyno.price,dyno.bedrooms,dyno.bathrooms,dyno.date,dyno.time,dyno.propertyfeatures'))
    
    conn.commit()
    conn.close()
    print(f"✅ Создан динамический шаблон: {template_id}")
    return True

def ensure_db_exists():
    """
    Создает базу данных и таблицы если они не существуют
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу templates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            template_role TEXT NOT NULL,
            svg_content TEXT NOT NULL,
            dyno_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу carousels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carousels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            main_template_id TEXT NOT NULL,
            photo_template_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (main_template_id) REFERENCES templates (id),
            FOREIGN KEY (photo_template_id) REFERENCES templates (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_supabase_storage(file_content, filename, folder="generated"):
    """
    Загружает файл в Supabase Storage
    """
    if not supabase:
        print("❌ Supabase клиент не инициализирован")
        return None
    
    try:
        # Создаем путь к файлу
        file_path = f"{folder}/{filename}"
        
        # Загружаем файл в Storage
        result = supabase.storage.from_("images").upload(
            path=file_path,
            file=file_content.encode('utf-8'),
            file_options={"content-type": "image/svg+xml"}
        )
        
        # Получаем публичный URL
        public_url = supabase.storage.from_("images").get_public_url(file_path)
        
        print(f"✅ Файл загружен в Supabase: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в Supabase: {e}")
        return None

def save_file_locally_or_supabase(content, filename, folder="carousel"):
    """
    Сохраняет файл локально (для разработки) или в Supabase (для продакшена)
    """
    # Определяем, работаем ли мы на Render
    is_render = os.environ.get('RENDER', False) or os.environ.get('SUPABASE_URL', False)
    
    if is_render and supabase:
        # На Render - загружаем в Supabase
        return upload_to_supabase_storage(content, filename, folder)
    else:
        # Локально - сохраняем в файл
        local_path = os.path.join(OUTPUT_DIR, folder, filename)
        try:
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Файл сохранен локально: {local_path}")
            return f"/output/{folder}/{filename}"
        except Exception as e:
            print(f"❌ Ошибка сохранения локально: {e}")
            return None

def create_app():
    """
    Функция для создания приложения (нужна для Gunicorn)
    """
    ensure_db_exists()
    return app

# Веб-интерфейс
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Получаем все шаблоны из базы данных
        cursor.execute('SELECT id, name, category, template_role, created_at FROM templates ORDER BY created_at DESC')
        templates_data = cursor.fetchall()
        
        conn.close()
        
        # Преобразуем в список словарей для передачи в шаблон
        templates = []
        for template in templates_data:
            templates.append({
                'id': template[0],
                'name': template[1],
                'category': template[2],
                'template_role': template[3],
                'created_at': template[4]
            })
        
        # Передаем шаблоны в HTML шаблон
        return render_template('templates.html', templates=templates)
        
    except Exception as e:
        print(f"Ошибка в templates_page: {str(e)}")
        return render_template('templates.html', templates=[])

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/preview')
def preview_page():
    return render_template('preview.html')

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# Статические файлы для ручных превью
@app.route('/output/template_previews/<filename>')
def serve_template_previews(filename):
    preview_dir = os.path.join(OUTPUT_DIR, 'template_previews')
    return send_from_directory(preview_dir, filename)

# API для загрузки одиночного шаблона
@app.route('/api/upload-single', methods=['POST'])
def upload_single_template():
    try:
        # Импортируем функции для работы с превью
        from manual_preview_system import save_preview_image, validate_preview_image, create_default_preview
        
        # ИСПРАВЛЕНО: Проверяем правильное имя поля из формы (svg_file)
        if 'svg_file' not in request.files:
            return jsonify({'error': 'Файл не найден'}), 400
        
        file = request.files['svg_file']
        name = request.form.get('name', '')
        category = request.form.get('category', '')
        template_role = request.form.get('template_role', '')
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое файла
        svg_content = file.read().decode('utf-8')
        
        # Проверяем наличие dyno полей
        has_dyno = has_dyno_fields_simple(svg_content)
        dyno_fields = extract_dyno_fields_simple(svg_content) if has_dyno else []
        
        # Генерируем уникальный ID
        template_id = str(uuid.uuid4())
        
        # Сохраняем в базу данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [template_id, name, category, template_role, svg_content, ','.join(dyno_fields)])
        
        conn.commit()
        conn.close()
        
        # Обрабатываем превью изображение
        preview_result = None
        if 'preview_file' in request.files and request.files['preview_file'].filename:
            preview_file = request.files['preview_file']
            print(f"📸 Обрабатываю загруженное превью: {preview_file.filename}")
            
            # Валидируем превью
            validation = validate_preview_image(preview_file)
            if validation['valid']:
                # Сохраняем превью
                preview_result = save_preview_image(preview_file, template_id)
                if preview_result['success']:
                    print(f"✅ Превью сохранено для шаблона {template_id}")
                else:
                    print(f"⚠️ Ошибка сохранения превью: {preview_result['error']}")
            else:
                print(f"⚠️ Превью не прошло валидацию: {validation['error']}")
        
        # Если превью не загружено или не удалось сохранить, создаем дефолтное
        if not preview_result or not preview_result['success']:
            print(f"🎨 Создаю дефолтное превью для {template_id}")
            preview_result = create_default_preview(name, template_id)
        
        response_data = {
            'success': True,
            'template_id': template_id,
            'has_dyno_fields': has_dyno,
            'dyno_fields': dyno_fields,
            'message': f'Шаблон "{name}" успешно загружен'
        }
        
        # Добавляем информацию о превью
        if preview_result and preview_result['success']:
            response_data['preview_url'] = preview_result['url']
            response_data['preview_uploaded'] = not preview_result.get('is_default', False)
            if preview_result.get('is_default'):
                response_data['preview_message'] = 'Создано дефолтное превью. Вы можете загрузить свое изображение.'
            else:
                response_data['preview_message'] = 'Превью успешно загружено!'
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

# API для загрузки карусели
@app.route('/api/upload-carousel', methods=['POST'])
def upload_carousel():
    try:
        if 'main_file' not in request.files or 'photo_file' not in request.files:
            return jsonify({'error': 'Необходимы оба файла: main и photo'}), 400
        
        main_file = request.files['main_file']
        photo_file = request.files['photo_file']
        name = request.form.get('name', '')
        category = request.form.get('category', '')
        
        if main_file.filename == '' or photo_file.filename == '':
            return jsonify({'error': 'Оба файла должны быть выбраны'}), 400
        
        if not (allowed_file(main_file.filename) and allowed_file(photo_file.filename)):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое файлов
        main_svg = main_file.read().decode('utf-8')
        photo_svg = photo_file.read().decode('utf-8')
        
        # Анализируем dyno поля
        main_dyno_info = {
            'has_dyno': has_dyno_fields_simple(main_svg),
            'fields': extract_dyno_fields_simple(main_svg)
        }
        
        photo_dyno_info = {
            'has_dyno': has_dyno_fields_simple(photo_svg),
            'fields': extract_dyno_fields_simple(photo_svg)
        }
        
        # Генерируем уникальные ID
        main_template_id = str(uuid.uuid4())
        photo_template_id = str(uuid.uuid4())
        carousel_id = str(uuid.uuid4())
        
        # Сохраняем шаблоны в базу данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Сохраняем main template
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [main_template_id, f"{name} - Main", category, "main", main_svg, ','.join(main_dyno_info.get('fields', []))])
        
        # Сохраняем photo template
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [photo_template_id, f"{name} - Photo", category, "photo", photo_svg, ','.join(photo_dyno_info.get('fields', []))])
        
        # Сохраняем карусель
        cursor.execute('''
            INSERT INTO carousels (id, name, main_template_id, photo_template_id)
            VALUES (?, ?, ?, ?)
        ''', [carousel_id, name, main_template_id, photo_template_id])
        
        conn.commit()
        conn.close()
        
        # Генерируем превью для обоих шаблонов
        print(f"🎨 Генерирую превью для main шаблона: {name} - Main")
        main_preview = generate_svg_preview(main_svg, main_template_id)
        
        print(f"🎨 Генерирую превью для photo шаблона: {name} - Photo")
        photo_preview = generate_svg_preview(photo_svg, photo_template_id)
        
        response_data = {
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_template_id,
            'photo_template_id': photo_template_id,
            'main_dyno_fields': main_dyno_info.get('fields', []) if main_dyno_info else [],
            'photo_dyno_fields': photo_dyno_info.get('fields', []) if photo_dyno_info else [],
            'message': f'Карусель "{name}" успешно загружена'
        }
        
        # Добавляем информацию о превью
        if main_preview['success']:
            response_data['main_preview_url'] = main_preview['url']
        if photo_preview['success']:
            response_data['photo_preview_url'] = photo_preview['url']
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки карусели: {str(e)}'}), 500

# API для загрузки карусели с множественными photo слайдами
@app.route('/api/upload-carousel-multi', methods=['POST'])
def upload_carousel_multi():
    try:
        if 'main_file' not in request.files:
            return jsonify({'error': 'Необходим main файл'}), 400
        
        main_file = request.files['main_file']
        name = request.form.get('name', '')
        category = request.form.get('category', '')
        photo_count = int(request.form.get('photo_count', 1))  # Количество photo слайдов
        
        if main_file.filename == '':
            return jsonify({'error': 'Main файл должен быть выбран'}), 400
        
        if not allowed_file(main_file.filename):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Проверяем что все photo файлы загружены
        photo_files = []
        for i in range(1, photo_count + 1):
            photo_file_key = f'photo_file_{i}'
            if photo_file_key not in request.files:
                return jsonify({'error': f'Необходим photo файл {i}'}), 400
            
            photo_file = request.files[photo_file_key]
            if photo_file.filename == '':
                return jsonify({'error': f'Photo файл {i} должен быть выбран'}), 400
            
            if not allowed_file(photo_file.filename):
                return jsonify({'error': f'Photo файл {i}: разрешены только SVG файлы'}), 400
            
            photo_files.append(photo_file)
        
        # Читаем содержимое main файла
        main_svg = main_file.read().decode('utf-8')
        
        # Анализируем dyno поля main
        main_dyno_info = {
            'has_dyno': has_dyno_fields_simple(main_svg),
            'fields': extract_dyno_fields_simple(main_svg)
        }
        
        # Генерируем уникальные ID
        main_template_id = str(uuid.uuid4())
        carousel_id = str(uuid.uuid4())
        photo_template_ids = []
        
        # Сохраняем шаблоны в базу данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Сохраняем main template
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [main_template_id, f"{name} - Main", category, "main", main_svg, ','.join(main_dyno_info.get('fields', []))])
        
        # Создаем множественные photo шаблоны из загруженных файлов
        for i, photo_file in enumerate(photo_files):
            photo_template_id = str(uuid.uuid4())
            photo_template_ids.append(photo_template_id)
            
            # Читаем содержимое photo файла
            photo_svg = photo_file.read().decode('utf-8')
            
            # Анализируем dyno поля photo
            photo_dyno_info = {
                'has_dyno': has_dyno_fields_simple(photo_svg),
                'fields': extract_dyno_fields_simple(photo_svg)
            }
            
            # Сохраняем photo template
            cursor.execute('''
                INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', [photo_template_id, f"{name} - Photo {i+1}", category, "photo", photo_svg, ','.join(photo_dyno_info.get('fields', []))])
        
        # Сохраняем карусель с множественными photo
        # Создаем отдельную запись для каждого photo слайда
        for i, photo_template_id in enumerate(photo_template_ids):
            cursor.execute('''
                INSERT INTO carousels (id, name, main_template_id, photo_template_id)
                VALUES (?, ?, ?, ?)
            ''', [str(uuid.uuid4()), f"{name} - Photo {i+1}", main_template_id, photo_template_id])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_template_id,
            'photo_template_ids': photo_template_ids,
            'photo_count': photo_count,
            'main_dyno_fields': main_dyno_info.get('fields', []) if main_dyno_info else [],
            'message': f'Карусель "{name}" с {photo_count} photo слайдами успешно загружена'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки карусели: {str(e)}'}), 500

# API роуты
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "API работает"})

# API для создания простой карусели (используется фронтендом)
@app.route('/api/carousel', methods=['POST'])
def create_carousel():
    """
    Простое создание карусели с автоматическим определением количества photo слайдов
    """
    try:
        data = request.get_json()
        print(f"📥 Простое создание карусели: {data}")
        
        main_template_name = data.get('main_template_name')
        photo_template_name = data.get('photo_template_name')
        replacements = data.get('replacements', {})
        
        # Перенаправляем на основной эндпоинт
        return create_and_generate_carousel()
        
    except Exception as e:
        print(f"❌ Ошибка простого создания карусели: {str(e)}")
        return jsonify({'error': f'Ошибка создания карусели: {str(e)}'}), 500

@app.route('/api/templates/all-previews')
def get_all_templates():
    """Получает все шаблоны с превью согласно требованиям фронта"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, category, template_role, svg_content FROM templates ORDER BY created_at DESC')
        templates_data = cursor.fetchall()
        
        conn.close()
        
        templates = []
        for template in templates_data:
            template_id = template[0]
            template_name = template[1]
            category = template[2]
            template_role = template[3]
            svg_content = template[4]
            
            # Проверяем, существует ли PNG превью
            preview_dir = os.path.join(OUTPUT_DIR, 'previews')
            os.makedirs(preview_dir, exist_ok=True)
            preview_path = os.path.join(preview_dir, f"{template_id}_preview.png")
            
            # Если превью не существует, генерируем его
            if not os.path.exists(preview_path):
                print(f"🖼️ Генерирую превью для шаблона: {template_id}")
                try:
                    # Конвертируем SVG в PNG с размером 400x600px как требует фронт
                    png_data = cairosvg.svg2png(
                        bytestring=svg_content.encode('utf-8'),
                        output_width=400,
                        output_height=600,
                        background_color='white'
                    )
                    
                    # Сохраняем PNG файл
                    with open(preview_path, 'wb') as f:
                        f.write(png_data)
                    
                    print(f"✅ Превью создано: {preview_path}")
                except Exception as e:
                    print(f"❌ Ошибка генерации превью для {template_id}: {e}")
                    return jsonify({'error': f'Ошибка генерации превью: {str(e)}'}), 500
            else:
                preview_url = f'/output/previews/{template_id}_preview.png'
            
            # Структура согласно требованиям фронта
            templates.append({
                'id': template_id,
                'name': template_name,
                'category': category,
                'template_role': template_role,
                'preview_url': preview_url
            })
        
        return jsonify({
            'templates': templates
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения шаблонов: {e}")
        return jsonify({'error': f'Ошибка получения шаблонов: {str(e)}'}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    """Получает превью конкретного шаблона"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Получаем SVG содержимое шаблона
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        conn.close()
        
        # Проверяем, существует ли PNG превью
        preview_dir = os.path.join(OUTPUT_DIR, 'previews')
        os.makedirs(preview_dir, exist_ok=True)
        preview_path = os.path.join(preview_dir, f"{template_id}_preview.png")
        
        # Если превью не существует, генерируем его
        if not os.path.exists(preview_path):
            print(f"🖼️ Генерирую превью для шаблона: {template_id}")
            try:
                # Конвертируем SVG в PNG с размером 400x600px как требует фронт
                png_data = cairosvg.svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    output_width=400,
                    output_height=600,
                    background_color='white'
                )
                
                # Сохраняем PNG файл
                with open(preview_path, 'wb') as f:
                    f.write(png_data)
                
                print(f"✅ Превью создано: {preview_path}")
            except Exception as e:
                print(f"❌ Ошибка генерации превью для {template_id}: {e}")
                return jsonify({'error': f'Ошибка генерации превью: {str(e)}'}), 500
        
        # Возвращаем URL к PNG превью
        return jsonify({
            'preview_url': f'/output/previews/{template_id}_preview.png'
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения превью: {e}")
        return jsonify({'error': f'Ошибка получения превью: {str(e)}'}), 500

@app.route('/api/templates/<template_id>/delete', methods=['DELETE'])
def delete_template(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существование шаблона
        cursor.execute('SELECT name FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name = result[0]
        
        # Удаляем шаблон
        cursor.execute('DELETE FROM templates WHERE id = ?', [template_id])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Шаблон "{template_name}" успешно удален'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка удаления: {str(e)}'}), 500

# API для получения всех каруселей (простой)
@app.route('/api/carousels', methods=['GET'])
def get_carousels():
    """Простой endpoint для получения списка карусели"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, main_template_id, photo_template_id, created_at
            FROM carousels
            ORDER BY created_at DESC
        ''')
        
        carousels_data = cursor.fetchall()
        conn.close()
        
        carousels = []
        for carousel in carousels_data:
            carousels.append({
                'id': carousel[0],
                'name': carousel[1],
                'category': carousel[2],
                'main_template_id': carousel[3],
                'photo_template_id': carousel[4],
                'created_at': carousel[5]
            })
        
        return jsonify({
            'success': True,
            'carousels': carousels,
            'count': len(carousels)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения карусели: {str(e)}'}), 500

# API для получения всех каруселей (полный)
@app.route('/api/carousels/all', methods=['GET'])
def get_all_carousels():
    """Получает все карусели с превью для main и photo шаблонов"""
    try:
        from manual_preview_system import get_template_preview_url
        
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Получаем все карусели с информацией о шаблонах
        cursor.execute('''
            SELECT c.id, c.name, c.category, c.main_template_id, c.photo_template_id, c.created_at,
                   mt.name as main_name, pt.name as photo_name,
                   mt.dyno_fields as main_dyno_fields, pt.dyno_fields as photo_dyno_fields
            FROM carousels c
            LEFT JOIN templates mt ON c.main_template_id = mt.id
            LEFT JOIN templates pt ON c.photo_template_id = pt.id
            ORDER BY c.created_at DESC
        ''')
        
        carousels_data = cursor.fetchall()
        conn.close()
        
        carousels = []
        for carousel in carousels_data:
            carousel_id = carousel[0]
            carousel_name = carousel[1]
            category = carousel[2]
            main_template_id = carousel[3]
            photo_template_id = carousel[4]
            created_at = carousel[5]
            main_name = carousel[6]
            photo_name = carousel[7]
            main_dyno_fields = carousel[8] if carousel[8] else ""
            photo_dyno_fields = carousel[9] if carousel[9] else ""
            
            # Получаем URL превью для main и photo шаблонов
            main_preview_url = get_template_preview_url(main_template_id) if main_template_id else ''
            photo_preview_url = get_template_preview_url(photo_template_id) if photo_template_id else ''
            
            carousel_info = {
                'id': carousel_id,
                'name': carousel_name,
                'category': category,
                'created_at': created_at,
                'main_template': {
                    'id': main_template_id,
                    'name': main_name,
                    'preview_url': main_preview_url,
                    'dyno_fields': main_dyno_fields.split(',') if main_dyno_fields else []
                },
                'photo_template': {
                    'id': photo_template_id,
                    'name': photo_name,
                    'preview_url': photo_preview_url,
                    'dyno_fields': photo_dyno_fields.split(',') if photo_dyno_fields else []
                }
            }
            
            carousels.append(carousel_info)
        
        return jsonify({
            'success': True,
            'carousels': carousels,
            'total_count': len(carousels)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения каруселей: {str(e)}'}), 500

# API для получения конкретной карусели
@app.route('/api/carousels/<carousel_id>', methods=['GET'])
def get_carousel(carousel_id):
    """Получает информацию о конкретной карусели"""
    try:
        from manual_preview_system import get_template_preview_url
        
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Получаем карусель с информацией о шаблонах
        cursor.execute('''
            SELECT c.id, c.name, c.category, c.main_template_id, c.photo_template_id, c.created_at,
                   mt.name as main_name, pt.name as photo_name,
                   mt.dyno_fields as main_dyno_fields, pt.dyno_fields as photo_dyno_fields
            FROM carousels c
            LEFT JOIN templates mt ON c.main_template_id = mt.id
            LEFT JOIN templates pt ON c.photo_template_id = pt.id
            WHERE c.id = ?
        ''', [carousel_id])
        
        carousel_data = cursor.fetchone()
        conn.close()
        
        if not carousel_data:
            return jsonify({'error': 'Карусель не найдена'}), 404
        
        carousel_id = carousel_data[0]
        carousel_name = carousel_data[1]
        category = carousel_data[2]
        main_template_id = carousel_data[3]
        photo_template_id = carousel_data[4]
        created_at = carousel_data[5]
        main_name = carousel_data[6]
        photo_name = carousel_data[7]
        main_dyno_fields = carousel_data[8] if carousel_data[8] else ""
        photo_dyno_fields = carousel_data[9] if carousel_data[9] else ""
        
        # Получаем URL превью для main и photo шаблонов
        main_preview_url = get_template_preview_url(main_template_id) if main_template_id else ''
        photo_preview_url = get_template_preview_url(photo_template_id) if photo_template_id else ''
        
        carousel_info = {
            'id': carousel_id,
            'name': carousel_name,
            'category': category,
            'created_at': created_at,
            'main_template': {
                'id': main_template_id,
                'name': main_name,
                'preview_url': main_preview_url,
                'dyno_fields': main_dyno_fields.split(',') if main_dyno_fields else []
            },
            'photo_template': {
                'id': photo_template_id,
                'name': photo_name,
                'preview_url': photo_preview_url,
                'dyno_fields': photo_dyno_fields.split(',') if photo_dyno_fields else []
            }
        }
        
        return jsonify({
            'success': True,
            'carousel': carousel_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения карусели: {str(e)}'}), 500

# API для генерации одиночного изображения
@app.route('/api/generate/single', methods=['POST'])
def generate_single():
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        replacements = data.get('replacements', {})
        
        if not template_id:
            return jsonify({'error': 'template_id обязателен'}), 400
        
        # Получаем шаблон из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name, svg_content = result
        
        # Обрабатываем SVG с идеальным сохранением шрифтов
        processed_svg = process_svg_font_perfect(svg_content, replacements)
        
        # Генерируем уникальное имя файла
        output_filename = f"single_{str(uuid.uuid4())}.svg"
        
        # Используем новую логику сохранения
        output_url = save_file_locally_or_supabase(processed_svg, output_filename, "single")
        
        if not output_url:
            return jsonify({'error': 'Ошибка сохранения файла'}), 500
        
        return jsonify({
            'success': True,
            'template_name': template_name,
            'output_url': output_url,
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500

# API для генерации карусели
@app.route('/api/generate/carousel', methods=['POST'])
def generate_carousel():
    try:
        data = request.get_json()
        print(f"📥 Входящий запрос: {data}")
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        # Фронтенд отправляет 'data' вместо 'replacements'
        replacements = data.get('data', data.get('replacements', {}))
        
        print(f"🔍 Received data: {data}")
        print(f"📋 Replacements: {replacements}")
        
        if not main_template_id or not photo_template_id:
            return jsonify({'error': 'main_template_id и photo_template_id обязательны'}), 400
        
        # Получаем шаблоны из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [main_template_id])
        main_result = cursor.fetchone()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [photo_template_id])
        photo_result = cursor.fetchone()
        
        # Если шаблоны не найдены, создаем динамические шаблоны
        if not main_result:
            print(f"⚠️ Шаблон {main_template_id} не найден, создаю динамический")
            create_dynamic_template(main_template_id, 'main')
            cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [main_template_id])
            main_result = cursor.fetchone()
        
        if not photo_result:
            print(f"⚠️ Шаблон {photo_template_id} не найден, создаю динамический")
            create_dynamic_template(photo_template_id, 'photo')
            cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [photo_template_id])
            photo_result = cursor.fetchone()
        
        conn.close()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Не удалось создать один или оба шаблона'}), 500
        
        main_name, main_svg_content = main_result
        photo_name, photo_svg_content = photo_result
        
        # Получаем реальные поля из SVG
        svg_fields_main = extract_dyno_fields_simple(main_svg_content)
        svg_fields_photo = extract_dyno_fields_simple(photo_svg_content)
        
        print(f"🔍 Main SVG поля: {svg_fields_main}")
        print(f"🔍 Photo SVG поля: {svg_fields_photo}")
        print(f"🔍 Все replacements: {replacements}")
        
        # Показываем все поля в photo SVG
        print("🔍 ВСЕ поля в photo SVG:")
        for field in svg_fields_photo:
            print(f"   - {field}")
        
        # Фильтруем replacements для main SVG
        filtered_replacements_main = {k: v for k, v in replacements.items() if k in svg_fields_main or field_mapping.get(k, k) in svg_fields_main}
        
        # Фильтруем replacements для photo SVG
        filtered_replacements_photo = {k: v for k, v in replacements.items() if k in svg_fields_photo or field_mapping.get(k, k) in svg_fields_photo}
        
        # Используем только те поля, которые фронт отправил
        print(f"✅ Используем оригинальные поля из replacements для photo template")
        
        print(f"🔍 Replacements для main SVG: {filtered_replacements_main}")
        print(f"🔍 Replacements для photo SVG: {filtered_replacements_photo}")
        
        # Дополнительная отладка для photo template
        print("🔍 Детальная проверка photo replacements:")
        for key, value in replacements.items():
            mapped_key = field_mapping.get(key, key)
            in_photo = key in svg_fields_photo or mapped_key in svg_fields_photo
            print(f"   {key} -> {mapped_key} -> в photo: {in_photo}")
        processed_main_svg = process_svg_font_perfect(main_svg_content, filtered_replacements_main)
        processed_photo_svg = process_svg_font_perfect(photo_svg_content, filtered_replacements_photo)
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Сохраняем обработанные SVG и конвертируем в JPG
        main_svg_filename = f"carousel_{carousel_id}_main.svg"
        photo_svg_filename = f"carousel_{carousel_id}_photo.svg"
        main_jpg_filename = f"carousel_{carousel_id}_main.jpg"
        photo_jpg_filename = f"carousel_{carousel_id}_photo.jpg"
        
        # Создаем папку carousel если не существует
        carousel_output_dir = os.path.join(OUTPUT_DIR, 'carousel')
        os.makedirs(carousel_output_dir, exist_ok=True)
        
        # Сохраняем SVG файлы
        main_svg_path = os.path.join(carousel_output_dir, main_svg_filename)
        photo_svg_path = os.path.join(carousel_output_dir, photo_svg_filename)
        
        with open(main_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        print(f"💾 Сохраняю main SVG: {main_filename}")
        print(f"💾 Сохраняю photo SVG: {photo_filename}")
        
        # Используем новую логику сохранения
        main_url = save_file_locally_or_supabase(processed_main_svg, main_filename, "carousel")
        photo_url = save_file_locally_or_supabase(processed_photo_svg, photo_filename, "carousel")
        
        if not main_url or not photo_url:
            return jsonify({'error': 'Ошибка сохранения файлов'}), 500
        
        # Конвертируем в JPG
        main_jpg_path = os.path.join(carousel_output_dir, main_jpg_filename)
        photo_jpg_path = os.path.join(carousel_output_dir, photo_jpg_filename)
        
        main_jpg_success = convert_svg_to_jpg(processed_main_svg, main_jpg_path)
        photo_jpg_success = convert_svg_to_jpg(processed_photo_svg, photo_jpg_path)
        
        # Создаем массив изображений для совместимости с фронтендом
        images = [
            {
                'slide_number': 1,
                'template_id': main_template_id,
                'template_name': main_name,
                'filename': main_jpg_filename if main_jpg_success else main_svg_filename,
                'url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
                'status': 'completed'
            },
            {
                'slide_number': 2,
                'template_id': photo_template_id,
                'template_name': photo_name,
                'filename': photo_jpg_filename if photo_jpg_success else photo_svg_filename,
                'url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
                'status': 'completed'
            }
        ]
        
        # Создаем простые массивы URL для фронтенда (предпочитаем JPG)
        image_urls = [
            f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
            f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}'
        ]
        
        response_data = {
            'success': True,
            'carousel_id': carousel_id,
            'main_template_name': main_name,
            'photo_template_name': photo_name,
            'main_url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
            'photo_url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
            'replacements_applied': len(replacements),
            # Простые массивы URL для совместимости с фронтендом
            'images': image_urls,  # Простой массив строк URL
            'slides': image_urls,  # Простой массив строк URL
            'urls': image_urls,    # Простой массив строк URL
            'image_url': image_urls[0],  # Первое изображение
            'data': {'images': image_urls},  # С вложенными данными
            # Детальная информация для расширенного использования
            'images_detailed': images,  # Массив объектов с дополнительной информацией
            'slides_count': 2,
            'status': 'completed',
            'format': 'jpg' if main_jpg_success and photo_jpg_success else 'svg',
            # Дополнительные поля для совместимости
            'images_detailed_alt': [
                {
                    'type': 'main',
                    'url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
                    'template_name': main_name
                },
                {
                    'type': 'photo',
                    'url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
                    'template_name': photo_name
                }
            ]
        }
        
        print(f"🔍 /api/generate/carousel response: {response_data}")
        print(f"📊 Images count: {len(images)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации карусели: {str(e)}'}), 500

# API для генерации карусели по именам шаблонов
@app.route('/api/generate/carousel-by-name', methods=['POST'])
def generate_carousel_by_name():
    """
    Создает карусель используя имена шаблонов вместо ID
    """
    try:
        data = request.get_json()
        print(f"📥 Входящий запрос (by-name): {data}")
        main_template_name = data.get('main_template_name')
        photo_template_name = data.get('photo_template_name')
        replacements = data.get('replacements', {})
        
        if not main_template_name or not photo_template_name:
            return jsonify({'error': 'main_template_name и photo_template_name обязательны'}), 400
        
        print(f"🔍 Ищу шаблоны по именам:")
        print(f"   Main: {main_template_name}")
        print(f"   Photo: {photo_template_name}")
        
        # Получаем шаблоны из базы данных по именам
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ищем main шаблон
        cursor.execute('SELECT id, name, svg_content FROM templates WHERE name = ?', [main_template_name])
        main_result = cursor.fetchone()
        
        if not main_result:
            conn.close()
            return jsonify({'error': f'Main шаблон "{main_template_name}" не найден'}), 404
        
        # Ищем photo шаблон
        cursor.execute('SELECT id, name, svg_content FROM templates WHERE name = ?', [photo_template_name])
        photo_result = cursor.fetchone()
        
        if not photo_result:
            conn.close()
            return jsonify({'error': f'Photo шаблон "{photo_template_name}" не найден'}), 404
        
        conn.close()
        
        main_id, main_name, main_svg = main_result
        photo_id, photo_name, photo_svg = photo_result
        
        print(f"✅ Найдены шаблоны:")
        print(f"   Main: {main_name} (ID: {main_id})")
        print(f"   Photo: {photo_name} (ID: {photo_id})")
        
        # Обрабатываем SVG с идеальным сохранением шрифтов
        print(f"🔍 Replacements получены: {replacements}")
        print(f"🔍 Main SVG поля: {extract_dyno_fields_simple(main_svg)}")
        print(f"🔍 Photo SVG поля: {extract_dyno_fields_simple(photo_svg)}")
        
        # Фильтруем replacements для каждого шаблона
        svg_fields_main = extract_dyno_fields_simple(main_svg)
        svg_fields_photo = extract_dyno_fields_simple(photo_svg)
        
        # Показываем все поля в photo SVG
        print("🔍 ВСЕ поля в photo SVG:")
        for field in svg_fields_photo:
            print(f"   - {field}")
        
        filtered_replacements_main = {k: v for k, v in replacements.items() if k in svg_fields_main or field_mapping.get(k, k) in svg_fields_main}
        filtered_replacements_photo = {k: v for k, v in replacements.items() if k in svg_fields_photo or field_mapping.get(k, k) in svg_fields_photo}
        
        # Используем только те поля, которые фронт отправил
        print(f"✅ Используем оригинальные поля из replacements для photo template")
        
        print(f"🔍 Filtered replacements для main: {filtered_replacements_main}")
        print(f"🔍 Filtered replacements для photo: {filtered_replacements_photo}")
        
        print("🎨 Обрабатываю Main шаблон...")
        processed_main_svg = process_svg_font_perfect(main_svg, filtered_replacements_main)
        
        print("🎨 Обрабатываю Photo шаблон...")
        processed_photo_svg = process_svg_font_perfect(photo_svg, filtered_replacements_photo)
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Создаем директорию если не существует
        os.makedirs(os.path.join(OUTPUT_DIR, 'carousel'), exist_ok=True)
        
        # Генерируем имена файлов
        main_svg_filename = f"carousel_{carousel_id}_main.svg"
        photo_svg_filename = f"carousel_{carousel_id}_photo.svg"
        main_jpg_filename = f"carousel_{carousel_id}_main.jpg"
        photo_jpg_filename = f"carousel_{carousel_id}_photo.jpg"
        
        # Создаем директорию если не существует
        os.makedirs(os.path.join(OUTPUT_DIR, 'carousel'), exist_ok=True)
        
        # Сохраняем SVG файлы
        main_svg_path = os.path.join(OUTPUT_DIR, 'carousel', main_svg_filename)
        photo_svg_path = os.path.join(OUTPUT_DIR, 'carousel', photo_svg_filename)
        
        with open(main_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        print(f"💾 Сохраняю main SVG: {main_filename}")
        print(f"💾 Сохраняю photo SVG: {photo_filename}")
        
        # Используем новую логику сохранения
        main_url = save_file_locally_or_supabase(processed_main_svg, main_filename, "carousel")
        photo_url = save_file_locally_or_supabase(processed_photo_svg, photo_filename, "carousel")
        
        if not main_url or not photo_url:
            return jsonify({'error': 'Ошибка сохранения файлов'}), 500
        
        # Конвертируем в JPG
        main_jpg_path = os.path.join(OUTPUT_DIR, 'carousel', main_jpg_filename)
        photo_jpg_path = os.path.join(OUTPUT_DIR, 'carousel', photo_jpg_filename)
        
        main_jpg_success = convert_svg_to_jpg(processed_main_svg, main_jpg_path)
        photo_jpg_success = convert_svg_to_jpg(processed_photo_svg, photo_jpg_path)
        
        print(f"🎉 Карусель создана: {carousel_id}")
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_id,
            'photo_template_id': photo_id,
            'main_template_name': main_name,
            'photo_template_name': photo_name,
            'main_url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
            'photo_url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
            'replacements_applied': len(replacements),
            'format': 'jpg' if main_jpg_success and photo_jpg_success else 'svg',
            # Дополнительные поля для совместимости
            'images_detailed': [
                {
                    'type': 'main',
                    'url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
                    'template_name': main_name
                },
                {
                    'type': 'photo',
                    'url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
                    'template_name': photo_name
                }
            ]
        })
        
    except Exception as e:
        print(f"❌ Ошибка генерации карусели по именам: {str(e)}")
        return jsonify({'error': f'Ошибка генерации карусели: {str(e)}'}), 500

# API для создания и генерации полноценной карусели (до 10 слайдов)
@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    """
    Создает полноценную карусель с main слайдом + до 9 фото слайдов
    Поддерживает dyno.propertyimage2, dyno.propertyimage3, ... dyno.propertyimage10
    
    Также поддерживает создание карусели с правильным маппингом полей:
    - Main слайд: dyno.propertyimage, dyno.agentheadshot и т.д.
    - Photo слайд 1: dyno.propertyimage2
    - Photo слайд 2: dyno.propertyimage3
    - И так далее до dyno.propertyimage10
    """
    try:
        data = request.get_json()
        print(f"📥 Входящий запрос create-and-generate: {data}")
        
        # Поддерживаем оба формата
        carousel_name = data.get('name', 'Untitled Carousel')
        slides = data.get('slides', [])
        main_template_name = data.get('main_template_name')
        photo_template_name = data.get('photo_template_name')
        replacements = data.get('replacements', {})
        slides_count = data.get('slides_count', 0)  # Новое поле для количества слайдов
        
        # Если передан новый формат с template names
        if main_template_name and photo_template_name:
            print(f"🔍 Ищу шаблоны по именам:")
            print(f"   Main: {main_template_name}")
            print(f"   Photo: {photo_template_name}")
            print(f"   Количество слайдов: {slides_count}")
            
            # Получаем шаблоны из базы данных по именам
            ensure_db_exists()
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Ищем main шаблон
            cursor.execute('SELECT id, name, svg_content FROM templates WHERE name = ?', [main_template_name])
            main_result = cursor.fetchone()
            
            if not main_result:
                conn.close()
                return jsonify({'error': f'Main шаблон "{main_template_name}" не найден'}), 404
            
            # Ищем photo шаблон
            cursor.execute('SELECT id, name, svg_content FROM templates WHERE name = ?', [photo_template_name])
            photo_result = cursor.fetchone()
            
            if not photo_result:
                conn.close()
                return jsonify({'error': f'Photo шаблон "{photo_template_name}" не найден'}), 404
            
            conn.close()
            
            main_id, main_name, main_svg = main_result
            photo_id, photo_name, photo_svg = photo_result
            
            print(f"✅ Найдены шаблоны:")
            print(f"   Main: {main_name} (ID: {main_id})")
            print(f"   Photo: {photo_name} (ID: {photo_id})")
            
            # Используем slides_count из payload вместо автоматического подсчета
            photo_count = slides_count
            print(f"🔍 Используем количество слайдов из payload: {photo_count}")
            
            # Проверяем, что есть достаточно изображений для указанного количества слайдов
            property_image_fields = []
            for i in range(2, photo_count + 2):  # propertyimage2, propertyimage3, etc.
                field_name = f'dyno.propertyimage{i}'
                if field_name in replacements:
                    property_image_fields.append((field_name, i))
                else:
                    print(f"⚠️ Поле {field_name} не найдено в replacements")
            
            if len(property_image_fields) < photo_count:
                print(f"⚠️ Предупреждение: запрошено {photo_count} слайдов, но найдено только {len(property_image_fields)} изображений")
                photo_count = len(property_image_fields)
            
            print(f"🔍 Создаем {photo_count} photo слайдов")
            print(f"🔍 Все replacements: {list(replacements.keys())}")
            
            # Обрабатываем main SVG (используем dyno.propertyimage, dyno.agentheadshot и т.д.)
            print("🎨 Обрабатываю Main шаблон...")
            svg_fields_main = extract_dyno_fields_simple(main_svg)
            print(f"🔍 Main SVG поля: {svg_fields_main}")
            
            # Для main используем ВСЕ поля из replacements
            main_replacements = replacements.copy()
            
            # Убираем служебные поля, которые не нужны для SVG
            if 'dyno.slides_count' in main_replacements:
                del main_replacements['dyno.slides_count']
                print(f"   🚫 Убираю служебное поле dyno.slides_count")
            if 'dyno.generate_multiple' in main_replacements:
                del main_replacements['dyno.generate_multiple']
                print(f"   🚫 Убираю служебное поле dyno.generate_multiple")
            
            print(f"🔍 Main replacements: {main_replacements}")
            processed_main_svg = process_svg_font_perfect(main_svg, main_replacements)
            
            # Генерируем уникальный ID карусели
            carousel_id = str(uuid.uuid4())
            
            # Сохраняем main файл
            main_filename = f"carousel_{carousel_id}_main.svg"
            main_url = save_file_locally_or_supabase(processed_main_svg, main_filename, "carousel")
            
            if not main_url:
                return jsonify({'error': 'Ошибка сохранения main файла'}), 500
            
            # Создаем photo слайды
            photo_urls = []
            images = [
                {
                    'type': 'main',
                    'url': main_url,
                    'template_name': main_name
                }
            ]
            
            for i, (property_image_field, field_number) in enumerate(property_image_fields):
                print(f"🎨 Обрабатываю Photo слайд {i+1} (поле: {property_image_field})...")
                
                # Создаем replacements для этого photo слайда
                photo_replacements = replacements.copy()  # Копируем ВСЕ поля
                
                # Убираем headshot поля из photo слайдов
                headshot_fields = ['dyno.agentheadshot', 'dyno.agentphoto', 'dyno.headshot', 'dyno.agent', 'dyno.photo']
                for headshot_field in headshot_fields:
                    if headshot_field in photo_replacements:
                        del photo_replacements[headshot_field]
                        print(f"   🚫 Убираю {headshot_field} с photo слайда {i+1}")
                
                # Проверяем, есть ли в photo SVG поле dyno.propertyimage
                svg_fields_photo = extract_dyno_fields_simple(photo_svg)
                print(f"🔍 Photo SVG поля: {svg_fields_photo}")
                
                # Если в photo SVG есть dyno.propertyimage, заменяем его на соответствующее
                if 'dyno.propertyimage' in svg_fields_photo:
                    photo_replacements['dyno.propertyimage'] = replacements[property_image_field]
                    print(f"   📸 Заменяю dyno.propertyimage на {property_image_field} = {replacements[property_image_field]}")
                else:
                    # Если dyno.propertyimage нет, но есть другое поле с изображением, заменяем его
                    for field in svg_fields_photo:
                        if 'image' in field.lower() and field != 'dyno.propertyimage':
                            photo_replacements[field] = replacements[property_image_field]
                            print(f"   📸 Заменяю {field} на {property_image_field} = {replacements[property_image_field]}")
                            break
                
                print(f"🔍 Photo {i+1} replacements: {photo_replacements}")
                processed_photo_svg = process_svg_font_perfect(photo_svg, photo_replacements)
                
                # Сохраняем photo файл
                photo_filename = f"carousel_{carousel_id}_photo_{i+1}.svg"
                photo_url = save_file_locally_or_supabase(processed_photo_svg, photo_filename, "carousel")
                
                if photo_url:
                    photo_urls.append(photo_url)
                    
                    # Конвертируем в JPG
                    jpg_filename = f"carousel_{carousel_id}_photo_{i+1}.jpg"
                    jpg_path = os.path.join(OUTPUT_DIR, "carousel", jpg_filename)
                    
                    try:
                        convert_svg_to_jpg(processed_photo_svg, jpg_path)
                        # Читаем JPG файл как bytes и передаем напрямую
                        with open(jpg_path, 'rb') as jpg_file:
                            jpg_data = jpg_file.read()
                        jpg_url = save_file_locally_or_supabase(jpg_data, jpg_filename, "carousel")
                        
                        if jpg_url:
                            images.append({
                                'type': f'photo_{i+1}',
                                'svg_url': photo_url,
                                'jpg_url': jpg_url,
                                'template_name': photo_name,
                                'property_image': replacements[property_image_field]
                            })
                            print(f"   ✅ Photo слайд {i+1} создан: {jpg_url}")
                        else:
                            print(f"   ⚠️ Photo слайд {i+1} SVG сохранен, но JPG не удалось сохранить")
                    except Exception as e:
                        print(f"   ❌ Ошибка конвертации Photo слайд {i+1} в JPG: {e}")
                        # Добавляем только SVG если JPG не удалось
                        images.append({
                            'type': f'photo_{i+1}',
                            'svg_url': photo_url,
                            'jpg_url': None,
                            'template_name': photo_name,
                            'property_image': replacements[property_image_field]
                        })
                else:
                    print(f"   ❌ Ошибка сохранения Photo слайд {i+1}")
            
            print(f"🎉 Карусель создана: {carousel_id}")
            print(f"📊 Создано слайдов: 1 main + {len(photo_urls)} photo")
            
            return jsonify({
                'success': True,
                'carousel_id': carousel_id,
                'main_template_name': main_name,
                'photo_template_name': photo_name,
                'images': images,
                'main_url': main_url,
                'photo_urls': photo_urls,
                'total_slides': 1 + len(photo_urls),
                'replacements_applied': len(replacements)
            })
        
        # Старый формат с массивом slides
        if not slides:
            return jsonify({'error': 'Массив slides обязателен'}), 400
        
        print(f"🎠 Создаю карусель: {carousel_name}")
        print(f"📊 Количество слайдов: {len(slides)}")
        print(f"📋 Данные слайдов: {slides}")
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Создаем директорию для карусели
        carousel_dir = os.path.join(OUTPUT_DIR, 'carousel', carousel_id)
        os.makedirs(carousel_dir, exist_ok=True)
        
        # Получаем шаблоны из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Сохраняем main template
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [main_template_id, f"{name} - Main", category, "main", main_svg, ','.join(main_dyno_info.get('fields', []))])
        
        # Сохраняем photo template
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [photo_template_id, f"{name} - Photo", category, "photo", photo_svg, ','.join(photo_dyno_info.get('fields', []))])
        
        # Сохраняем карусель
        cursor.execute('''
            INSERT INTO carousels (id, name, main_template_id, photo_template_id)
            VALUES (?, ?, ?, ?)
        ''', [carousel_id, name, main_template_id, photo_template_id])
        
        conn.commit()
        conn.close()
        
        # Генерируем превью для обоих шаблонов
        print(f"🎨 Генерирую превью для main шаблона: {name} - Main")
        main_preview = generate_svg_preview(main_svg, main_template_id)
        
        print(f"🎨 Генерирую превью для photo шаблона: {name} - Photo")
        photo_preview = generate_svg_preview(photo_svg, photo_template_id)
        
        response_data = {
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_template_id,
            'photo_template_id': photo_template_id,
            'main_dyno_fields': main_dyno_info.get('fields', []) if main_dyno_info else [],
            'photo_dyno_fields': photo_dyno_info.get('fields', []) if photo_dyno_info else [],
            'message': f'Карусель "{name}" успешно загружена'
        }
        
        # Добавляем информацию о превью
        if main_preview['success']:
            response_data['main_preview_url'] = main_preview['url']
        if photo_preview['success']:
            response_data['photo_preview_url'] = photo_preview['url']
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка создания карусели: {str(e)}")
        return jsonify({'error': f'Ошибка создания карусели: {str(e)}'}), 500

# API для получения статуса карусели
@app.route('/api/carousel/<carousel_id>/slides', methods=['GET'])
def get_carousel_slides(carousel_id):
    """
    Возвращает информацию о слайдах карусели
    """
    try:
        print(f"📊 Получаю информацию о карусели: {carousel_id}")
        
        # Проверяем существование карусели
        carousel_dir = os.path.join(OUTPUT_DIR, 'carousel', carousel_id)
        
        if not os.path.exists(carousel_dir):
            return jsonify({'error': 'Карусель не найдена'}), 404
        
        # Получаем информацию из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, slides_count, created_at FROM carousels_full WHERE id = ?', [carousel_id])
        carousel_result = cursor.fetchone()
        
        conn.close()
        
        if not carousel_result:
            return jsonify({'error': 'Информация о карусели не найдена'}), 404
        
        carousel_name, slides_count, created_at = carousel_result
        
        # Сканируем файлы в директории
        slides = []
        for i in range(1, slides_count + 1):
            slide_svg_filename = f"slide_{i:02d}.svg"
            slide_jpg_filename = f"slide_{i:02d}.jpg"
            
            slide_svg_path = os.path.join(carousel_dir, slide_svg_filename)
            slide_jpg_path = os.path.join(carousel_dir, slide_jpg_filename)
            
            # Проверяем наличие JPG файла (предпочтительно)
            if os.path.exists(slide_jpg_path):
                slides.append({
                    'slide_number': i,
                    'filename': slide_jpg_filename,
                    'image_url': f'/output/carousel/{carousel_id}/{slide_jpg_filename}',
                    'status': 'completed',
                    'format': 'jpg'
                })
            elif os.path.exists(slide_svg_path):
                slides.append({
                    'slide_number': i,
                    'filename': slide_svg_filename,
                    'image_url': f'/output/carousel/{carousel_id}/{slide_svg_filename}',
                    'status': 'completed',
                    'format': 'svg'
                })
            else:
                slides.append({
                    'slide_number': i,
                    'filename': slide_svg_filename,
                    'image_url': '',
                    'status': 'error'
                })
        
        return jsonify({
            'carousel_id': carousel_id,
            'name': carousel_name,
            'status': 'completed',
            'slides_count': slides_count,
            'created_at': created_at,
            'slides': slides
        })
        
    except Exception as e:
        print(f"❌ Ошибка получения информации о карусели: {str(e)}")
        return jsonify({'error': f'Ошибка получения информации: {str(e)}'}), 500

# API для превью SVG
@app.route('/api/preview/template/<template_id>', methods=['GET'])
def preview_template(template_id):
    """Генерирует превью шаблона без данных"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name, svg_content = result
        
        # Получаем параметры из query string
        preview_type = request.args.get('type', 'png')
        width = int(request.args.get('width', 400))
        height = int(request.args.get('height', 300))
        
        # Генерируем превью
        preview_result = generate_svg_preview(svg_content, preview_type, width, height)
        
        if preview_result['success']:
            preview_result['template_name'] = template_name
            preview_result['template_id'] = template_id
            return jsonify(preview_result)
        else:
            return jsonify({'error': preview_result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации превью: {str(e)}'}), 500

@app.route('/api/preview/with-data', methods=['POST'])
def preview_with_data():
    """Генерирует превью шаблона с заполненными данными"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        replacements = data.get('replacements', {})
        preview_type = data.get('type', 'png')
        width = int(data.get('width', 400))
        height = int(data.get('height', 300))
        
        if not template_id:
            return jsonify({'error': 'template_id обязателен'}), 400
        
        # Получаем шаблон из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name, svg_content = result
        
        # Создаем превью с данными
        preview_result = create_preview_with_data(svg_content, replacements, preview_type)
        
        if preview_result['success']:
            preview_result['template_name'] = template_name
            preview_result['template_id'] = template_id
            return jsonify(preview_result)
        else:
            return jsonify({'error': preview_result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации превью с данными: {str(e)}'}), 500

@app.route('/api/preview/carousel', methods=['POST'])
def preview_carousel():
    """Генерирует превью карусели (main + photo слайды)"""
    try:
        data = request.get_json()
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        replacements = data.get('replacements', {})
        preview_type = data.get('type', 'png')
        
        if not main_template_id or not photo_template_id:
            return jsonify({'error': 'main_template_id и photo_template_id обязательны'}), 400
        
        # Получаем шаблоны из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [main_template_id])
        main_result = cursor.fetchone()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [photo_template_id])
        photo_result = cursor.fetchone()
        
        conn.close()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Один или оба шаблона не найдены'}), 404
        
        main_name, main_svg = main_result
        photo_name, photo_svg = photo_result
        
        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        photo_preview = create_preview_with_data(photo_svg, replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,
                **main_preview
            },
            'photo_preview': {
                'template_name': photo_name,
                'template_id': photo_template_id,
                **photo_preview
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации превью карусели: {str(e)}'}), 500

@app.route('/api/preview/cleanup', methods=['POST'])
def cleanup_previews():
    """Очищает старые превью файлы"""
    try:
        max_age_hours = request.json.get('max_age_hours', 24) if request.json else 24
        cleanup_old_previews(max_age_hours)
        
        return jsonify({
            'success': True,
            'message': f'Превью старше {max_age_hours} часов удалены'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка очистки превью: {str(e)}'}), 500

def convert_svg_to_jpg(svg_content, output_path, width=1200, height=800, quality=95):
    """
    Конвертирует SVG в JPG с высоким качеством
    """
    try:
        print(f"🖼️ Конвертирую SVG в JPG: {output_path}")
        
        # Конвертация через cairosvg в PNG сначала
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            dpi=300  # Высокое качество
        )
        
        # Конвертируем PNG в JPG через PIL
        img = Image.open(io.BytesIO(png_data))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Сохраняем как JPG
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        print(f"✅ JPG файл создан: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конвертации SVG в JPG: {e}")
        return False

def convert_svg_to_png(svg_content, output_path, width=1200, height=800):
    """
    Конвертирует SVG в PNG с высоким качеством
    """
    try:
        print(f"🖼️ Конвертирую SVG в PNG: {output_path}")
        
        # Конвертация через cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            dpi=300  # Высокое качество
        )
        
        # Сохраняем PNG файл
        with open(output_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ PNG файл создан: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конвертации SVG в PNG: {e}")
        return False

# API для генерации карусели с множественными photo слайдами
@app.route('/api/generate/carousel-multi', methods=['POST'])
def generate_carousel_multi():
    """
    Создает карусель с множественными photo слайдами
    """
    try:
        data = request.get_json()
        print(f"📥 Входящий запрос (multi): {data}")
        main_template_id = data.get('main_template_id')
        photo_template_ids = data.get('photo_template_ids', [])  # Список ID photo шаблонов
        replacements = data.get('replacements', {})
        
        if not main_template_id or not photo_template_ids:
            return jsonify({'error': 'main_template_id и photo_template_ids обязательны'}), 400
        
        # Получаем шаблоны из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [main_template_id])
        main_result = cursor.fetchone()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [photo_template_id])
        photo_result = cursor.fetchone()
        
        conn.close()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Один или оба шаблона не найдены'}), 404
        
        main_name, main_svg = main_result
        photo_name, photo_svg = photo_result
        
        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        photo_preview = create_preview_with_data(photo_svg, replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,
                **main_preview
            },
            'photo_preview': {
                'template_name': photo_name,
                'template_id': photo_template_id,
                **photo_preview
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации превью карусели: {str(e)}'}), 500

def find_alternative_field(field, replacements):
    """Ищет альтернативное название поля в replacements"""
    field_lower = field.lower()
    
    # Маппинг для headshot полей - РАСШИРЕННЫЙ
    if 'headshot' in field_lower or 'agent' in field_lower or 'photo' in field_lower:
        headshot_alternatives = ['dyno.agentheadshot', 'dyno.agentphoto', 'dyno.headshot', 'dyno.agent', 'dyno.photo', 'dyno.agentPhoto', 'dyno.agentName']
        for alt in headshot_alternatives:
            if alt in replacements:
                return alt
    
    # Маппинг для property image полей
    elif 'propertyimage' in field_lower:
        # Ищем любое propertyimage поле
        for key in replacements.keys():
            if 'propertyimage' in key.lower():
                return key
    
    # Маппинг для logo полей
    elif 'logo' in field_lower:
        logo_alternatives = ['dyno.logo', 'dyno.companylogo', 'dyno.brandlogo']
        for alt in logo_alternatives:
            if alt in replacements:
                return alt
    
    # Маппинг для текстовых полей
    elif any(keyword in field_lower for keyword in ['name', 'title', 'address', 'price']):
        # Ищем похожие поля по ключевым словам
        for key in replacements.keys():
            if any(keyword in key.lower() for keyword in ['name', 'title', 'address', 'price']):
                return key
    
    return None

if __name__ == '__main__':
    ensure_db_exists()
    
    cleanup_old_previews()
    
    # Для локальной разработки
    app.run(host='0.0.0.0', port=5001, debug=True)
