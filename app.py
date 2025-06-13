"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИДЕАЛЬНАЯ ОБРАБОТКА ШРИФТОВ
================================================================

Версия 8.0 - Полная версия с АБСОЛЮТНЫМ сохранением шрифтов Montserrat
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
    
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        if is_image_field(dyno_field):
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ
            image_type = determine_image_type(dyno_field)
            
            print(f"   🖼️ Обрабатываю изображение: {dyno_field}")
            print(f"      📐 Тип изображения: {image_type}")
            
            safe_url = str(replacement).replace('&', '&amp;')
            
            # Ищем элемент с id и извлекаем pattern
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
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
                            
                            # Заменяем URL
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
                    print(f"      ⚠️ Адресный элемент {dyno_field} не найден")
            
            else:
                # Обычная замена для не-адресов
                print(f"   🔤 Обрабатываю текстовое поле: {dyno_field}")
                
                element_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
                
                def replace_text_element(match):
                    full_element = match.group(0)
                    element_content = match.group(1)
                    
                    # Ищем tspan
                    tspan_pattern = r'<tspan[^>]*>([^<]*)</tspan>'
                    tspan_match = re.search(tspan_pattern, element_content)
                    
                    if tspan_match:
                        old_content = tspan_match.group(1)
                        new_content = element_content.replace(old_content, safe_replacement)
                        return full_element.replace(element_content, new_content)
                    else:
                        return full_element.replace(element_content, safe_replacement)
                
                new_svg = re.sub(element_pattern, replace_text_element, processed_svg, flags=re.DOTALL)
                
                if new_svg != processed_svg:
                    processed_svg = new_svg
                    print(f"      ✅ Текстовое поле {dyno_field} заменено!")
                    successful_replacements += 1
                else:
                    print(f"      ⚠️ Текстовое поле {dyno_field} не найдено")
    
    print(f"\n📊 РЕЗУЛЬТАТ: {successful_replacements}/{total_fields} полей заменено")
    print("🎉 ФИНАЛЬНАЯ обработка SVG с круглыми хедшотами завершена!")
    

    return processed_svg

def ensure_db_exists():
    """Создает таблицы базы данных, если они не существуют"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            svg_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/templates', methods=['POST'])
def upload_template():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'svg_content' not in data:
            return jsonify({'error': 'Name and SVG content are required'}), 400
        
        template_id = str(uuid.uuid4())
        name = data['name']
        svg_content = data['svg_content']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO templates (id, name, svg_content) VALUES (?, ?, ?)',
            (template_id, name, svg_content)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'Template uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, created_at FROM templates ORDER BY created_at DESC')
        templates = cursor.fetchall()
        
        conn.close()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template[0],
                'name': template[1],
                'created_at': template[2]
            })
        
        return jsonify({'templates': template_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', (template_id,))
        template = cursor.fetchone()
        
        conn.close()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify({
            'id': template_id,
            'name': template[0],
            'svg_content': template[1]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>/svg', methods=['GET'])
def get_template_svg(template_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        template = cursor.fetchone()
        
        conn.close()
        
        if not template:
            return 'Template not found', 404
        
        return Response(template[0], mimetype='image/svg+xml')
        
    except Exception as e:
        return str(e), 500

@app.route('/api/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Template not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Template deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/all-previews', methods=['GET'])
def get_all_template_previews():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, svg_content FROM templates ORDER BY created_at DESC')
        templates = cursor.fetchall()
        
        conn.close()
        
        previews = []
        for template in templates:
            previews.append({
                'id': template[0],
                'name': template[1],
                'preview_url': f'/api/templates/{template[0]}/svg'
            })
        
        return jsonify({'previews': previews})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        template_name = data.get('template_name')
        replacements = data.get('replacements', {})
        
        if not template_name:
            return jsonify({'error': 'Template name is required'}), 400
        
        # Получаем шаблон из базы данных
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE name = ?', (template_name,))
        template = cursor.fetchone()
        
        conn.close()
        
        if not template:
            return jsonify({'error': f'Template "{template_name}" not found'}), 404
        
        svg_content = template[0]
        
        # Обрабатываем SVG
        processed_svg = process_svg_font_perfect(svg_content, replacements)
        
        # Конвертируем в PNG
        png_data = cairosvg.svg2png(bytestring=processed_svg.encode('utf-8'))
        
        # Кодируем в base64
        png_base64 = base64.b64encode(png_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{png_base64}',
            'svg_content': processed_svg
        })
        
    except Exception as e:
        print(f"Error in generate_image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-carousel', methods=['POST'])
def generate_carousel():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        main_template_name = data.get('main_template_name')
        photo_template_name = data.get('photo_template_name')
        property_images = data.get('property_images', [])
        replacements = data.get('replacements', {})
        
        if not main_template_name or not photo_template_name:
            return jsonify({'error': 'Both main_template_name and photo_template_name are required'}), 400
        
        if not property_images:
            return jsonify({'error': 'At least one property image is required'}), 400
        
        # Получаем шаблоны из базы данных
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE name = ?', (main_template_name,))
        main_template = cursor.fetchone()
        
        cursor.execute('SELECT svg_content FROM templates WHERE name = ?', (photo_template_name,))
        photo_template = cursor.fetchone()
        
        conn.close()
        
        if not main_template:
            return jsonify({'error': f'Main template "{main_template_name}" not found'}), 404
        
        if not photo_template:
            return jsonify({'error': f'Photo template "{photo_template_name}" not found'}), 404
        
        main_svg = main_template[0]
        photo_svg = photo_template[0]
        
        carousel_images = []
        
        # Генерируем главное изображение
        main_processed = process_svg_font_perfect(main_svg, replacements)
        main_png = cairosvg.svg2png(bytestring=main_processed.encode('utf-8'))
        main_base64 = base64.b64encode(main_png).decode('utf-8')
        
        carousel_images.append({
            'type': 'main',
            'image_data': f'data:image/png;base64,{main_base64}'
        })
        
        # Генерируем изображения для каждой фотографии недвижимости
        for i, property_image in enumerate(property_images):
            photo_replacements = replacements.copy()
            photo_replacements['dyno.propertyimage'] = property_image
            
            photo_processed = process_svg_font_perfect(photo_svg, photo_replacements)
            photo_png = cairosvg.svg2png(bytestring=photo_processed.encode('utf-8'))
            photo_base64 = base64.b64encode(photo_png).decode('utf-8')
            
            carousel_images.append({
                'type': 'photo',
                'index': i,
                'image_data': f'data:image/png;base64,{photo_base64}'
            })
        
        return jsonify({
            'success': True,
            'carousel_images': carousel_images,
            'total_images': len(carousel_images)
        })
        
    except Exception as e:
        print(f"Error in generate_carousel: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ensure_db_exists()
    app.run(host='0.0.0.0', port=5000, debug=True)

