#!/usr/bin/env python3
"""
ЕДИНОЕ ПРИЛОЖЕНИЕ: API + ВЕБ-ИНТЕРФЕЙС
Объединяет API для AgentFlow и веб-интерфейс для управления шаблонами
"""

import os
import sqlite3
import uuid
import json
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, flash
from flask_cors import CORS
import cairosvg
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests
import tempfile
import subprocess

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key-here'

# CORS настройки для AgentFlow
CORS(app, origins=[
    "https://agentflow-marketing-hub.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
], allow_headers=['Content-Type', 'Authorization'], supports_credentials=True)

# Создаем необходимые папки
os.makedirs('output', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('templates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Создаем таблицы
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
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slides (
            id TEXT PRIMARY KEY,
            carousel_id TEXT NOT NULL,
            template_id TEXT NOT NULL,
            slide_number INTEGER NOT NULL,
            replacements TEXT,
            image_path TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carousel_id) REFERENCES carousels (id),
            FOREIGN KEY (template_id) REFERENCES templates (id)
        )
    ''')
    
    # Добавляем начальные шаблоны если их нет
    cursor.execute('SELECT COUNT(*) FROM templates')
    if cursor.fetchone()[0] == 0:
        add_initial_templates(cursor)
    
    conn.commit()
    conn.close()

def add_initial_templates(cursor):
    """Добавляем 4 начальных шаблона"""
    initial_templates = [
        {
            'id': 'open-house-main',
            'name': 'Open House - Main',
            'category': 'open-house',
            'template_role': 'main',
            'svg_content': '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="#f8f9fa"/>
                <text x="400" y="100" text-anchor="middle" font-family="Arial" font-size="48" font-weight="bold" fill="#2d3748">OPEN HOUSE</text>
                <text x="400" y="200" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{dyno.agentName}</text>
                <text x="400" y="250" text-anchor="middle" font-family="Arial" font-size="20" fill="#718096">{dyno.propertyAddress}</text>
                <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="18" fill="#718096">{dyno.price}</text>
                <text x="400" y="400" text-anchor="middle" font-family="Arial" font-size="16" fill="#718096">{dyno.date} at {dyno.time}</text>
                <text x="400" y="500" text-anchor="middle" font-family="Arial" font-size="14" fill="#718096">{dyno.phone}</text>
            </svg>'''
        },
        {
            'id': 'open-house-photo',
            'name': 'Open House - Photo',
            'category': 'open-house',
            'template_role': 'photo',
            'svg_content': '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="#f8f9fa"/>
                <rect x="50" y="50" width="700" height="400" fill="#e2e8f0" stroke="#cbd5e0" stroke-width="2"/>
                <text x="400" y="275" text-anchor="middle" font-family="Arial" font-size="16" fill="#a0aec0">Property Image</text>
                <text x="400" y="500" text-anchor="middle" font-family="Arial" font-size="20" fill="#2d3748">{dyno.agentName}</text>
                <text x="400" y="530" text-anchor="middle" font-family="Arial" font-size="16" fill="#718096">{dyno.phone}</text>
            </svg>'''
        },
        {
            'id': 'sold-main',
            'name': 'Sold - Main',
            'category': 'sold',
            'template_role': 'main',
            'svg_content': '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="#fed7d7"/>
                <text x="400" y="100" text-anchor="middle" font-family="Arial" font-size="48" font-weight="bold" fill="#c53030">SOLD</text>
                <text x="400" y="200" text-anchor="middle" font-family="Arial" font-size="24" fill="#2d3748">{dyno.agentName}</text>
                <text x="400" y="250" text-anchor="middle" font-family="Arial" font-size="20" fill="#4a5568">{dyno.propertyAddress}</text>
                <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="18" fill="#4a5568">{dyno.price}</text>
                <text x="400" y="400" text-anchor="middle" font-family="Arial" font-size="16" fill="#4a5568">Sold on {dyno.date}</text>
                <text x="400" y="500" text-anchor="middle" font-family="Arial" font-size="14" fill="#4a5568">{dyno.phone}</text>
            </svg>'''
        },
        {
            'id': 'sold-photo',
            'name': 'Sold - Photo',
            'category': 'sold',
            'template_role': 'photo',
            'svg_content': '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="800" height="600" fill="#fed7d7"/>
                <rect x="50" y="50" width="700" height="400" fill="#e2e8f0" stroke="#cbd5e0" stroke-width="2"/>
                <text x="400" y="275" text-anchor="middle" font-family="Arial" font-size="16" fill="#a0aec0">Property Image</text>
                <text x="400" y="500" text-anchor="middle" font-family="Arial" font-size="20" fill="#2d3748">{dyno.agentName}</text>
                <text x="400" y="530" text-anchor="middle" font-family="Arial" font-size="16" fill="#4a5568">{dyno.phone}</text>
            </svg>'''
        }
    ]
    
    for template in initial_templates:
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (template['id'], template['name'], template['category'], 
              template['template_role'], template['svg_content']))

# OPTIONS обработка для CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Добавляем CORS заголовки ко всем ответам
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ============= ВЕБ-ИНТЕРФЕЙС =============

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/templates')
def templates_page():
    """Страница управления шаблонами"""
    conn = sqlite3.connect('templates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
    templates = cursor.fetchall()
    conn.close()
    
    return render_template('templates.html', templates=templates)

@app.route('/upload')
def upload_page():
    """Страница загрузки шаблонов"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_template():
    """Загрузка нового шаблона"""
    try:
        name = request.form.get('name')
        category = request.form.get('category')
        template_role = request.form.get('template_role')
        svg_file = request.files.get('svg_file')
        
        if not all([name, category, template_role, svg_file]):
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('upload_page'))
        
        if not svg_file.filename.endswith('.svg'):
            flash('Файл должен быть в формате SVG', 'error')
            return redirect(url_for('upload_page'))
        
        # Читаем содержимое SVG
        svg_content = svg_file.read().decode('utf-8')
        
        # Создаем уникальный ID
        template_id = str(uuid.uuid4())
        
        # Сохраняем в базу данных
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (template_id, name, category, template_role, svg_content))
        
        conn.commit()
        conn.close()
        
        flash(f'Шаблон "{name}" успешно загружен!', 'success')
        return redirect(url_for('templates_page'))
        
    except Exception as e:
        flash(f'Ошибка при загрузке: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/delete/<template_id>', methods=['POST'])
def delete_template(template_id):
    """Удаление шаблона"""
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()
        
        flash('Шаблон успешно удален!', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('templates_page'))

# ============= API ENDPOINTS =============

@app.route('/health')
def health():
    """Проверка статуса API"""
    return jsonify({
        'status': 'healthy',
        'message': 'SVG Template API Server is running',
        'features': [
            'Template Management',
            'Carousel Generation', 
            'Image Processing',
            'Web Interface',
            'CORS Support',
            'Database Storage'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/templates/all-previews')
def get_all_templates():
    """Получение всех шаблонов"""
    conn = sqlite3.connect('templates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, category, template_role, created_at FROM templates')
    templates = cursor.fetchall()
    conn.close()
    
    template_list = []
    for template in templates:
        template_list.append({
            'id': template['id'],
            'name': template['name'],
            'category': template['category'],
            'template_role': template['template_role'],
            'preview_url': f'/api/templates/{template["id"]}/preview',
            'created_at': template['created_at']
        })
    
    return jsonify({'templates': template_list})

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    """Получение превью шаблона"""
    conn = sqlite3.connect('templates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT svg_content FROM templates WHERE id = ?', (template_id,))
    template = cursor.fetchone()
    conn.close()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Возвращаем SVG как изображение
    response = app.response_class(
        template['svg_content'],
        mimetype='image/svg+xml'
    )
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/carousel', methods=['POST'])
def create_carousel():
    """Создание карусели"""
    try:
        data = request.get_json()
        carousel_id = str(uuid.uuid4())
        
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Создаем карусель
        cursor.execute('''
            INSERT INTO carousels (id, name, status)
            VALUES (?, ?, ?)
        ''', (carousel_id, data.get('name', 'Untitled Carousel'), 'pending'))
        
        # Создаем слайды
        for i, slide_data in enumerate(data.get('slides', [])):
            slide_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO slides (id, carousel_id, template_id, slide_number, replacements, image_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (slide_id, carousel_id, slide_data.get('templateId'), i + 1,
                  json.dumps(slide_data.get('replacements', {})),
                  slide_data.get('imagePath'), 'pending'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'carouselId': carousel_id,
            'status': 'created',
            'message': 'Carousel created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/create-and-generate', methods=['POST'])
def create_and_generate_carousel():
    """Создание и генерация карусели"""
    try:
        data = request.get_json()
        carousel_id = str(uuid.uuid4())
        
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Создаем карусель
        cursor.execute('''
            INSERT INTO carousels (id, name, status)
            VALUES (?, ?, ?)
        ''', (carousel_id, data.get('name', 'Untitled Carousel'), 'generating'))
        
        # Создаем слайды
        slide_ids = []
        for i, slide_data in enumerate(data.get('slides', [])):
            slide_id = str(uuid.uuid4())
            slide_ids.append(slide_id)
            cursor.execute('''
                INSERT INTO slides (id, carousel_id, template_id, slide_number, replacements, image_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (slide_id, carousel_id, slide_data.get('templateId'), i + 1,
                  json.dumps(slide_data.get('replacements', {})),
                  slide_data.get('imagePath'), 'generating'))
        
        conn.commit()
        conn.close()
        
        # Запускаем генерацию в отдельном потоке
        threading.Thread(target=generate_carousel_images, args=(carousel_id, slide_ids)).start()
        
        return jsonify({
            'carouselId': carousel_id,
            'status': 'generating',
            'message': 'Carousel generation started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carousel/<carousel_id>/slides')
def get_carousel_slides(carousel_id):
    """Получение слайдов карусели"""
    conn = sqlite3.connect('templates.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, c.status as carousel_status
        FROM slides s
        JOIN carousels c ON s.carousel_id = c.id
        WHERE s.carousel_id = ?
        ORDER BY s.slide_number
    ''', (carousel_id,))
    
    slides = cursor.fetchall()
    conn.close()
    
    if not slides:
        return jsonify({'error': 'Carousel not found'}), 404
    
    slide_list = []
    for slide in slides:
        slide_list.append({
            'id': slide['id'],
            'slideNumber': slide['slide_number'],
            'templateId': slide['template_id'],
            'status': slide['status'],
            'imageUrl': slide['image_url'],
            'createdAt': slide['created_at']
        })
    
    return jsonify({
        'carouselId': carousel_id,
        'status': slides[0]['carousel_status'],
        'slides': slide_list
    })

def generate_carousel_images(carousel_id, slide_ids):
    """Генерация изображений для карусели"""
    try:
        conn = sqlite3.connect('templates.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Создаем папку для карусели
        carousel_dir = os.path.join('output', carousel_id)
        os.makedirs(carousel_dir, exist_ok=True)
        
        for slide_id in slide_ids:
            # Получаем данные слайда
            cursor.execute('''
                SELECT s.*, t.svg_content
                FROM slides s
                JOIN templates t ON s.template_id = t.id
                WHERE s.id = ?
            ''', (slide_id,))
            
            slide = cursor.fetchone()
            if not slide:
                continue
            
            # Обрабатываем SVG
            svg_content = slide['svg_content']
            replacements = json.loads(slide['replacements'] or '{}')
            
            # Заменяем текст в SVG
            for key, value in replacements.items():
                # Поддерживаем разные форматы: {dyno.field}, {field}, dyno.field
                patterns = [f'{{{key}}}', f'{{dyno.{key}}}', f'dyno.{key}']
                for pattern in patterns:
                    svg_content = svg_content.replace(pattern, str(value))
            
            # Генерируем PNG
            try:
                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            except:
                # Fallback через Pillow
                png_data = generate_png_fallback(svg_content)
            
            # Сохраняем файл
            filename = f'slide_{slide["slide_number"]}.png'
            filepath = os.path.join(carousel_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(png_data)
            
            # Обновляем статус слайда
            image_url = f'/output/{carousel_id}/{filename}'
            cursor.execute('''
                UPDATE slides 
                SET status = 'completed', image_url = ?
                WHERE id = ?
            ''', (image_url, slide_id))
        
        # Обновляем статус карусели
        cursor.execute('''
            UPDATE carousels 
            SET status = 'completed'
            WHERE id = ?
        ''', (carousel_id,))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error generating carousel {carousel_id}: {e}")
        # Обновляем статус на ошибку
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE carousels 
            SET status = 'error'
            WHERE id = ?
        ''', (carousel_id,))
        conn.commit()
        conn.close()

def generate_png_fallback(svg_content):
    """Fallback генерация PNG через Pillow"""
    # Простая генерация изображения с текстом
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((400, 300), "Generated Image", font=font, fill='black', anchor='mm')
    
    # Конвертируем в PNG bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

@app.route('/output/<path:filename>')
def serve_output(filename):
    """Отдача сгенерированных файлов"""
    response = send_from_directory('output', filename)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

