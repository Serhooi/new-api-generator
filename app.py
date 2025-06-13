"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИДЕАЛЬНАЯ ОБРАБОТКА ШРИФТОВ
================================================================

Версия 9.0 - Полная версия с АБСОЛЮТНЫМ сохранением шрифтов Montserrat и исправлением экранирования спецсимволов
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

app = Flask(__name__)
CORS(app, origins="*")

# Устанавливаем максимальный размер загружаемого файла (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Конфигурация
DATABASE_PATH = 'templates.db'
OUTPUT_DIR = 'output'
ALLOWED_EXTENSIONS = {'svg'}

# Создаем директории
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('output/single', exist_ok=True)
os.makedirs('output/carousel', exist_ok=True)

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

def process_svg_font_perfect(svg_content, replacements):
    """
    ФИНАЛЬНАЯ функция с исправлением круглых хедшотов
    - Автоматическое определение формы элемента (круглый vs прямоугольный)
    - Правильный aspect ratio для каждого типа
    - Поддержка use элементов в pattern блоках
    - Сохранение оригинальных шрифтов Inter и Montserrat
    - Автоматический перенос длинных адресов на две строки
    - ПОЛНОЕ экранирование всех спецсимволов для URL и текстов
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
        """Определение типа изображения по названию поля"""
        field_lower = dyno_field.lower()
        
        headshot_keywords = ['headshot', 'agent', 'profile', 'portrait', 'realtor', 'agentheadshot']
        property_keywords = ['propertyimage', 'property', 'house', 'home', 'building', 'listing']
        logo_keywords = ['logo', 'companylogo', 'brand', 'brandlogo']
        
        for keyword in headshot_keywords:
            if keyword in field_lower:
                return 'headshot'
        
        for keyword in property_keywords:
            if keyword in field_lower:
                return 'property'
        
        for keyword in logo_keywords:
            if keyword in field_lower:
                return 'logo'
        
        return 'generic_image'
    
    def get_aspect_ratio_for_image(image_type, element_shape):
        """Возвращает правильный preserveAspectRatio для типа изображения и формы элемента"""
        
        if image_type == 'headshot':
            if element_shape == 'circular':
                # КРИТИЧНО: для круглых хедшотов используем slice!
                return 'xMidYMid slice'
            else:
                # Для прямоугольных хедшотов используем meet
                return 'xMidYMid meet'
        
        elif image_type == 'property':
            # Недвижимость всегда slice (cover эффект)
            return 'xMidYMid slice'
        
        elif image_type == 'logo':
            # Логотипы всегда meet (сохранение пропорций)
            return 'xMidYMid meet'
        
        else:
            # По умолчанию meet (безопасно)
            return 'xMidYMid meet'
    
    def is_image_field(dyno_field):
        """Определяет, является ли поле изображением"""
        field_lower = dyno_field.lower()
        explicit_image_indicators = ['image', 'headshot', 'logo', 'photo', 'pic', 'portrait']
        
        for indicator in explicit_image_indicators:
            if indicator in field_lower:
                return True
        
        if 'agent' in field_lower and any(img in field_lower for img in ['photo', 'image', 'pic', 'headshot']):
            return True
        
        return False
    
    def is_address_field(dyno_field):
        """Определяет, является ли поле адресом"""
        field_lower = dyno_field.lower()
        address_keywords = ['address', 'location', 'addr', 'street', 'propertyaddress']
        
        for keyword in address_keywords:
            if keyword in field_lower:
                return True
        
        return False
    
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
    
    # Маппинг полей для поддержки разных названий
    field_mapping = {
        'dyno.agentname': 'dyno.name',
        'dyno.agentemail': 'dyno.email', 
        'dyno.agentphone': 'dyno.phone'
    }
    
    # Обрабатываем каждое поле с учетом маппинга
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Проверяем основное поле
        original_field = dyno_field
        
        # Проверяем альтернативные названия полей
        if dyno_field in field_mapping:
            alternative_field = field_mapping[dyno_field]
            print(f"   🔄 Проверяю альтернативное название поля: {alternative_field}")
        else:
            alternative_field = None
        
        if is_image_field(dyno_field):
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ
            image_type = determine_image_type(dyno_field)
            
            print(f"   🖼️ Обрабатываю изображение: {dyno_field}")
            print(f"      📐 Тип изображения: {image_type}")
            
            # ИСПРАВЛЕНО: Используем полное экранирование для URL
            safe_url = safe_escape_for_svg(str(replacement))
            print(f"      🔒 Применено полное экранирование URL")
            
            # Ищем элемент с id и извлекаем pattern
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            # Если не нашли по основному имени, пробуем альтернативное
            if not match and alternative_field:
                element_pattern = f'<[^>]*id="{re.escape(alternative_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
                match = re.search(element_pattern, processed_svg)
                if match:
                    print(f"      ✅ Найдено по альтернативному имени: {alternative_field}")
                    dyno_field = alternative_field
            
            if match:
                pattern_id = match.group(1)
                print(f"      🎯 Найден pattern: {pattern_id}")
                
                # ОПРЕДЕЛЯЕМ ФОРМУ ЭЛЕМЕНТА
                element_shape = determine_element_shape(processed_svg, pattern_id)
                print(f"      🔍 Форма элемента: {element_shape}")
                
                # ВЫБИРАЕМ ПРАВИЛЬНЫЙ ASPECT RATIO
                aspect_ratio = get_aspect_ratio_for_image(image_type, element_shape)
                print(f"      ⚙️ Aspect ratio: {aspect_ratio}")
                
                # Ищем pattern блок
                pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                pattern_match = re.search(pattern_block_pattern, processed_svg, re.DOTALL)
                
                if pattern_match:
                    pattern_content = pattern_match.group(1)
                    
                    # Ищем use элемент внутри pattern
                    use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
                    use_match = re.search(use_pattern, pattern_content)
                    
                    if use_match:
                        image_id = use_match.group(1)
                        print(f"      🔗 Найден use элемент: #{image_id}")
                        
                        # Ищем соответствующий image элемент
                        image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
                        image_match = re.search(image_pattern, processed_svg)
                        
                        if image_match:
                            old_image = image_match.group(0)
                            new_image = old_image
                            
                            # Заменяем URL с полным экранированием
                            new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
                            new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                            
                            # КРИТИЧНО: Устанавливаем правильный preserveAspectRatio
                            if 'preserveAspectRatio=' in new_image:
                                new_image = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', new_image)
                            else:
                                if new_image.endswith('/>'):
                                    new_image = new_image[:-2] + f' preserveAspectRatio="{aspect_ratio}"/>'
                                elif new_image.endswith('>'):
                                    new_image = new_image[:-1] + f' preserveAspectRatio="{aspect_ratio}">'
                            
                            processed_svg = processed_svg.replace(old_image, new_image)
                            print(f"      ✅ Изображение {dyno_field} заменено!")
                            print(f"      🎯 Применен aspect ratio: {aspect_ratio}")
                            successful_replacements += 1
                        else:
                            print(f"      ❌ Image элемент #{image_id} не найден")
                    else:
                        print(f"      ❌ Use элемент в pattern не найден")
                else:
                    print(f"      ❌ Pattern блок {pattern_id} не найден")
            else:
                print(f"      ❌ Элемент с id {dyno_field} не найден")
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

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# API для загрузки одиночного шаблона
@app.route('/api/upload-single', methods=['POST'])
def upload_single_template():
    try:
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
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'has_dyno_fields': has_dyno,
            'dyno_fields': dyno_fields,
            'message': f'Шаблон "{name}" успешно загружен'
        })
        
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
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_template_id,
            'photo_template_id': photo_template_id,
            'main_dyno_fields': main_dyno_info.get('fields', []) if main_dyno_info else [],
            'photo_dyno_fields': photo_dyno_info.get('fields', []) if photo_dyno_info else [],
            'message': f'Карусель "{name}" успешно загружена'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки карусели: {str(e)}'}), 500

# API роуты
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "API работает"})

@app.route('/api/templates/all-previews')
def get_all_templates():
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, category, template_role, created_at FROM templates ORDER BY created_at DESC')
        templates_data = cursor.fetchall()
        
        conn.close()
        
        templates = []
        for template in templates_data:
            templates.append({
                'id': template[0],
                'name': template[1],
                'category': template[2],
                'template_role': template[3],
                'created_at': template[4],
                'preview_url': f'/api/templates/{template[0]}/preview'
            })
        
        return jsonify({
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения шаблонов: {str(e)}'}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        
        return svg_content, 200, {'Content-Type': 'image/svg+xml'}
        
    except Exception as e:
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
        output_path = os.path.join(OUTPUT_DIR, 'single', output_filename)
        
        # Сохраняем обработанный SVG
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_svg)
        
        return jsonify({
            'success': True,
            'template_name': template_name,
            'output_url': f'/output/single/{output_filename}',
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500

# API для генерации карусели
@app.route('/api/generate/carousel', methods=['POST'])
def generate_carousel():
    try:
        data = request.get_json()
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        replacements = data.get('replacements', {})
        
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
        
        main_name, main_svg_content = main_result
        photo_name, photo_svg_content = photo_result
        
        # Обрабатываем SVG с идеальным сохранением шрифтов
        processed_main_svg = process_svg_font_perfect(main_svg_content, replacements)
        processed_photo_svg = process_svg_font_perfect(photo_svg_content, replacements)
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Сохраняем обработанные SVG
        main_filename = f"carousel_{carousel_id}_main.svg"
        photo_filename = f"carousel_{carousel_id}_photo.svg"
        
        main_path = os.path.join(OUTPUT_DIR, 'carousel', main_filename)
        photo_path = os.path.join(OUTPUT_DIR, 'carousel', photo_filename)
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_name': main_name,
            'photo_template_name': photo_name,
            'main_url': f'/output/carousel/{main_filename}',
            'photo_url': f'/output/carousel/{photo_filename}',
            'replacements_applied': len(replacements)
        })
        
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
        print("🎨 Обрабатываю Main шаблон...")
        processed_main_svg = process_svg_font_perfect(main_svg, replacements)
        
        print("🎨 Обрабатываю Photo шаблон...")
        processed_photo_svg = process_svg_font_perfect(photo_svg, replacements)
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Создаем директорию если не существует
        os.makedirs(os.path.join(OUTPUT_DIR, 'carousel'), exist_ok=True)
        
        # Генерируем имена файлов
        main_filename = f"carousel_{carousel_id}_main.svg"
        photo_filename = f"carousel_{carousel_id}_photo.svg"
        
        main_path = os.path.join(OUTPUT_DIR, 'carousel', main_filename)
        photo_path = os.path.join(OUTPUT_DIR, 'carousel', photo_filename)
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        print(f"🎉 Карусель создана: {carousel_id}")
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_id,
            'photo_template_id': photo_id,
            'main_template_name': main_name,
            'photo_template_name': photo_name,
            'main_url': f'/output/carousel/{main_filename}',
            'photo_url': f'/output/carousel/{photo_filename}',
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        print(f"❌ Ошибка генерации карусели по именам: {str(e)}")
        return jsonify({'error': f'Ошибка генерации карусели: {str(e)}'}), 500

if __name__ == '__main__':
    ensure_db_exists()
    
    # Для локальной разработки
    app.run(host='0.0.0.0', port=5000, debug=True)
