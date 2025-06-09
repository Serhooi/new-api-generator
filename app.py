#!/usr/bin/env python3
"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИСПРАВЛЕННАЯ ОБРАБОТКА PROPERTY IMAGE
===========================================================================

Версия 7.0 - Полная версия с исправленной заменой property image
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
    # Ищем dyno поля в id атрибутах
    id_pattern = r'id="(dyno\.[^"]*)"'
    id_matches = re.findall(id_pattern, svg_content)
    
    # Ищем dyno поля в тексте
    text_patterns = [
        r'\{\{(dyno\.[^}]+)\}\}',
        r'\{(dyno\.[^}]+)\}'
    ]
    
    text_matches = []
    for pattern in text_patterns:
        text_matches.extend(re.findall(pattern, svg_content))
    
    # Объединяем все найденные поля
    all_fields = list(set(id_matches + text_matches))
    
    # Определяем типы полей
    field_types = {}
    for field in all_fields:
        if any(img_keyword in field.lower() for img_keyword in ['image', 'photo', 'picture', 'logo', 'headshot']):
            field_types[field] = 'image'
        else:
            field_types[field] = 'text'
    
    return {
        'fields': all_fields,
        'types': field_types,
        'count': len(all_fields),
        'has_dyno': len(all_fields) > 0
    }

def process_svg_ultimate_fixed(svg_content, replacements):
    """
    ОКОНЧАТЕЛЬНО ИСПРАВЛЕННАЯ функция обработки SVG:
    1. Заменяет ВСЕ pattern для property image (pattern0_294_4 И pattern0_332_4)
    2. ПОЛНОСТЬЮ сохраняет шрифты при замене текста
    """
    processed_svg = svg_content
    
    print("🔧 Начинаю ОКОНЧАТЕЛЬНУЮ обработку SVG...")
    
    for field, value in replacements.items():
        if field.startswith('dyno.'):
            # Безопасное экранирование значения
            safe_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Определяем тип поля
            is_image = any(img_keyword in field.lower() for img_keyword in ['image', 'photo', 'picture', 'logo', 'headshot'])
            
            if is_image:
                print(f"🖼️ Обрабатываю изображение: {field}")
                
                # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ PROPERTY IMAGE
                if 'propertyimage' in field.lower():
                    print("   🎯 Это property image - заменяю ВСЕ возможные patterns")
                    
                    # Список всех возможных pattern ID для property image
                    property_patterns = ['pattern0_294_4', 'pattern0_332_4', 'pattern0_294_5', 'pattern0_332_5']
                    
                    for pattern_id in property_patterns:
                        pattern_replacement = f'''<pattern id="{pattern_id}" patternContentUnits="objectBoundingBox" width="1" height="1">
<image href="{safe_value}" x="0" y="0" width="1" height="1" preserveAspectRatio="xMidYMid slice"/>
</pattern>'''
                        
                        # Ищем и заменяем этот pattern если он существует
                        old_pattern_regex = f'<pattern id="{pattern_id}"[^>]*>.*?</pattern>'
                        if re.search(old_pattern_regex, processed_svg, flags=re.DOTALL):
                            processed_svg = re.sub(old_pattern_regex, pattern_replacement, processed_svg, flags=re.DOTALL)
                            print(f"   ✅ Property image заменен в {pattern_id}!")
                
                # ОБРАБОТКА ДРУГИХ ИЗОБРАЖЕНИЙ (logo, headshot)
                else:
                    # Ищем rect с этим id и получаем pattern id
                    rect_pattern = f'<rect[^>]*id="{field}"[^>]*fill="url\\(#([^)]+)\\)"'
                    rect_match = re.search(rect_pattern, processed_svg)
                    
                    if rect_match:
                        pattern_id = rect_match.group(1)
                        print(f"   Найден pattern: {pattern_id}")
                        
                        # Заменяем pattern
                        pattern_replacement = f'''<pattern id="{pattern_id}" patternContentUnits="objectBoundingBox" width="1" height="1">
<image href="{safe_value}" x="0" y="0" width="1" height="1" preserveAspectRatio="xMidYMid slice"/>
</pattern>'''
                        
                        # Ищем и заменяем старый pattern
                        old_pattern_regex = f'<pattern id="{pattern_id}"[^>]*>.*?</pattern>'
                        processed_svg = re.sub(old_pattern_regex, pattern_replacement, processed_svg, flags=re.DOTALL)
                        print(f"   ✅ Заменен pattern {pattern_id}")
                    else:
                        print(f"   ⚠️ Pattern не найден для {field}")
                
            else:
                # ДЛЯ ТЕКСТА - МАКСИМАЛЬНО ОСТОРОЖНАЯ замена с ПОЛНЫМ сохранением шрифтов
                print(f"📝 Обрабатываю текст: {field}")
                
                # Ищем text элемент с нужным id
                text_pattern = f'<text[^>]*id="{field}"[^>]*>'
                text_match = re.search(text_pattern, processed_svg)
                
                if text_match:
                    text_element_start = text_match.end()
                    
                    # Ищем первый tspan внутри этого text элемента
                    tspan_pattern = r'<tspan[^>]*>([^<]*)</tspan>'
                    tspan_match = re.search(tspan_pattern, processed_svg[text_element_start:])
                    
                    if tspan_match:
                        # Вычисляем позицию в полном SVG
                        tspan_content_start = text_element_start + tspan_match.start(1)
                        tspan_content_end = text_element_start + tspan_match.end(1)
                        
                        # Заменяем ТОЛЬКО содержимое tspan, НЕ ТРОГАЯ атрибуты
                        old_content = processed_svg[tspan_content_start:tspan_content_end]
                        processed_svg = processed_svg[:tspan_content_start] + safe_value + processed_svg[tspan_content_end:]
                        print(f"   ✅ Заменено: '{old_content}' → '{safe_value}' (ВСЕ атрибуты сохранены)")
                    else:
                        print(f"   ⚠️ Не найден tspan в text элементе для {field}")
                else:
                    print(f"   ⚠️ Не найден text элемент с id {field}")
    
    print("✅ ОКОНЧАТЕЛЬНАЯ обработка SVG завершена!")
    return processed_svg

