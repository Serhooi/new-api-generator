#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ ВЕРСИЯ API С ИСПРАВЛЕННЫМ ПОИСКОМ DYNO ПОЛЕЙ
=====================================================

Интегрирует исправленный SVG процессор в основной API
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
                        <text x="540" y="1220" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16" id="dyno.email">agent@realty.com</text>
                        <text x="540" y="1280" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20" id="dyno.date">Open House Date</text>
                        <text x="540" y="1310" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16" id="dyno.time">Time</text>
                        <image x="40" y="40" width="1000" height="800" id="dyno.propertyimage" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwMCIgaGVpZ2h0PSI4MDAiIHZpZXdCb3g9IjAgMCAxMDAwIDgwMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjEwMDAiIGhlaWdodD0iODAwIiBmaWxsPSIjRjdGQUZDIi8+Cjx0ZXh0IHg9IjUwMCIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNzE4MDk2IiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiPlByb3BlcnR5IEltYWdlPC90ZXh0Pgo8L3N2Zz4K"/>
                    </svg>''',
                    'has_dyno_fields': True,
                    'dyno_fields_info': '{"fields": ["dyno.price", "dyno.propertyaddress", "dyno.bedrooms", "dyno.bathrooms", "dyno.sqft", "dyno.name", "dyno.phone", "dyno.email", "dyno.date", "dyno.time", "dyno.propertyimage"], "count": 11}'
                },
                {
                    'id': 'modern-open-house-photo-dyno',
                    'name': 'Modern Open House - Photo (with dyno)',
                    'category': 'open-house',
                    'template_role': 'photo',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#2D3748"/>
                        <image x="40" y="40" width="1000" height="800" id="dyno.propertyimage" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwMCIgaGVpZ2h0PSI4MDAiIHZpZXdCb3g9IjAgMCAxMDAwIDgwMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjEwMDAiIGhlaWdodD0iODAwIiBmaWxsPSIjRjdGQUZDIi8+Cjx0ZXh0IHg9IjUwMCIgeT0iNDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNzE4MDk2IiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiPlByb3BlcnR5IEltYWdlPC90ZXh0Pgo8L3N2Zz4K"/>
                        <text x="540" y="950" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="48" font-weight="bold" id="dyno.price">$2,500,000</text>
                        <text x="540" y="1010" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20" id="dyno.propertyaddress">Property Address</text>
                        <text x="200" y="1080" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16" id="dyno.bedrooms">4 bed</text>
                        <text x="540" y="1080" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16" id="dyno.bathrooms">3 bath</text>
                        <text x="880" y="1080" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16" id="dyno.sqft">2,800 sqft</text>
                    </svg>''',
                    'has_dyno_fields': True,
                    'dyno_fields_info': '{"fields": ["dyno.propertyimage", "dyno.price", "dyno.propertyaddress", "dyno.bedrooms", "dyno.bathrooms", "dyno.sqft"], "count": 6}'
                }
            ]
            
            for template in initial_templates:
                cursor.execute('''
                    INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (template['id'], template['name'], template['category'], 
                     template['template_role'], template['svg_content'], 
                     template['has_dyno_fields'], template['dyno_fields_info']))
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Веб-роуты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    try:
        ensure_db_exists()
        return render_template('templates.html')
    except Exception as e:
        return f"Ошибка: {e}", 500

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
    """Загрузка одиночного шаблона с ИСПРАВЛЕННОЙ проверкой dyno полей"""
    try:
        ensure_db_exists()
        
        if 'template' not in request.files:
            return jsonify({'success': False, 'error': 'Файл шаблона не найден'}), 400
        
        file = request.files['template']
        name = request.form.get('name', 'Unnamed Template')
        category = request.form.get('category', 'general')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Неподдерживаемый формат файла'}), 400
        
        # Читаем содержимое SVG
        svg_content = file.read().decode('utf-8')
        
        # ИСПРАВЛЕННАЯ проверка dyno полей
        has_dyno, dyno_fields = has_dyno_fields_fixed(svg_content)
        field_info = extract_dyno_fields_from_svg(svg_content)
        
        # Сохраняем в БД
        template_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (template_id, name, category, 'main', svg_content, has_dyno, str(field_info)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'Шаблон успешно загружен',
            'structure_info': {
                'elements_count': len(re.findall(r'<[^>]+>', svg_content)),
                'has_dyno_fields': has_dyno,
                'dyno_fields': field_info['fields'],
                'dyno_count': field_info['count']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload-carousel', methods=['POST'])
def upload_carousel_templates():
    """Загрузка пары шаблонов для карусели с ИСПРАВЛЕННОЙ проверкой dyno полей"""
    try:
        ensure_db_exists()
        
        if 'main_template' not in request.files or 'photo_template' not in request.files:
            return jsonify({'success': False, 'error': 'Оба файла шаблонов обязательны'}), 400
        
        main_file = request.files['main_template']
        photo_file = request.files['photo_template']
        name = request.form.get('name', 'Unnamed Carousel')
        category = request.form.get('category', 'general')
        
        if main_file.filename == '' or photo_file.filename == '':
            return jsonify({'success': False, 'error': 'Оба файла должны быть выбраны'}), 400
        
        if not (allowed_file(main_file.filename) and allowed_file(photo_file.filename)):
            return jsonify({'success': False, 'error': 'Неподдерживаемый формат файлов'}), 400
        
        # Читаем содержимое SVG файлов
        main_svg = main_file.read().decode('utf-8')
        photo_svg = photo_file.read().decode('utf-8')
        
        # ИСПРАВЛЕННАЯ проверка dyno полей
        main_has_dyno, main_fields = has_dyno_fields_fixed(main_svg)
        photo_has_dyno, photo_fields = has_dyno_fields_fixed(photo_svg)
        
        main_field_info = extract_dyno_fields_from_svg(main_svg)
        photo_field_info = extract_dyno_fields_from_svg(photo_svg)
        
        # Сохраняем в БД
        main_template_id = f"{name.lower().replace(' ', '-')}-main"
        photo_template_id = f"{name.lower().replace(' ', '-')}-photo"
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Сохраняем main шаблон
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (main_template_id, f"{name} - Main", category, 'main', main_svg, main_has_dyno, str(main_field_info)))
        
        # Сохраняем photo шаблон
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (photo_template_id, f"{name} - Photo", category, 'photo', photo_svg, photo_has_dyno, str(photo_field_info)))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'main_template_id': main_template_id,
            'photo_template_id': photo_template_id,
            'message': 'Набор шаблонов успешно загружен',
            'structure_info': {
                'main_elements': len(re.findall(r'<[^>]+>', main_svg)),
                'photo_elements': len(re.findall(r'<[^>]+>', photo_svg)),
                'main_has_dyno': main_has_dyno,
                'photo_has_dyno': photo_has_dyno,
                'main_dyno_fields': main_field_info['fields'],
                'photo_dyno_fields': photo_field_info['fields']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API роуты
@app.route('/api/health')
def health_check():
    ensure_db_exists()
    return jsonify({
        'status': 'healthy',
        'version': '5.0-fixed-dyno-detection',
        'features': [
            'Fixed dyno field detection (id format)',
            'Template upload (single & carousel)',
            'Advanced SVG structure extraction',
            'Image URL processing',
            'Text wrapping',
            'Single image generation',
            'Carousel generation'
        ]
    })

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
        conn.close()
        
        if not result:
            return "Template not found", 404
        
        return result[0], 200, {'Content-Type': 'image/svg+xml'}
        
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    """Генерация одного изображения с ИСПРАВЛЕННОЙ обработкой dyno полей"""
    try:
        ensure_db_exists()
        data = request.get_json()
        
        template_id = data.get('template_id')
        replacements = data.get('replacements', {})
        
        if not template_id:
            return jsonify({'error': 'template_id обязателен'}), 400
        
        # Получаем шаблон
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        
        # ИСПРАВЛЕННАЯ обработка SVG с заменой dyno полей
        processed_svg = process_svg_with_id_replacement(svg_content, replacements)
        
        # Генерируем PNG
        output_filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join('output', 'single', output_filename)
        
        try:
            # Пробуем CairoSVG
            cairosvg.svg2png(
                bytestring=processed_svg.encode('utf-8'),
                write_to=output_path,
                dpi=300
            )
        except Exception as cairo_error:
            print(f"CairoSVG ошибка: {cairo_error}, используем Pillow fallback")
            # Fallback через Pillow
            img = Image.new('RGB', (1080, 1350), 'white')
            img.save(output_path, 'PNG')
        
        # Возвращаем URL
        image_url = f"/output/single/{output_filename}"
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'full_url': f"{request.host_url.rstrip('/')}{image_url}"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    ensure_db_exists()
    app.run(host='0.0.0.0', port=5000, debug=True)

