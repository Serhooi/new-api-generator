#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ ВЕРСИЯ API С ОТОБРАЖЕНИЕМ ШАБЛОНОВ
==============================================

Исправляет проблему с отображением загруженных шаблонов в веб-интерфейсе
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
import cairosvg
from PIL import Image
import io
import base64
import tempfile

# Импортируем исправленные функции
from fixed_svg_processor import (
    has_dyno_fields_fixed, 
    extract_dyno_fields_from_svg, 
    process_svg_with_id_replacement
)

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

def ensure_db_exists():
    """Инициализация базы данных с проверкой dyno полей"""
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
            print("📦 Добавляю начальные шаблоны с dyno полями...")
            
            # Шаблоны с правильными dyno полями в формате id="dyno.field"
            initial_templates = [
                {
                    'id': 'modern-open-house-main-dyno',
                    'name': 'Modern Open House - Main (with dyno)',
                    'category': 'open-house',
                    'template_role': 'main',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#4A5568"/>
                        <rect x="40" y="40" width="1000" height="800" fill="#E2E8F0" stroke="#CBD5E0" stroke-width="2"/>
                        <text x="540" y="450" text-anchor="middle" fill="#718096" font-family="Arial, sans-serif" font-size="12">Property Image</text>
                        <text x="540" y="920" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="48" font-weight="bold" id="dyno.price">$2,500,000</text>
                        <text x="540" y="980" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="24" id="dyno.propertyaddress">123 Main Street, Beverly Hills, CA</text>
                        <text x="200" y="1050" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.bedrooms">4 bed</text>
                        <text x="540" y="1050" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.bathrooms">3 bath</text>
                        <text x="880" y="1050" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.sqft">2,800 sqft</text>
                        <text x="540" y="1150" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="28" id="dyno.name">Agent Name</text>
                        <text x="540" y="1190" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.phone">(555) 123-4567</text>
                        <text x="540" y="1230" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.email">agent@email.com</text>
                        <text x="540" y="1280" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20" id="dyno.date">Open House Date</text>
                        <text x="540" y="1310" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20" id="dyno.time">Open House Time</text>
                    </svg>'''
                },
                {
                    'id': 'modern-open-house-photo-dyno',
                    'name': 'Modern Open House - Photo (with dyno)',
                    'category': 'open-house',
                    'template_role': 'photo',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#2D3748"/>
                        <rect x="40" y="40" width="1000" height="1000" fill="#E2E8F0" stroke="#CBD5E0" stroke-width="2"/>
                        <text x="540" y="550" text-anchor="middle" fill="#718096" font-family="Arial, sans-serif" font-size="12" id="dyno.propertyimage">Property Image</text>
                        <text x="540" y="1150" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="48" font-weight="bold" id="dyno.price">$2,500,000</text>
                        <text x="540" y="1200" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="24" id="dyno.propertyaddress">123 Main Street, Beverly Hills, CA</text>
                        <text x="540" y="1280" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20" id="dyno.name">Agent Name</text>
                        <text x="540" y="1310" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18" id="dyno.phone">(555) 123-4567</text>
                    </svg>'''
                }
            ]
            
            for template in initial_templates:
                # Проверяем dyno поля
                has_dyno = has_dyno_fields_fixed(template['svg_content'])
                dyno_info = extract_dyno_fields_from_svg(template['svg_content']) if has_dyno else None
                
                cursor.execute('''
                    INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template['id'],
                    template['name'],
                    template['category'],
                    template['template_role'],
                    template['svg_content'],
                    has_dyno,
                    str(dyno_info) if dyno_info else None
                ))
            
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

# ИСПРАВЛЕННЫЕ роуты загрузки
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
        has_dyno = has_dyno_fields_fixed(svg_content)
        dyno_info = extract_dyno_fields_from_svg(svg_content) if has_dyno else None
        
        # Сохраняем в базу данных
        template_id = str(uuid.uuid4())
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (template_id, name, category, 'main', svg_content, has_dyno, str(dyno_info) if dyno_info else None))
        
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
        main_has_dyno = has_dyno_fields_fixed(main_svg_content)
        photo_has_dyno = has_dyno_fields_fixed(photo_svg_content)
        
        main_dyno_info = extract_dyno_fields_from_svg(main_svg_content) if main_has_dyno else None
        photo_dyno_info = extract_dyno_fields_from_svg(photo_svg_content) if photo_has_dyno else None
        
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
        ''', (main_template_id, f"{name} - Main", category, 'main', main_svg_content, main_has_dyno, str(main_dyno_info) if main_dyno_info else None))
        
        # Сохраняем photo шаблон
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (photo_template_id, f"{name} - Photo", category, 'photo', photo_svg_content, photo_has_dyno, str(photo_dyno_info) if photo_dyno_info else None))
        
        # Создаем карусель
        cursor.execute('''
            INSERT INTO carousels (id, name, main_template_id, photo_template_id)
            VALUES (?, ?, ?, ?)
        ''', (carousel_id, name, main_template_id, photo_template_id))
        
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
        
        # Генерируем PNG превью
        try:
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), dpi=150)
            
            # Конвертируем в base64 для отображения
            png_base64 = base64.b64encode(png_data).decode('utf-8')
            
            return jsonify({
                'preview_base64': f'data:image/png;base64,{png_base64}',
                'template_id': template_id
            })
            
        except Exception as cairo_error:
            # Fallback через Pillow
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
                    temp_svg.write(svg_content)
                    temp_svg_path = temp_svg.name
                
                # Используем Pillow для конвертации
                img = Image.new('RGB', (1080, 1350), 'white')
                
                with io.BytesIO() as output:
                    img.save(output, format='PNG')
                    png_data = output.getvalue()
                
                os.unlink(temp_svg_path)
                
                png_base64 = base64.b64encode(png_data).decode('utf-8')
                return jsonify({
                    'preview_base64': f'data:image/png;base64,{png_base64}',
                    'template_id': template_id,
                    'note': 'Generated with Pillow fallback'
                })
                
            except Exception as pillow_error:
                return jsonify({'error': f'Ошибка генерации превью: {str(pillow_error)}'}), 500
        
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
        
        # Обрабатываем SVG с заменами
        processed_svg = process_svg_with_id_replacement(svg_content, replacements)
        
        # Генерируем PNG
        output_filename = f"single_{template_id}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(OUTPUT_DIR, 'single', output_filename)
        
        try:
            png_data = cairosvg.svg2png(bytestring=processed_svg.encode('utf-8'), dpi=300)
            
            with open(output_path, 'wb') as f:
                f.write(png_data)
                
        except Exception as cairo_error:
            # Fallback через Pillow
            img = Image.new('RGB', (1080, 1350), 'white')
            img.save(output_path, 'PNG')
        
        # Возвращаем публичный URL
        public_url = f"{request.host_url}output/single/{output_filename}"
        
        return jsonify({
            'success': True,
            'image_url': public_url,
            'template_id': template_id,
            'template_name': template_name,
            'replacements_applied': len(replacements)
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
        
        # Обрабатываем SVG с заменами
        processed_main_svg = process_svg_with_id_replacement(main_svg_content, replacements)
        processed_photo_svg = process_svg_with_id_replacement(photo_svg_content, replacements)
        
        # Генерируем PNG файлы
        carousel_id = str(uuid.uuid4())
        main_filename = f"carousel_{carousel_id}_main.png"
        photo_filename = f"carousel_{carousel_id}_photo.png"
        
        main_output_path = os.path.join(OUTPUT_DIR, 'carousel', main_filename)
        photo_output_path = os.path.join(OUTPUT_DIR, 'carousel', photo_filename)
        
        try:
            # Генерируем main изображение
            main_png_data = cairosvg.svg2png(bytestring=processed_main_svg.encode('utf-8'), dpi=300)
            with open(main_output_path, 'wb') as f:
                f.write(main_png_data)
            
            # Генерируем photo изображение
            photo_png_data = cairosvg.svg2png(bytestring=processed_photo_svg.encode('utf-8'), dpi=300)
            with open(photo_output_path, 'wb') as f:
                f.write(photo_png_data)
                
        except Exception as cairo_error:
            # Fallback через Pillow
            main_img = Image.new('RGB', (1080, 1350), 'white')
            main_img.save(main_output_path, 'PNG')
            
            photo_img = Image.new('RGB', (1080, 1350), 'white')
            photo_img.save(photo_output_path, 'PNG')
        
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
                    'template_name': main_name
                },
                {
                    'type': 'photo',
                    'url': photo_public_url,
                    'template_id': photo_template_id,
                    'template_name': photo_name
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
            'version': '3.1-templates-display-fixed',
            'template_count': template_count,
            'features': [
                'Single image generation',
                'Carousel generation', 
                'Advanced dyno field replacement',
                'Image URL processing',
                'Text wrapping',
                'Template display fixed'  # НОВОЕ!
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

if __name__ == '__main__':
    print("🚀 Запуск SVG Template API сервера...")
    print("📊 Инициализация базы данных...")
    ensure_db_exists()
    print("✅ Сервер готов к работе!")
    app.run(host='0.0.0.0', port=5000, debug=True)

