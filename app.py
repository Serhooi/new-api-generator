#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ ВЕРСИЯ API С ПРАВИЛЬНОЙ ОБРАБОТКОЙ ИЗОБРАЖЕНИЙ
==========================================================

Версия 6.0 - Исправлена замена изображений и сохранение шрифтов
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

def process_svg_advanced(svg_content, replacements):
    """
    ИСПРАВЛЕННАЯ функция обработки SVG с правильной заменой изображений и сохранением шрифтов
    """
    processed_svg = svg_content
    
    for field, value in replacements.items():
        if field.startswith('dyno.'):
            # Безопасное экранирование значения
            safe_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Определяем тип поля
            is_image = any(img_keyword in field.lower() for img_keyword in ['image', 'photo', 'picture', 'logo', 'headshot'])
            
            if is_image:
                # ДЛЯ ИЗОБРАЖЕНИЙ - заменяем в pattern definitions
                print(f"🖼️ Обрабатываю изображение: {field}")
                
                # Ищем rect с этим id и получаем pattern id
                rect_pattern = f'<rect[^>]*id="{field}"[^>]*fill="url\\(#([^)]+)\\)"'
                rect_match = re.search(rect_pattern, processed_svg)
                
                if rect_match:
                    pattern_id = rect_match.group(1)
                    print(f"   Найден pattern: {pattern_id}")
                    
                    # Заменяем pattern definition на простое изображение
                    pattern_replacement = f'''<pattern id="{pattern_id}" patternContentUnits="objectBoundingBox" width="1" height="1">
<image href="{safe_value}" width="1" height="1" preserveAspectRatio="xMidYMid slice"/>
</pattern>'''
                    
                    # Ищем и заменяем старый pattern
                    old_pattern = f'<pattern id="{pattern_id}"[^>]*>.*?</pattern>'
                    processed_svg = re.sub(old_pattern, pattern_replacement, processed_svg, flags=re.DOTALL)
                    print(f"   ✅ Заменен pattern {pattern_id}")
                
            else:
                # ДЛЯ ТЕКСТА - простая замена содержимого
                print(f"📝 Обрабатываю текст: {field}")
                
                # Ищем text элемент с нужным id
                text_start = processed_svg.find(f'id="{field}"')
                if text_start != -1:
                    # Ищем следующий <tspan> после этого id
                    tspan_start = processed_svg.find('<tspan', text_start)
                    if tspan_start != -1:
                        # Ищем закрывающий >
                        content_start = processed_svg.find('>', tspan_start) + 1
                        # Ищем закрывающий </tspan>
                        content_end = processed_svg.find('</tspan>', content_start)
                        
                        if content_start > 0 and content_end != -1:
                            # Заменяем содержимое
                            old_content = processed_svg[content_start:content_end]
                            processed_svg = processed_svg[:content_start] + safe_value + processed_svg[content_end:]
                            print(f"   ✅ Заменено: '{old_content}' → '{safe_value}'")
    
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
        
        # Проверяем есть ли шаблоны
        cursor.execute('SELECT COUNT(*) FROM templates')
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📦 Добавляю начальные шаблоны...")
            
            # Простые тестовые шаблоны
            initial_templates = [
                {
                    'id': 'simple-main-template',
                    'name': 'Simple Main Template',
                    'category': 'open-house',
                    'template_role': 'main',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#4A5568"/>
                        <text x="540" y="920" text-anchor="middle" fill="white" font-family="Arial" font-size="48" id="dyno.price">$2,500,000</text>
                        <text x="540" y="980" text-anchor="middle" fill="#A0AEC0" font-family="Arial" font-size="24" id="dyno.propertyaddress">123 Main Street</text>
                        <text x="540" y="1150" text-anchor="middle" fill="#A0AEC0" font-family="Arial" font-size="28" id="dyno.name">Agent Name</text>
                        <text x="540" y="1190" text-anchor="middle" fill="#A0AEC0" font-family="Arial" font-size="18" id="dyno.phone">(555) 123-4567</text>
                    </svg>'''
                },
                {
                    'id': 'simple-photo-template',
                    'name': 'Simple Photo Template',
                    'category': 'open-house',
                    'template_role': 'photo',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#2D3748"/>
                        <rect x="40" y="40" width="1000" height="1000" fill="#E2E8F0"/>
                        <text x="540" y="1150" text-anchor="middle" fill="white" font-family="Arial" font-size="48" id="dyno.price">$2,500,000</text>
                        <text x="540" y="1200" text-anchor="middle" fill="#A0AEC0" font-family="Arial" font-size="24" id="dyno.propertyaddress">123 Main Street</text>
                    </svg>'''
                }
            ]
            
            for template in initial_templates:
                # Проверяем dyno поля
                has_dyno = has_dyno_fields_simple(template['svg_content'])
                dyno_info = extract_dyno_fields_simple(template['svg_content']) if has_dyno else None
                
                cursor.execute('''
                    INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [
                    template['id'],
                    template['name'],
                    template['category'],
                    template['template_role'],
                    template['svg_content'],
                    has_dyno,
                    str(dyno_info) if dyno_info else None
                ])
            
            print(f"✅ Добавлено {len(initial_templates)} начальных шаблонов")
        
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
            'main_has_dyno': main_has_dyno,
            'photo_has_dyno': photo_has_dyno,
            'main_dyno_fields': main_dyno_info.get('fields', []) if main_dyno_info else [],
            'photo_dyno_fields': photo_dyno_info.get('fields', []) if photo_dyno_info else [],
            'message': f'Карусель "{name}" успешно загружена'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки карусели: {str(e)}'}), 500

# API endpoints
@app.route('/api/templates/all-previews')
def get_all_templates():
    try:
        ensure_db_exists()
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
        return jsonify({'templates': templates})
        
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
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        conn.close()
        
        # Простое превью - возвращаем SVG как base64
        svg_base64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        
        return jsonify({
            'preview_base64': f'data:image/svg+xml;base64,{svg_base64}',
            'template_id': template_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    try:
        ensure_db_exists()
        data = request.get_json()
        
        if not data or 'template_id' not in data:
            return jsonify({'error': 'template_id обязателен'}), 400
        
        template_id = data['template_id']
        replacements = data.get('replacements', {})
        
        # Получаем шаблон из базы данных
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content, name FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content, template_name = result
        conn.close()
        
        # Обрабатываем SVG с заменами (ИСПРАВЛЕННАЯ ФУНКЦИЯ)
        processed_svg = process_svg_advanced(svg_content, replacements)
        
        # Генерируем файл
        output_filename = f"single_{template_id}_{uuid.uuid4().hex[:8]}.svg"
        output_path = os.path.join(OUTPUT_DIR, 'single', output_filename)
        
        # Сохраняем как SVG
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_svg)
        
        # Возвращаем публичный URL
        public_url = f"{request.host_url}output/single/{output_filename}"
        
        return jsonify({
            'success': True,
            'image_url': public_url,
            'template_id': template_id,
            'template_name': template_name,
            'replacements_applied': len(replacements),
            'format': 'svg'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    try:
        ensure_db_exists()
        data = request.get_json()
        
        if not data or 'main_template_id' not in data or 'photo_template_id' not in data:
            return jsonify({'error': 'main_template_id и photo_template_id обязательны'}), 400
        
        main_template_id = data['main_template_id']
        photo_template_id = data['photo_template_id']
        replacements = data.get('replacements', {})
        
        # Получаем шаблоны из базы данных
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content, name FROM templates WHERE id = ?', (main_template_id,))
        main_result = cursor.fetchone()
        
        cursor.execute('SELECT svg_content, name FROM templates WHERE id = ?', (photo_template_id,))
        photo_result = cursor.fetchone()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Один или оба шаблона не найдены'}), 404
        
        main_svg_content, main_name = main_result
        photo_svg_content, photo_name = photo_result
        conn.close()
        
        # Обрабатываем SVG с заменами (ИСПРАВЛЕННАЯ ФУНКЦИЯ)
        processed_main_svg = process_svg_advanced(main_svg_content, replacements)
        processed_photo_svg = process_svg_advanced(photo_svg_content, replacements)
        
        # Генерируем файлы
        carousel_id = str(uuid.uuid4())
        main_filename = f"carousel_{carousel_id}_main.svg"
        photo_filename = f"carousel_{carousel_id}_photo.svg"
        
        main_output_path = os.path.join(OUTPUT_DIR, 'carousel', main_filename)
        photo_output_path = os.path.join(OUTPUT_DIR, 'carousel', photo_filename)
        
        # Сохраняем как SVG
        with open(main_output_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_output_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        # Возвращаем публичные URL
        main_public_url = f"{request.host_url}output/carousel/{main_filename}"
        photo_public_url = f"{request.host_url}output/carousel/{photo_filename}"
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'images': [
                {
                    'type': 'main',
                    'url': main_public_url,
                    'template_id': main_template_id,
                    'template_name': main_name,
                    'format': 'svg'
                },
                {
                    'type': 'photo',
                    'url': photo_public_url,
                    'template_id': photo_template_id,
                    'template_name': photo_name,
                    'format': 'svg'
                }
            ],
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    try:
        ensure_db_exists()
        
        # Проверяем количество шаблонов
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM templates')
        template_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'healthy',
            'version': '6.0-images-fixed',
            'template_count': template_count,
            'features': [
                'Single image generation (SVG)',
                'Carousel generation (SVG)', 
                'FIXED: Image replacement in patterns',
                'FIXED: Font preservation',
                'Template display working',
                'Gunicorn compatible',
                'Render.com ready'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# Инициализация при запуске
if __name__ == '__main__':
    print("🚀 Запуск ИСПРАВЛЕННОГО SVG Template API сервера...")
    print("📊 Инициализация базы данных...")
    ensure_db_exists()
    print("✅ Сервер готов к работе!")
    
    # Получаем порт из переменной окружения (для Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Для Gunicorn
def create_app():
    """
    Фабрика приложений для Gunicorn
    """
    ensure_db_exists()
    return app