def ensure_db_exists():
    """
    Инициализация базы данных
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                template_role TEXT DEFAULT 'main',
                svg_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_dyno_fields BOOLEAN DEFAULT FALSE,
                dyno_fields_info TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousels (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                main_template_id TEXT,
                photo_template_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (main_template_id) REFERENCES templates (id),
                FOREIGN KEY (photo_template_id) REFERENCES templates (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Веб-интерфейс
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    try:
        ensure_db_exists()
        
        # Получаем шаблоны из базы данных
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, template_role, has_dyno_fields, dyno_fields_info, created_at
            FROM templates 
            ORDER BY created_at DESC
        ''')
        
        templates = []
        for row in cursor.fetchall():
            templates.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'template_role': row[3],
                'has_dyno_fields': bool(row[4]),
                'dyno_fields_info': row[5],
                'created_at': row[6],
                'preview_url': f'/api/templates/{row[0]}/preview'
            })
        
        conn.close()
        
        # Передаем шаблоны в HTML шаблон
        return render_template('templates.html', templates=templates)
        
    except Exception as e:
        return f"Ошибка загрузки шаблонов: {e}", 500

@app.route('/upload')
def upload_page():
    try:
        ensure_db_exists()
        return render_template('upload.html')
    except Exception as e:
        return f"Ошибка: {e}", 500

# Роуты загрузки
@app.route('/upload-single', methods=['POST'])
def upload_single_template():
    try:
        ensure_db_exists()
        
        if 'template' not in request.files:
            return jsonify({'error': 'Файл шаблона не найден'}), 400
        
        file = request.files['template']
        name = request.form.get('name', 'Unnamed Template')
        category = request.form.get('category', 'other')
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое SVG
        svg_content = file.read().decode('utf-8')
        
        # Проверяем dyno поля
        has_dyno = has_dyno_fields_simple(svg_content)
        dyno_info = extract_dyno_fields_simple(svg_content) if has_dyno else None
        
        # Сохраняем в базу данных
        template_id = str(uuid.uuid4())
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [template_id, name, category, 'main', svg_content, has_dyno, str(dyno_info) if dyno_info else None])
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'has_dyno': has_dyno,
            'dyno_fields': dyno_info.get('fields', []) if dyno_info else [],
            'message': f'Шаблон "{name}" успешно загружен'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/upload-carousel', methods=['POST'])
def upload_carousel_templates():
    try:
        ensure_db_exists()
        
        if 'main_template' not in request.files or 'photo_template' not in request.files:
            return jsonify({'error': 'Необходимы оба файла: main_template и photo_template'}), 400
        
        main_file = request.files['main_template']
        photo_file = request.files['photo_template']
        name = request.form.get('name', 'Unnamed Carousel')
        category = request.form.get('category', 'other')
        
        if main_file.filename == '' or photo_file.filename == '':
            return jsonify({'error': 'Оба файла должны быть выбраны'}), 400
        
        if not (allowed_file(main_file.filename) and allowed_file(photo_file.filename)):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое SVG файлов
        main_svg_content = main_file.read().decode('utf-8')
        photo_svg_content = photo_file.read().decode('utf-8')
        
        # Проверяем dyno поля в обоих шаблонах
        main_has_dyno = has_dyno_fields_simple(main_svg_content)
        photo_has_dyno = has_dyno_fields_simple(photo_svg_content)
        
        main_dyno_info = extract_dyno_fields_simple(main_svg_content) if main_has_dyno else None
        photo_dyno_info = extract_dyno_fields_simple(photo_svg_content) if photo_has_dyno else None
        
        # Сохраняем шаблоны в базу данных
        main_template_id = str(uuid.uuid4())
        photo_template_id = str(uuid.uuid4())
        carousel_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Сохраняем main шаблон
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [main_template_id, f"{name} - Main", category, 'main', main_svg_content, main_has_dyno, str(main_dyno_info) if main_dyno_info else None])
        
        # Сохраняем photo шаблон
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [photo_template_id, f"{name} - Photo", category, 'photo', photo_svg_content, photo_has_dyno, str(photo_dyno_info) if photo_dyno_info else None])
        
        # Создаем карусель
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            svg_content = result[0]
            # Кодируем SVG в base64 для передачи
            svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            
            return jsonify({
                'preview_base64': f'data:image/svg+xml;base64,{svg_base64}'
            })
        else:
            return jsonify({'error': 'Шаблон не найден'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>/delete', methods=['DELETE'])
def delete_template(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем существует ли шаблон
        cursor.execute('SELECT name FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name = result[0]
        
        # Удаляем шаблон
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        
        # Удаляем связанные карусели
        cursor.execute('DELETE FROM carousels WHERE main_template_id = ? OR photo_template_id = ?', (template_id, template_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Шаблон "{template_name}" успешно удален'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка удаления: {str(e)}'}), 500

@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    try:
        data = request.get_json()
        
        template_id = data.get('template_id')
        replacements = data.get('replacements', {})
        
        if not template_id:
            return jsonify({'error': 'Требуется template_id'}), 400
        
        # Получаем шаблон из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        template_name, svg_content = result
        
        # Обрабатываем SVG с ИСПРАВЛЕННОЙ функцией
        processed_svg = process_svg_ultimate_fixed(svg_content, replacements)
        
        # Сохраняем результат
        output_filename = f'single_{template_id}_{uuid.uuid4().hex[:8]}.svg'
        output_path = f'{OUTPUT_DIR}/single/{output_filename}'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_svg)
        
        return jsonify({
            'success': True,
            'template_name': template_name,
            'image_url': f'/output/single/{output_filename}',
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    try:
        data = request.get_json()
        
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        replacements = data.get('replacements', {})
        
        if not main_template_id or not photo_template_id:
            return jsonify({'error': 'Требуются main_template_id и photo_template_id'}), 400
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Создаем директорию для вывода
        os.makedirs(f'{OUTPUT_DIR}/carousel', exist_ok=True)
        
        # Получаем шаблоны из базы данных
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Main template
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', (main_template_id,))
        main_result = cursor.fetchone()
        
        # Photo template
        cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', (photo_template_id,))
        photo_result = cursor.fetchone()
        
        conn.close()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Один или оба шаблона не найдены'}), 404
        
        main_name, main_svg = main_result
        photo_name, photo_svg = photo_result
        
        # Обрабатываем шаблоны с ИСПРАВЛЕННОЙ функцией
        print("🔧 Обрабатываю main template...")
        pro        processed_main = process_svg_ultimate_fixed(main_svg, replacements)
        
        # Обрабатываем photo template
        processed_photo = process_svg_ultimate_fixed(photo_svg, replacements)
        
        # Сохраняем результаты
        main_filename = f'carousel_{carousel_id}_main.svg'
        photo_filename = f'carousel_{carousel_id}_photo.svg'
        
        main_path = f'{OUTPUT_DIR}/carousel/{main_filename}'
        photo_path = f'{OUTPUT_DIR}/carousel/{photo_filename}'
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(processed_main)
        
        with open(photo_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo)
        
        # Формируем ответ
        result = {
            'carousel_id': carousel_id,
            'replacements_applied': len(replacements),
            'images': [
                {
                    'type': 'main',
                    'template_name': main_name,
                    'url': f'/output/carousel/{main_filename}',
                    'format': 'svg'
                },
                {
                    'type': 'photo',
                    'template_name': photo_name,
                    'url': f'/output/carousel/{photo_filename}',
                    'format': 'svg'
                }
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousels')
def get_all_carousels():
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.name, c.created_at, 
                   mt.name as main_template_name, pt.name as photo_template_name
            FROM carousels c
            LEFT JOIN templates mt ON c.main_template_id = mt.id
            LEFT JOIN templates pt ON c.photo_template_id = pt.id
            ORDER BY c.created_at DESC
        ''')
        
        carousels = []
        for row in cursor.fetchall():
            carousels.append({
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'main_template_name': row[3],
                'photo_template_name': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'carousels': carousels,
            'total': len(carousels)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    ensure_db_exists()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

