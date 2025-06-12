"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИДЕАЛЬНАЯ ОБРАБОТКА ШРИФТОВ
================================================================

Версия 8.0 - Полная версия с АБСОЛЮТНЫМ сохранением шрифтов Montserrat
"""

import os
import sqlite3
import uuid
import time
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
import subprocess
from PIL import Image
import cairosvg

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

def convert_svg_to_png(svg_content, output_path, width=1200, height=800):
    """
    Конвертирует SVG в PNG с высоким качеством и сохранением оригинальных шрифтов
    """
    try:
        print(f"🖼️ Конвертирую SVG в PNG с сохранением оригинальных шрифтов: {output_path}")
        
        # Убедимся, что SVG не содержит принудительной замены шрифтов
        svg_content = svg_content.replace('font-family="Montserrat"', 'font-family="Montserrat, sans-serif"')
        svg_content = svg_content.replace('font-family="Inter"', 'font-family="Inter, sans-serif"')
        
        # Конвертация через cairosvg с сохранением оригинальных шрифтов
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

def save_png_only(svg_content, base_path, width=1200, height=800):
    """
    Сохраняет только PNG файл из SVG
    Возвращает путь к PNG файлу
    """
    png_path = f"{base_path}.png"
    
    try:
        print(f"🖼️ Конвертирую SVG в PNG: {png_path}")
        
        # Конвертация через cairosvg
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=width,
            output_height=height,
            dpi=300  # Высокое качество
        )
        
        # Сохраняем PNG файл
        with open(png_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ PNG файл создан: {png_path}")
        
        return {
            'png_path': png_path,
            'png_url': png_path.replace('output/', '/output/')
        }
        
    except Exception as e:
        print(f"❌ Ошибка конвертации SVG в PNG: {e}")
        # Fallback - сохраняем SVG если PNG не получился
        svg_path = f"{base_path}.svg"
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return {
            'png_path': svg_path,  # Возвращаем SVG как fallback
            'png_url': svg_path.replace('output/', '/output/')
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

def process_svg_font_perfect(svg_content, replacements):
    """
    ИСПРАВЛЕННАЯ функция обработки SVG:
    1. Правильная замена без дублирования
    2. Автоматический перенос длинных адресов
    3. Сохранение оригинальных шрифтов БЕЗ ЗАМЕНЫ
    """
    print("🎨 ЗАПУСК ИСПРАВЛЕННОЙ ОБРАБОТКИ SVG С СОХРАНЕНИЕМ ОРИГИНАЛЬНЫХ ШРИФТОВ")
    
    # Сохраняем оригинальные шрифты - НЕ ЗАМЕНЯЕМ ИХ
    processed_svg = svg_content
    
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Безопасное экранирование
        safe_replacement = safe_escape_for_svg(str(replacement))
        
        # Специальная обработка для адреса - добавляем перенос строки
        if 'address' in dyno_field.lower():
            # Разбиваем длинный адрес на строки
            address_parts = str(replacement).split(', ')
            if len(address_parts) >= 3:
                # Первая строка: номер дома + улица
                line1 = address_parts[0]
                # Вторая строка: город + штат + индекс
                line2 = ', '.join(address_parts[1:])
                
                # Создаем многострочный текст для SVG
                safe_replacement = f'''<tspan x="0" dy="0">{safe_escape_for_svg(line1)}</tspan><tspan x="0" dy="1.2em">{safe_escape_for_svg(line2)}</tspan>'''
                print(f"   📍 Адрес разбит на строки: {line1} | {line2}")
            else:
                safe_replacement = safe_escape_for_svg(str(replacement))
        
        if 'image' in dyno_field.lower() or 'headshot' in dyno_field.lower() or 'logo' in dyno_field.lower():
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ
            print(f"🖼️ Обрабатываю изображение: {dyno_field}")
            
            safe_url = str(replacement).replace('&', '&amp;')
            
            if 'propertyimage' in dyno_field.lower():
                aspect_ratio = 'xMidYMid slice'
            elif 'logo' in dyno_field.lower():
                aspect_ratio = 'xMidYMid meet'
            elif 'headshot' in dyno_field.lower() or 'agent' in dyno_field.lower():
                # СПЕЦИАЛЬНАЯ обработка для headshot - НЕ обрезаем лица
                aspect_ratio = 'xMidYMid meet'  # Выравнивание по центру + полное изображение
            else:
                aspect_ratio = 'xMidYMid meet'
            
            # ПОЛНОЕ РЕШЕНИЕ ДЛЯ HEADSHOT - ГАРАНТИРОВАННЫЙ ПОЛНЫЙ КРУГ
            if 'headshot' in dyno_field.lower() or 'agent' in dyno_field.lower():
                print(f"🔄 ПОЛНОЕ РЕШЕНИЕ для headshot: {dyno_field}")
                
                # Находим элемент с clipPath для headshot
                clip_pattern = f'<g[^>]*clip-path="url\\(#([^)]+)\\)"[^>]*>\\s*<rect[^>]*id="{re.escape(dyno_field)}"[^>]*>'
                clip_match = re.search(clip_pattern, processed_svg)
                
                if clip_match:
                    clip_id = clip_match.group(1)
                    print(f"   ✅ Найден clipPath: {clip_id} для headshot")
                    
                    # Находим определение clipPath
                    clip_def_pattern = f'<clipPath[^>]*id="{re.escape(clip_id)}"[^>]*>\\s*<rect[^>]*rx="([^"]+)"[^>]*>'
                    clip_def_match = re.search(clip_def_pattern, processed_svg)
                    
                    if clip_def_match:
                        rx_value = clip_def_match.group(1)
                        print(f"   ✅ Найдено определение clipPath с rx={rx_value} (круглая маска)")
                        
                        # Находим pattern для изображения
                        element_pattern = f'<rect[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
                        match = re.search(element_pattern, processed_svg)
                        
                        if match:
                            pattern_id = match.group(1)
                            
                            # Находим pattern определение
                            pattern_def = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>[^<]*<use[^>]*xlink:href="#([^"]+)"[^>]*>'
                            pattern_match = re.search(pattern_def, processed_svg)
                            
                            if pattern_match:
                                image_id = pattern_match.group(1)
                                
                                # Заменяем изображение в defs
                                image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                                def replace_specific_image(img_match):
                                    result = img_match.group(0)
                                    result = re.sub(r'href="[^"]*"', f'href="{safe_url}"', result)
                                    result = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', result)
                                    result = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="xMidYMid meet"', result)
                                    
                                    if 'preserveAspectRatio=' not in result:
                                        result = result.replace('/>', f' preserveAspectRatio="xMidYMid meet"/>')
                                    
                                    return result
                                
                                processed_svg = re.sub(image_pattern, replace_specific_image, processed_svg, count=1)
                                print(f"   ✅ Заменено изображение headshot {image_id} с настройкой xMidYMid meet")
                                
                                # Пропускаем стандартную обработку
                                continue
                
                # Запасной вариант - если не нашли clipPath или pattern
                print(f"   ⚠️ Используем запасной вариант для headshot")
                
                # Находим pattern для изображения
                element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
                match = re.search(element_pattern, processed_svg)
                
                if match:
                    pattern_id = match.group(1)
                    image_id = pattern_id.replace("pattern", "image")
                    
                    # Заменяем изображение в pattern
                    image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                    def replace_specific_image(img_match):
                        result = img_match.group(0)
                        result = re.sub(r'href="[^"]*"', f'href="{safe_url}"', result)
                        result = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', result)
                        result = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="xMidYMid meet"', result)
                        
                        if 'preserveAspectRatio=' not in result:
                            result = result.replace('/>', f' preserveAspectRatio="xMidYMid meet"/>')
                        
                        return result
                    
                    processed_svg = re.sub(image_pattern, replace_specific_image, processed_svg, count=1)
                    print(f"   ✅ Заменено изображение headshot {image_id} с настройкой xMidYMid meet")
                    
                    # Пропускаем стандартную обработку
                    continue
                else:
                    print(f"   ⚠️ Не найден pattern для headshot, пробуем стандартную обработку")
            
            # СТАНДАРТНАЯ ОБРАБОТКА ДЛЯ ДРУГИХ ИЗОБРАЖЕНИЙ
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            if match:
                pattern_id = match.group(1)
                image_id = pattern_id.replace("pattern", "image")
                
                image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                def replace_specific_image(img_match):
                    result = img_match.group(0)
                    result = re.sub(r'href="[^"]*"', f'href="{safe_url}"', result)
                    result = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', result)
                    result = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', result)
                    
                    if 'preserveAspectRatio=' not in result:
                        result = result.replace('/>', f' preserveAspectRatio="{aspect_ratio}"/>')
                    
                    return result
                
                processed_svg = re.sub(image_pattern, replace_specific_image, processed_svg, count=1)
                print(f"   ✅ Заменено изображение {image_id}")
        
        else:
            # ИСПРАВЛЕННАЯ ОБРАБОТКА ТЕКСТА - ищем ТОЧНЫЕ совпадения
            print(f"📝 Обрабатываю текст: {dyno_field}")
            
            # Ищем ТОЧНОЕ совпадение dyno поля в тексте элементов
            text_element_pattern = f'<text[^>]*>([^<]*{re.escape(dyno_field)}[^<]*)</text>'
            matches = list(re.finditer(text_element_pattern, processed_svg))
            
            if matches:
                # Заменяем ТОЛЬКО ПЕРВОЕ совпадение
                match = matches[0]
                old_text = match.group(1)
                
                if 'address' in dyno_field.lower():
                    # Для адреса используем tspan элементы
                    new_text = safe_replacement
                else:
                    # Для обычного текста - простая замена
                    new_text = old_text.replace(dyno_field, safe_replacement)
                
                # Заменяем только этот конкретный элемент
                old_element = match.group(0)
                new_element = old_element.replace(old_text, new_text)
                
                processed_svg = processed_svg.replace(old_element, new_element, 1)
                print(f"   ✅ Заменен текст: {old_text} → {new_text[:50]}...")
            
            else:
                # Fallback - ищем по старым паттернам
                patterns = [
                    f'>{re.escape(dyno_field)}<',
                    f'{{{{\\s*{re.escape(dyno_field)}\\s*}}}}',
                    f'{{\\s*{re.escape(dyno_field)}\\s*}}',
                ]
                
                replaced = False
                for pattern in patterns:
                    if re.search(pattern, processed_svg):
                        if pattern.startswith('>'):
                            processed_svg = re.sub(pattern, f'>{safe_replacement}<', processed_svg, count=1)
                        else:
                            processed_svg = re.sub(pattern, safe_replacement, processed_svg, count=1)
                        
                        print(f"   ✅ Заменен текст по fallback паттерну: {pattern}")
                        replaced = True
                        break
                
                if not replaced:
                    print(f"   ⚠️ Текстовое поле {dyno_field} не найдено")
    
    print("✅ Сохраняем оригинальные шрифты шаблона")
    print("🎉 ИСПРАВЛЕННАЯ обработка SVG завершена!")
    return processed_svg        
                print(f"   ✅ Содержимое заменено!")
                return full_element.replace(element_content, new_content)
            
            # Применяем замену
            new_svg = re.sub(element_pattern, replace_element_content, processed_svg, flags=re.DOTALL)
            
            if new_svg != processed_svg:
                processed_svg = new_svg
                print(f"   ✅ Поле {dyno_field} успешно заменено!")
            else:
                print(f"   ⚠️ Элемент с id='{dyno_field}' не найден")
    
    # УБИРАЕМ принудительную замену шрифтов - оставляем оригинальные!
    print("🔤 СОХРАНЯЮ оригинальные шрифты (НЕ заменяю на Montserrat)")
    
    # УБИРАЕМ добавление Google Fonts импорта - оставляем как есть
    print("📥 НЕ добавляю Google Fonts импорт - сохраняю оригинальные шрифты")
    
    print("🎉 ИСПРАВЛЕННАЯ обработка SVG завершена!")
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
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не найден'}), 400
        
        file = request.files['file']
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
        
        # Генерируем PNG превью для шаблона
        preview_url = generate_png_preview(svg_content, template_id)
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'has_dyno_fields': has_dyno,
            'dyno_fields': dyno_fields,
            'preview_url': preview_url,
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
        
        # Генерируем PNG превью для обоих шаблонов
        main_preview_url = generate_png_preview(main_svg, main_template_id)
        photo_preview_url = generate_png_preview(photo_svg, photo_template_id)
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'main_template_id': main_template_id,
            'photo_template_id': photo_template_id,
            'main_preview_url': main_preview_url,
            'photo_preview_url': photo_preview_url,
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
        
        cursor.execute('SELECT id, name, category, template_role, svg_content, created_at FROM templates ORDER BY created_at DESC')
        templates_data = cursor.fetchall()
        
        conn.close()
        
        templates = []
        for template in templates_data:
            template_id = template[0]
            
            # Проверяем, существует ли PNG превью
            preview_path = os.path.join(OUTPUT_DIR, 'previews', f"{template_id}_preview.png")
            
            # Если превью не существует, генерируем его
            if not os.path.exists(preview_path):
                svg_content = template[4]
                generate_png_preview(svg_content, template_id)
            
            # Формируем URL для превью
            preview_url = f'/output/previews/{template_id}_preview.png'
            
            templates.append({
                'id': template_id,
                'name': template[1],
                'category': template[2],
                'template_role': template[3],
                'created_at': template[5],
                'preview_url': preview_url
            })
        
        return jsonify({
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения шаблонов: {str(e)}'}), 500

# Функция для конвертации SVG в PNG превью
def generate_png_preview(svg_content, template_id):
    try:
        # Создаем директорию для превью, если её нет
        preview_dir = os.path.join(OUTPUT_DIR, 'previews')
        os.makedirs(preview_dir, exist_ok=True)
        
        # Путь для сохранения PNG превью
        png_path = os.path.join(preview_dir, f"{template_id}_preview.png")
        
        # Конвертируем SVG в PNG с помощью cairosvg
        cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=png_path, output_width=400)
        
        print(f"✅ Сгенерировано PNG превью для шаблона {template_id}")
        return f"/output/previews/{template_id}_preview.png"
    except Exception as e:
        print(f"❌ Ошибка генерации PNG превью: {str(e)}")
        return None

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем, существует ли PNG превью
        preview_path = os.path.join(OUTPUT_DIR, 'previews', f"{template_id}_preview.png")
        
        if not os.path.exists(preview_path):
            # Если превью нет, получаем SVG и генерируем его
            cursor.execute('SELECT svg_content FROM templates WHERE id = ?', [template_id])
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return jsonify({'error': 'Шаблон не найден'}), 404
            
            svg_content = result[0]
            
            # Генерируем PNG превью
            generate_png_preview(svg_content, template_id)
        
        conn.close()
        
        # Возвращаем URL к PNG превью
        return jsonify({
            'preview_url': f'/output/previews/{template_id}_preview.png'
        })
        
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
        
        # ИСПРАВЛЕННАЯ обработка SVG с разными изображениями для слайдов
        print("🎨 Обрабатываю Main слайд с ПОЛНЫМИ данными...")
        main_replacements = replacements.copy()
        processed_main_svg = process_svg_font_perfect(main_svg_content, main_replacements)
        
        print("🎨 Обрабатываю Photo слайд - теперь БЕЗ МАППИНГА!")
        print("   ✅ Photo шаблон теперь использует dyno.propertyimage2 напрямую")
        # Теперь НЕ НУЖНО маппинга - photo шаблон сам ищет dyno.propertyimage2
        photo_replacements = replacements.copy()
        processed_photo_svg = process_svg_font_perfect(photo_svg_content, photo_replacements)
        
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
        
        # ИСПРАВЛЕННАЯ обработка SVG с разными изображениями для слайдов
        print("🎨 Обрабатываю Main слайд с ПОЛНЫМИ данными...")
        main_replacements = replacements.copy()
        processed_main_svg = process_svg_font_perfect(main_svg, main_replacements)
        
        print("🎨 Обрабатываю Photo слайд - теперь БЕЗ МАППИНГА!")
        print("   ✅ Photo шаблон теперь использует dyno.propertyimage2 напрямую")
        # Теперь НЕ НУЖНО маппинга - photo шаблон сам ищет dyno.propertyimage2
        photo_replacements = replacements.copy()
        processed_photo_svg = process_svg_font_perfect(photo_svg, photo_replacements)
        
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

