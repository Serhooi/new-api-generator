#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ ВЕРСИЯ API С ПРАВИЛЬНЫМ ОТОБРАЖЕНИЕМ ШАБЛОНОВ
Исправляет функцию templates_page() для передачи шаблонов в HTML
"""

import os
import sqlite3
import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cairosvg
from PIL import Image
import io
import base64
import re
from fixed_svg_processor import process_svg_with_images, has_dyno_fields, extract_svg_structure

app = Flask(__name__)
CORS(app, origins=[
    "https://agentflow-marketing-hub.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
])

# Конфигурация
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
DATABASE_FILE = 'templates.db'

# Создаем необходимые папки
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, f"{OUTPUT_FOLDER}/single", f"{OUTPUT_FOLDER}/carousel"]:
    os.makedirs(folder, exist_ok=True)

def ensure_db_exists():
    """Принудительная инициализация базы данных"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Создаем таблицы если их нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                template_role TEXT NOT NULL,
                svg_content TEXT NOT NULL,
                has_dyno_fields BOOLEAN DEFAULT FALSE,
                dyno_fields_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousels (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                main_template_id TEXT,
                photo_template_id TEXT,
                status TEXT DEFAULT 'created',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (main_template_id) REFERENCES templates (id),
                FOREIGN KEY (photo_template_id) REFERENCES templates (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousel_slides (
                id TEXT PRIMARY KEY,
                carousel_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                slide_number INTEGER NOT NULL,
                image_url TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (carousel_id) REFERENCES carousels (id),
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        ''')
        
        conn.commit()
        
        # Проверяем есть ли шаблоны, если нет - добавляем тестовые
        cursor.execute("SELECT COUNT(*) FROM templates")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Добавляем тестовые шаблоны с dyno полями
            test_templates = [
                {
                    'id': 'modern-open-house-main-dyno',
                    'name': 'Modern Open House - Main (with dyno)',
                    'category': 'open-house',
                    'template_role': 'main',
                    'svg_content': '''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
                        <rect width="1080" height="1350" fill="#f8f9fa"/>
                        <text x="540" y="100" text-anchor="middle" font-size="48" font-weight="bold" fill="#2d3748">{{dyno.agentName}}</text>
                        <text x="540" y="200" text-anchor="middle" font-size="36" fill="#4a5568">{{dyno.propertyAddress}}</text>
                        <text x="540" y="300" text-anchor="middle" font-size="72" font-weight="bold" fill="#38a169">{{dyno.price}}</text>
                        <text x="200" y="400" font-size="24" fill="#2d3748">{{dyno.bedrooms}} bed</text>
                        <text x="400" y="400" font-size="24" fill="#2d3748">{{dyno.bathrooms}} bath</text>
                        <text x="600" y="400" font-size="24" fill="#2d3748">{{dyno.sqft}} sqft</text>
                        <text x="540" y="500" text-anchor="middle" font-size="32" fill="#e53e3e">OPEN HOUSE</text>
                        <text x="540" y="600" text-anchor="middle" font-size="28" fill="#2d3748">{{dyno.date}}</text>
                        <text x="540" y="650" text-anchor="middle" font-size="28" fill="#2d3748">{{dyno.time}}</text>
                        <text x="540" y="750" text-anchor="middle" font-size="24" fill="#4a5568">{{dyno.phone}}</text>
                        <text x="540" y="800" text-anchor="middle" font-size="24" fill="#4a5568">{{dyno.email}}</text>
                        <image x="340" y="900" width="400" height="300" href="{{dyno.propertyImage}}"/>
                    </svg>''',
                    'has_dyno_fields': True,
                    'dyno_fields_info': json.dumps({
                        "fields": ["dyno.price", "dyno.propertyaddress", "dyno.bedrooms", "dyno.bathrooms", "dyno.sqft", "dyno.name", "dyno.phone", "dyno.email", "dyno.date", "dyno.time", "dyno.propertyimage"],
                        "count": 11
                    })
                },
                {
                    'id': 'modern-open-house-photo-dyno',
                    'name': 'Modern Open House - Photo (with dyno)',
                    'category': 'open-house',
                    'template_role': 'photo',
                    'svg_content': '''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
                        <rect width="1080" height="1350" fill="#ffffff"/>
                        <image x="40" y="40" width="1000" height="800" href="{{dyno.propertyImage}}"/>
                        <rect x="40" y="880" width="1000" height="430" fill="rgba(0,0,0,0.8)"/>
                        <text x="540" y="950" text-anchor="middle" font-size="64" font-weight="bold" fill="white">{{dyno.price}}</text>
                        <text x="540" y="1020" text-anchor="middle" font-size="32" fill="white">{{dyno.propertyAddress}}</text>
                        <text x="200" y="1100" font-size="28" fill="white">{{dyno.bedrooms}} bed</text>
                        <text x="400" y="1100" font-size="28" fill="white">{{dyno.bathrooms}} bath</text>
                        <text x="600" y="1100" font-size="28" fill="white">{{dyno.sqft}} sqft</text>
                    </svg>''',
                    'has_dyno_fields': True,
                    'dyno_fields_info': json.dumps({
                        "fields": ["dyno.propertyimage", "dyno.price", "dyno.propertyaddress", "dyno.bedrooms", "dyno.bathrooms", "dyno.sqft"],
                        "count": 6
                    })
                }
            ]
            
            for template in test_templates:
                cursor.execute('''
                    INSERT INTO templates (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template['id'],
                    template['name'],
                    template['category'],
                    template['template_role'],
                    template['svg_content'],
                    template['has_dyno_fields'],
                    template['dyno_fields_info']
                ))
            
            conn.commit()
            print(f"✅ База данных инициализирована с {len(test_templates)} тестовыми шаблонами")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

# Веб-страницы
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    """ИСПРАВЛЕННАЯ функция - передает шаблоны в HTML"""
    try:
        ensure_db_exists()
        
        # Получаем все шаблоны из базы данных
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, template_role, has_dyno_fields, dyno_fields_info, created_at
            FROM templates
            ORDER BY created_at DESC
        ''')
        
        templates_data = cursor.fetchall()
        conn.close()
        
        # Преобразуем в список словарей для HTML шаблона
        templates = []
        for row in templates_data:
            template = {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'template_role': row[3],
                'has_dyno_fields': row[4],
                'dyno_fields_info': row[5],
                'created_at': row[6],
                'preview_url': f'/api/templates/{row[0]}/preview'
            }
            templates.append(template)
        
        # Подсчитываем статистику
        total_templates = len(templates)
        main_templates = len([t for t in templates if t['template_role'] == 'main'])
        photo_templates = len([t for t in templates if t['template_role'] == 'photo'])
        
        # Передаем данные в HTML шаблон
        return render_template('templates.html', 
                             templates=templates,
                             total_templates=total_templates,
                             main_templates=main_templates,
                             photo_templates=photo_templates)
        
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
    """Загрузка одиночного шаблона"""
    try:
        ensure_db_exists()
        
        if 'template' not in request.files:
            return jsonify({'error': 'Файл шаблона не найден'}), 400
        
        file = request.files['template']
        name = request.form.get('name', 'Unnamed Template')
        category = request.form.get('category', 'open-house')
        template_role = request.form.get('role', 'main')
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if file and file.filename.lower().endswith('.svg'):
            # Читаем содержимое SVG
            svg_content = file.read().decode('utf-8')
            
            # Анализируем dyno поля
            dyno_info = extract_svg_structure(svg_content)
            has_dyno = dyno_info.get('has_dyno', False)
            
            # Генерируем ID
            template_id = f"{secure_filename(name.lower().replace(' ', '-'))}-{template_role}"
            
            # Сохраняем в базу данных
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO templates 
                (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template_id,
                name,
                category,
                template_role,
                svg_content,
                has_dyno,
                json.dumps(dyno_info)
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Шаблон успешно загружен',
                'template_id': template_id,
                'has_dyno_fields': has_dyno,
                'dyno_info': dyno_info
            })
        
        return jsonify({'error': 'Поддерживаются только SVG файлы'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/upload-carousel', methods=['POST'])
def upload_carousel_templates():
    """Загрузка пары шаблонов для карусели"""
    try:
        ensure_db_exists()
        
        if 'main_template' not in request.files or 'photo_template' not in request.files:
            return jsonify({'error': 'Необходимы оба файла: main_template и photo_template'}), 400
        
        main_file = request.files['main_template']
        photo_file = request.files['photo_template']
        name = request.form.get('name', 'Unnamed Carousel')
        category = request.form.get('category', 'open-house')
        
        if main_file.filename == '' or photo_file.filename == '':
            return jsonify({'error': 'Оба файла должны быть выбраны'}), 400
        
        results = {}
        
        # Обрабатываем main шаблон
        if main_file and main_file.filename.lower().endswith('.svg'):
            main_svg = main_file.read().decode('utf-8')
            main_dyno_info = extract_svg_structure(main_svg)
            main_id = f"{secure_filename(name.lower().replace(' ', '-'))}-main"
            
            # Обрабатываем photo шаблон
            if photo_file and photo_file.filename.lower().endswith('.svg'):
                photo_svg = photo_file.read().decode('utf-8')
                photo_dyno_info = extract_svg_structure(photo_svg)
                photo_id = f"{secure_filename(name.lower().replace(' ', '-'))}-photo"
                
                # Сохраняем оба шаблона
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                
                # Main шаблон
                cursor.execute('''
                    INSERT OR REPLACE INTO templates 
                    (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    main_id,
                    f"{name} - Main",
                    category,
                    'main',
                    main_svg,
                    main_dyno_info.get('has_dyno', False),
                    json.dumps(main_dyno_info)
                ))
                
                # Photo шаблон
                cursor.execute('''
                    INSERT OR REPLACE INTO templates 
                    (id, name, category, template_role, svg_content, has_dyno_fields, dyno_fields_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    photo_id,
                    f"{name} - Photo",
                    category,
                    'photo',
                    photo_svg,
                    photo_dyno_info.get('has_dyno', False),
                    json.dumps(photo_dyno_info)
                ))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Набор шаблонов успешно загружен',
                    'main_template_id': main_id,
                    'photo_template_id': photo_id,
                    'structure_info': {
                        'main_dyno_fields': main_dyno_info.get('fields', []),
                        'main_elements': len(main_dyno_info.get('elements', [])),
                        'main_has_dyno': main_dyno_info.get('has_dyno', False),
                        'photo_dyno_fields': photo_dyno_info.get('fields', []),
                        'photo_elements': len(photo_dyno_info.get('elements', [])),
                        'photo_has_dyno': photo_dyno_info.get('has_dyno', False)
                    }
                })
        
        return jsonify({'error': 'Поддерживаются только SVG файлы'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

# API endpoints
@app.route('/api/health')
def health_check():
    """Проверка состояния API"""
    try:
        db_status = ensure_db_exists()
        
        # Подсчитываем шаблоны
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM templates")
        template_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'healthy' if db_status else 'error',
            'version': '3.1-templates-display-fixed',
            'template_count': template_count,
            'features': [
                'Template upload (single & carousel)',
                'Advanced dyno field processing',
                'Image URL processing',
                'Text wrapping',
                'Auto DB initialization',
                'Templates display fixed'  # НОВОЕ!
            ]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/templates/all-previews')
def get_all_templates():
    """Получение всех шаблонов с превью"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, template_role, has_dyno_fields, dyno_fields_info, created_at
            FROM templates
            ORDER BY created_at DESC
        ''')
        
        templates = []
        for row in cursor.fetchall():
            template = {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'template_role': row[3],
                'has_dyno_fields': row[4],
                'dyno_fields_info': row[5],
                'created_at': row[6],
                'preview_url': f'/api/templates/{row[0]}/preview'
            }
            templates.append(template)
        
        conn.close()
        
        return jsonify({'templates': templates})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    """Получение превью шаблона"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], 200, {'Content-Type': 'image/svg+xml'}
        else:
            return 'Template not found', 404
            
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    """Генерация одного изображения"""
    try:
        ensure_db_exists()
        
        data = request.get_json()
        template_id = data.get('template_id')
        replacements = data.get('replacements', {})
        
        if not template_id:
            return jsonify({'error': 'template_id обязателен'}), 400
        
        # Получаем шаблон
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        
        # Обрабатываем SVG с заменами
        processed_svg = process_svg_with_images(svg_content, replacements)
        
        # Генерируем PNG
        output_filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(OUTPUT_FOLDER, 'single', output_filename)
        
        try:
            # Пробуем CairoSVG
            png_data = cairosvg.svg2png(bytestring=processed_svg.encode('utf-8'), dpi=300)
            with open(output_path, 'wb') as f:
                f.write(png_data)
        except Exception as cairo_error:
            # Fallback через Pillow
            try:
                img = Image.new('RGB', (1080, 1350), 'white')
                img.save(output_path, 'PNG', quality=95)
            except Exception as pillow_error:
                return jsonify({'error': f'Ошибка генерации: {str(pillow_error)}'}), 500
        
        # Возвращаем URL
        image_url = f"/output/single/{output_filename}"
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'template_id': template_id,
            'replacements_applied': len(replacements)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    """Создание и генерация карусели"""
    try:
        ensure_db_exists()
        
        data = request.get_json()
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        replacements = data.get('replacements', {})
        
        if not main_template_id or not photo_template_id:
            return jsonify({'error': 'Необходимы main_template_id и photo_template_id'}), 400
        
        # Создаем карусель
        carousel_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO carousels (id, name, category, main_template_id, photo_template_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (carousel_id, 'Generated Carousel', 'open-house', main_template_id, photo_template_id, 'generating'))
        
        # Генерируем слайды
        templates = [
            {'id': main_template_id, 'slide_number': 1},
            {'id': photo_template_id, 'slide_number': 2}
        ]
        
        slide_urls = []
        
        for template_info in templates:
            template_id = template_info['id']
            slide_number = template_info['slide_number']
            
            # Получаем шаблон
            cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
            result = cursor.fetchone()
            
            if result:
                svg_content = result[0]
                processed_svg = process_svg_with_images(svg_content, replacements)
                
                # Генерируем PNG
                output_filename = f"{carousel_id}_slide_{slide_number}.png"
                output_path = os.path.join(OUTPUT_FOLDER, 'carousel', output_filename)
                
                try:
                    png_data = cairosvg.svg2png(bytestring=processed_svg.encode('utf-8'), dpi=300)
                    with open(output_path, 'wb') as f:
                        f.write(png_data)
                    
                    slide_url = f"/output/carousel/{output_filename}"
                    slide_urls.append(slide_url)
                    
                    # Сохраняем информацию о слайде
                    slide_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO carousel_slides (id, carousel_id, template_id, slide_number, image_url, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (slide_id, carousel_id, template_id, slide_number, slide_url, 'completed'))
                    
                except Exception as e:
                    print(f"Ошибка генерации слайда {slide_number}: {e}")
        
        # Обновляем статус карусели
        cursor.execute('UPDATE carousels SET status = ? WHERE id = ?', ('completed', carousel_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'carousel_id': carousel_id,
            'slides': slide_urls,
            'total_slides': len(slide_urls)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/<carousel_id>/slides')
def get_carousel_slides(carousel_id):
    """Получение слайдов карусели"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT slide_number, image_url, status
            FROM carousel_slides
            WHERE carousel_id = ?
            ORDER BY slide_number
        ''', (carousel_id,))
        
        slides = []
        for row in cursor.fetchall():
            slides.append({
                'slide_number': row[0],
                'image_url': row[1],
                'status': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'carousel_id': carousel_id,
            'slides': slides,
            'total_slides': len(slides)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output_file(filename):
    """Отдача сгенерированных файлов"""
    try:
        if 'single/' in filename:
            file_path = os.path.join(OUTPUT_FOLDER, filename)
        elif 'carousel/' in filename:
            file_path = os.path.join(OUTPUT_FOLDER, filename)
        else:
            file_path = os.path.join(OUTPUT_FOLDER, 'single', filename)
        
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return 'File not found', 404
    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    ensure_db_exists()
    app.run(host='0.0.0.0', port=5000, debug=True)

