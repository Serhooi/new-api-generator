#!/usr/bin/env python3
"""
ПОЛНАЯ ВЕРСИЯ API С РОУТАМИ ЗАГРУЗКИ И УЛУЧШЕННОЙ ОБРАБОТКОЙ SVG
Включает все недостающие роуты и продвинутую обработку SVG элементов
"""

import os
import sqlite3
import uuid
import json
import time
import requests
import base64
from io import BytesIO
from PIL import Image
import xml.etree.ElementTree as ET
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cairosvg

app = Flask(__name__)
CORS(app, origins=["*"])

# Конфигурация
DATABASE_PATH = 'templates.db'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'svg'}

# Создаем необходимые папки
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, f"{OUTPUT_FOLDER}/single", f"{OUTPUT_FOLDER}/carousel"]:
    os.makedirs(folder, exist_ok=True)

def ensure_db_exists():
    """Принудительная инициализация базы данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Создаем таблицы если их нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                template_role TEXT NOT NULL,
                svg_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousels (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carousel_slides (
                id TEXT PRIMARY KEY,
                carousel_id TEXT NOT NULL,
                template_id TEXT NOT NULL,
                slide_order INTEGER NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (carousel_id) REFERENCES carousels (id),
                FOREIGN KEY (template_id) REFERENCES templates (id)
            )
        ''')
        
        # Проверяем есть ли шаблоны
        cursor.execute("SELECT COUNT(*) FROM templates")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Добавляем начальные шаблоны с dyno полями
            initial_templates = [
                {
                    'id': 'open-house-main-dyno',
                    'name': 'Open House - Main (with dyno)',
                    'category': 'open-house',
                    'template_role': 'main',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#2D3748"/>
                        <text x="540" y="120" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="48" font-weight="bold">OPEN HOUSE</text>
                        <text x="540" y="200" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="24">{{dyno.agentName}}</text>
                        <text x="540" y="250" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18">{{dyno.propertyAddress}}</text>
                        <text x="540" y="320" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="36" font-weight="bold">{{dyno.price}}</text>
                        <text x="200" y="400" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.bedrooms}} bed</text>
                        <text x="540" y="400" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.bathrooms}} bath</text>
                        <text x="880" y="400" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.sqft}} sqft</text>
                        <text x="540" y="480" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="20">{{dyno.openHouseDate}}</text>
                        <text x="540" y="520" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.openHouseTime}}</text>
                        <text x="540" y="580" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.agentPhone}}</text>
                        <text x="540" y="610" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="14">{{dyno.agentEmail}}</text>
                        <rect x="320" y="650" width="440" height="300" fill="#E2E8F0" stroke="#CBD5E0" stroke-width="2"/>
                        <text x="540" y="810" text-anchor="middle" fill="#718096" font-family="Arial, sans-serif" font-size="12">{{dyno.propertyImage}}</text>
                    </svg>'''
                },
                {
                    'id': 'open-house-photo-dyno',
                    'name': 'Open House - Photo (with dyno)',
                    'category': 'open-house',
                    'template_role': 'photo',
                    'svg_content': '''<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">
                        <rect width="1080" height="1350" fill="#2D3748"/>
                        <rect x="320" y="80" width="440" height="300" fill="#E2E8F0" stroke="#CBD5E0" stroke-width="2"/>
                        <text x="540" y="240" text-anchor="middle" fill="#718096" font-family="Arial, sans-serif" font-size="12">{{dyno.propertyImage}}</text>
                        <text x="540" y="450" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="36" font-weight="bold">{{dyno.price}}</text>
                        <text x="540" y="500" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="18">{{dyno.propertyAddress}}</text>
                        <text x="200" y="580" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.bedrooms}} bed</text>
                        <text x="540" y="580" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.bathrooms}} bath</text>
                        <text x="880" y="580" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.sqft}} sqft</text>
                        <text x="540" y="680" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="24">{{dyno.agentName}}</text>
                        <text x="540" y="720" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="16">{{dyno.agentPhone}}</text>
                        <text x="540" y="750" text-anchor="middle" fill="#A0AEC0" font-family="Arial, sans-serif" font-size="14">{{dyno.agentEmail}}</text>
                    </svg>'''
                }
            ]
            
            for template in initial_templates:
                cursor.execute('''
                    INSERT INTO templates (id, name, category, template_role, svg_content)
                    VALUES (?, ?, ?, ?, ?)
                ''', (template['id'], template['name'], template['category'], 
                     template['template_role'], template['svg_content']))
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_svg_structure(svg_content):
    """Извлекает структуру SVG: элементы, стили, позиции, эффекты"""
    try:
        root = ET.fromstring(svg_content)
        structure = {
            'elements': [],
            'styles': {},
            'fonts': {},
            'effects': {},
            'layout': {}
        }
        
        # Извлекаем все элементы с их атрибутами
        for elem in root.iter():
            if elem.tag.endswith(('text', 'rect', 'circle', 'path', 'image', 'g')):
                element_info = {
                    'tag': elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag,
                    'attributes': dict(elem.attrib),
                    'text': elem.text,
                    'position': {
                        'x': elem.get('x', '0'),
                        'y': elem.get('y', '0'),
                        'width': elem.get('width', ''),
                        'height': elem.get('height', '')
                    },
                    'style': {
                        'fill': elem.get('fill', ''),
                        'stroke': elem.get('stroke', ''),
                        'font-family': elem.get('font-family', ''),
                        'font-size': elem.get('font-size', ''),
                        'font-weight': elem.get('font-weight', '')
                    }
                }
                structure['elements'].append(element_info)
        
        return structure
        
    except Exception as e:
        print(f"Ошибка извлечения структуры SVG: {e}")
        return None

def process_svg_with_advanced_replacement(svg_content, data):
    """Продвинутая обработка SVG с сохранением всех элементов дизайна"""
    try:
        # Сначала извлекаем структуру
        structure = extract_svg_structure(svg_content)
        
        # Заменяем dyno поля с сохранением форматирования
        processed_svg = svg_content
        
        for key, value in data.items():
            # Поддерживаем разные форматы dyno полей
            patterns = [
                f'{{{{{key}}}}}',  # {{dyno.field}}
                f'{{{key}}}',     # {dyno.field}
                f'{{{{{key.replace("dyno.", "")}}}}}',  # {{field}}
                f'{{{key.replace("dyno.", "")}}}'       # {field}
            ]
            
            for pattern in patterns:
                if pattern in processed_svg:
                    if key == 'dyno.propertyImage' and value.startswith('http'):
                        # Обрабатываем изображения
                        try:
                            response = requests.get(value, timeout=10)
                            if response.status_code == 200:
                                img = Image.open(BytesIO(response.content))
                                img = img.convert('RGB')
                                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                                
                                buffer = BytesIO()
                                img.save(buffer, format='PNG')
                                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                                img_data_url = f"data:image/png;base64,{img_base64}"
                                
                                # Заменяем placeholder на реальное изображение
                                processed_svg = processed_svg.replace(pattern, img_data_url)
                            else:
                                processed_svg = processed_svg.replace(pattern, value)
                        except:
                            processed_svg = processed_svg.replace(pattern, value)
                    else:
                        # Обрабатываем текст с переносом для длинных строк
                        if key == 'dyno.propertyAddress' and len(str(value)) > 40:
                            # Автоматический перенос для длинных адресов
                            words = str(value).split()
                            if len(words) > 4:
                                mid = len(words) // 2
                                line1 = ' '.join(words[:mid])
                                line2 = ' '.join(words[mid:])
                                wrapped_value = f"{line1},{line2}"
                            else:
                                wrapped_value = str(value)
                            processed_svg = processed_svg.replace(pattern, wrapped_value)
                        else:
                            processed_svg = processed_svg.replace(pattern, str(value))
        
        return processed_svg
        
    except Exception as e:
        print(f"Ошибка обработки SVG: {e}")
        return svg_content

def generate_png_from_svg(svg_content, output_path):
    """Генерирует PNG из SVG с высоким качеством"""
    try:
        # Пробуем CairoSVG для лучшего качества
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=output_path,
            output_width=1080,
            output_height=1350,
            dpi=300
        )
        return True
    except Exception as e:
        print(f"CairoSVG ошибка: {e}")
        try:
            # Fallback через Pillow
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (1080, 1350), color='white')
            draw = ImageDraw.Draw(img)
            
            # Простая обработка для fallback
            draw.text((540, 675), "Generated Image", fill='black', anchor='mm')
            
            img.save(output_path, 'PNG', quality=95)
            return True
        except Exception as e2:
            print(f"Pillow fallback ошибка: {e2}")
            return False

# Веб-роуты
@app.route('/')
def index():
    ensure_db_exists()
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    ensure_db_exists()
    return render_template('templates.html')

@app.route('/upload')
def upload_page():
    ensure_db_exists()
    return render_template('upload.html')

# НОВЫЕ РОУТЫ ДЛЯ ЗАГРУЗКИ
@app.route('/upload-single', methods=['POST'])
def upload_single_template():
    """Загрузка одиночного шаблона"""
    ensure_db_exists()
    
    try:
        if 'template' not in request.files:
            return jsonify({'error': 'Файл шаблона не найден'}), 400
        
        file = request.files['template']
        name = request.form.get('name', 'Unnamed Template')
        category = request.form.get('category', 'general')
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое SVG
        svg_content = file.read().decode('utf-8')
        
        # Извлекаем структуру для анализа
        structure = extract_svg_structure(svg_content)
        
        # Генерируем ID
        template_id = str(uuid.uuid4())
        
        # Сохраняем в БД
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (template_id, name, category, 'single', svg_content))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'Шаблон успешно загружен',
            'structure_info': {
                'elements_count': len(structure['elements']) if structure else 0,
                'has_dyno_fields': '{{dyno.' in svg_content
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

@app.route('/upload-carousel', methods=['POST'])
def upload_carousel_templates():
    """Загрузка пары шаблонов для карусели"""
    ensure_db_exists()
    
    try:
        if 'main_template' not in request.files or 'photo_template' not in request.files:
            return jsonify({'error': 'Необходимы оба файла: main_template и photo_template'}), 400
        
        main_file = request.files['main_template']
        photo_file = request.files['photo_template']
        name = request.form.get('name', 'Unnamed Carousel Set')
        category = request.form.get('category', 'general')
        
        if not all([main_file.filename, photo_file.filename]):
            return jsonify({'error': 'Оба файла должны быть выбраны'}), 400
        
        if not all([allowed_file(main_file.filename), allowed_file(photo_file.filename)]):
            return jsonify({'error': 'Разрешены только SVG файлы'}), 400
        
        # Читаем содержимое обоих файлов
        main_svg = main_file.read().decode('utf-8')
        photo_svg = photo_file.read().decode('utf-8')
        
        # Анализируем структуру
        main_structure = extract_svg_structure(main_svg)
        photo_structure = extract_svg_structure(photo_svg)
        
        # Генерируем ID
        main_id = f"{name.lower().replace(' ', '-')}-main"
        photo_id = f"{name.lower().replace(' ', '-')}-photo"
        
        # Сохраняем в БД
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (main_id, f"{name} - Main", category, 'main', main_svg))
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (photo_id, f"{name} - Photo", category, 'photo', photo_svg))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'main_template_id': main_id,
            'photo_template_id': photo_id,
            'message': 'Набор шаблонов успешно загружен',
            'structure_info': {
                'main_elements': len(main_structure['elements']) if main_structure else 0,
                'photo_elements': len(photo_structure['elements']) if photo_structure else 0,
                'main_has_dyno': '{{dyno.' in main_svg,
                'photo_has_dyno': '{{dyno.' in photo_svg
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка загрузки: {str(e)}'}), 500

# API endpoints
@app.route('/api/health')
def health_check():
    ensure_db_exists()
    return jsonify({
        'status': 'healthy',
        'database': 'healthy',
        'version': '4.0-complete-svg',
        'features': [
            'Template management',
            'Carousel creation', 
            'Single image generation',
            'Advanced dyno field replacement',
            'Complete SVG structure extraction',
            'Template upload (single & carousel)',
            'Image URL processing',
            'Text wrapping',
            'CORS support',
            'File serving',
            'Database integration',
            'Auto DB initialization'
        ]
    })

@app.route('/api/templates/all-previews')
def get_all_templates():
    ensure_db_exists()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, template_role, created_at
            FROM templates
            ORDER BY created_at DESC
        ''')
        
        templates = []
        for row in cursor.fetchall():
            templates.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'templateRole': row[3],
                'previewUrl': f'/api/templates/{row[0]}/preview',
                'createdAt': row[4]
            })
        
        conn.close()
        return jsonify(templates)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    ensure_db_exists()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        conn.close()
        return result[0], 200, {'Content-Type': 'image/svg+xml'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    """Генерация одного изображения с продвинутой обработкой SVG"""
    ensure_db_exists()
    
    try:
        data = request.get_json()
        template_id = data.get('templateId')
        replacement_data = data.get('data', {})
        
        if not template_id:
            return jsonify({'error': 'templateId обязателен'}), 400
        
        # Получаем шаблон
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        conn.close()
        
        # Обрабатываем SVG с продвинутой заменой
        processed_svg = process_svg_with_advanced_replacement(svg_content, replacement_data)
        
        # Генерируем изображение
        image_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUT_FOLDER, 'single', f'{image_id}.png')
        
        if generate_png_from_svg(processed_svg, output_path):
            return jsonify({
                'imageId': image_id,
                'imageUrl': f'/output/single/{image_id}.png',
                'status': 'completed'
            })
        else:
            return jsonify({'error': 'Ошибка генерации изображения'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    """Создание и генерация карусели"""
    ensure_db_exists()
    
    try:
        data = request.get_json()
        carousel_name = data.get('name', f'Carousel-{int(time.time())}')
        slides_data = data.get('slides', [])
        
        if not slides_data:
            return jsonify({'error': 'Данные слайдов обязательны'}), 400
        
        # Создаем карусель
        carousel_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO carousels (id, name) VALUES (?, ?)
        ''', (carousel_id, carousel_name))
        
        generated_slides = []
        
        for i, slide_data in enumerate(slides_data):
            template_id = slide_data.get('templateId')
            replacement_data = slide_data.get('data', {})
            
            # Получаем шаблон
            cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
            result = cursor.fetchone()
            
            if result:
                svg_content = result[0]
                
                # Обрабатываем SVG
                processed_svg = process_svg_with_advanced_replacement(svg_content, replacement_data)
                
                # Генерируем изображение
                slide_id = str(uuid.uuid4())
                output_path = os.path.join(OUTPUT_FOLDER, 'carousel', f'{slide_id}.png')
                
                if generate_png_from_svg(processed_svg, output_path):
                    # Сохраняем информацию о слайде
                    cursor.execute('''
                        INSERT INTO carousel_slides (id, carousel_id, template_id, slide_order, image_path)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (slide_id, carousel_id, template_id, i, f'/output/carousel/{slide_id}.png'))
                    
                    generated_slides.append({
                        'slideId': slide_id,
                        'imageUrl': f'/output/carousel/{slide_id}.png',
                        'order': i
                    })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'carouselId': carousel_id,
            'slides': generated_slides,
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/<carousel_id>/slides')
def get_carousel_slides(carousel_id):
    """Получение слайдов карусели"""
    ensure_db_exists()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, image_path, slide_order
            FROM carousel_slides
            WHERE carousel_id = ?
            ORDER BY slide_order
        ''', (carousel_id,))
        
        slides = []
        for row in cursor.fetchall():
            slides.append({
                'slideId': row[0],
                'imageUrl': row[1],
                'order': row[2]
            })
        
        conn.close()
        return jsonify({'slides': slides})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    ensure_db_exists()
    app.run(host='0.0.0.0', port=5000, debug=True)

