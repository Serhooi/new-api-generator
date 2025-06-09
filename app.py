#!/usr/bin/env python3
"""
ИСПРАВЛЕННЫЙ API С ПРОДВИНУТОЙ ОБРАБОТКОЙ DYNO ПОЛЕЙ
===================================================

Интегрирует продвинутый SVG процессор для правильной замены dyno полей
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
import re
from urllib.parse import urlparse

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your-secret-key-here-change-in-production'

# CORS настройки
CORS(app, 
     origins=['*'],  # Разрешаем все домены для тестирования
     allow_headers=['Content-Type', 'Accept', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True
)

# Создаем необходимые папки
os.makedirs('output', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# ============= ПРОДВИНУТЫЙ SVG ПРОЦЕССОР =============

def download_image(url, max_size=(800, 600)):
    """Загрузка изображения по URL с ресайзом"""
    try:
        print(f"📥 Загружаю изображение: {url}")
        
        # Загружаем изображение
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Открываем изображение
        img = Image.open(io.BytesIO(response.content))
        
        # Конвертируем в RGB если нужно
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Ресайзим если нужно
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        print(f"✅ Изображение загружено и обработано: {img.size}")
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Ошибка загрузки изображения {url}: {e}")
        return None

def wrap_text(text, max_length=30):
    """Автоматический перенос длинного текста"""
    if len(text) <= max_length:
        return text
    
    # Пытаемся разбить по словам
    words = text.split()
    if len(words) <= 1:
        return text
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + len(current_line) <= max_length:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

def process_svg_with_advanced_replacement(svg_content, replacements):
    """ПРОДВИНУТАЯ обработка SVG с заменой текста и изображений"""
    result = svg_content
    
    print("🔄 Обрабатываю SVG шаблон с продвинутой заменой...")
    print(f"📝 Получено замен: {len(replacements)}")
    
    # Обрабатываем замены
    for key, value in replacements.items():
        # Очищаем ключ от dyno. префикса если есть
        clean_key = key.replace('dyno.', '') if key.startswith('dyno.') else key
        
        # Различные форматы переменных которые могут быть в SVG
        patterns = [
            f"{{{{dyno.{clean_key}}}}}",  # {{dyno.field}}
            f"{{{{{key}}}}}",             # {{dyno.field}} или {{field}}
            f"{{{{dyno.{key}}}}}",        # {{dyno.dyno.field}} (двойной префикс)
            f"{{{{{clean_key}}}}}",       # {{field}}
            f"dyno.{clean_key}",          # dyno.field (без скобок)
            f"{key}",                     # прямое имя поля
        ]
        
        # Специальная обработка для изображений
        if any(img_keyword in clean_key.lower() for img_keyword in ['image', 'photo', 'picture', 'img']):
            if isinstance(value, str) and (value.startswith('http') or value.startswith('https')):
                print(f"🖼️ Обрабатываю изображение: {clean_key}")
                # Загружаем изображение
                image_data = download_image(value)
                if image_data:
                    # Заменяем в SVG
                    for pattern in patterns:
                        if pattern in result:
                            # Ищем image элементы или создаем новые
                            result = result.replace(pattern, image_data)
                            print(f"✅ Заменено изображение: {clean_key}")
                else:
                    # Если не удалось загрузить, оставляем placeholder
                    for pattern in patterns:
                        result = result.replace(pattern, f"[Image: {clean_key}]")
            else:
                # Обычная текстовая замена для изображений
                for pattern in patterns:
                    result = result.replace(pattern, str(value))
        else:
            # Обработка текста с переносом для длинных адресов
            processed_value = str(value)
            if 'address' in clean_key.lower() and len(processed_value) > 30:
                processed_value = wrap_text(processed_value, 25)
            
            # Заменяем во всех форматах
            replaced_count = 0
            for pattern in patterns:
                if pattern in result:
                    result = result.replace(pattern, processed_value)
                    replaced_count += 1
            
            if replaced_count > 0:
                print(f"✅ Заменено поле: {clean_key} = {processed_value[:50]}... ({replaced_count} раз)")
    
    # Проверяем остались ли незамененные переменные
    remaining_vars = re.findall(r'\{\{[^}]+\}\}', result)
    if remaining_vars:
        print(f"⚠️ Остались незамененные переменные: {remaining_vars}")
        # Заменяем их на пустые строки
        for var in remaining_vars:
            result = result.replace(var, "")
    
    print("✅ SVG обработка завершена!")
    return result

def generate_png_from_svg_advanced(svg_content):
    """Продвинутая генерация PNG из SVG"""
    try:
        print("🎨 Генерирую PNG из SVG...")
        
        # Пытаемся использовать CairoSVG
        try:
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            print("✅ PNG сгенерирован через CairoSVG")
            return png_data
        except Exception as cairo_error:
            print(f"⚠️ CairoSVG ошибка: {cairo_error}")
            
            # Fallback через Pillow
            print("🔄 Использую Pillow fallback...")
            img = Image.new('RGB', (1080, 1350), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Извлекаем текст из SVG для отображения
            text_matches = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
            y_pos = 100
            for text in text_matches[:10]:  # Максимум 10 строк
                draw.text((50, y_pos), text, font=font, fill='black')
                y_pos += 40
            
            # Конвертируем в PNG bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            print("✅ PNG сгенерирован через Pillow fallback")
            return img_bytes.getvalue()
            
    except Exception as e:
        print(f"❌ Ошибка генерации PNG: {e}")
        # Создаем простое изображение с ошибкой
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Error: {str(e)}", fill='red')
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

# ============= БАЗА ДАННЫХ =============

def ensure_db_exists():
    """ПРИНУДИТЕЛЬНАЯ инициализация базы данных при каждом обращении"""
    try:
        conn = sqlite3.connect('templates.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Проверяем существование таблицы templates
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='templates'
        """)
        
        if not cursor.fetchone():
            print("Таблица templates не найдена. Создаем...")
            
            # Создаем таблицы
            cursor.execute('''
                CREATE TABLE templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    template_role TEXT NOT NULL,
                    svg_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE carousels (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE slides (
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
            
            # Добавляем начальные шаблоны С DYNO ПОЛЯМИ
            add_initial_templates_with_dyno_fields(cursor)
            print("Начальные шаблоны с dyno полями добавлены")
            
            conn.commit()
            print("База данных создана успешно!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка создания БД: {e}")
        return False

def add_initial_templates_with_dyno_fields(cursor):
    """Добавляем начальные шаблоны С ПРАВИЛЬНЫМИ DYNO ПОЛЯМИ"""
    initial_templates = [
        {
            'id': 'open-house-main-dyno',
            'name': 'Open House - Main (with dyno)',
            'category': 'open-house',
            'template_role': 'main',
            'svg_content': '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
                <rect width="1080" height="1350" fill="#f8f9fa"/>
                <text x="540" y="150" text-anchor="middle" font-family="Arial" font-size="72" font-weight="bold" fill="#2d3748">OPEN HOUSE</text>
                <text x="540" y="250" text-anchor="middle" font-family="Arial" font-size="36" fill="#4a5568">{{dyno.agentName}}</text>
                <text x="540" y="320" text-anchor="middle" font-family="Arial" font-size="28" fill="#718096">{{dyno.propertyAddress}}</text>
                <text x="540" y="400" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#2d3748">{{dyno.price}}</text>
                <text x="270" y="500" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.bedrooms}} bed</text>
                <text x="540" y="500" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.bathrooms}} bath</text>
                <text x="810" y="500" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.sqft}} sqft</text>
                <text x="540" y="600" text-anchor="middle" font-family="Arial" font-size="28" fill="#2d3748">{{dyno.openHouseDate}}</text>
                <text x="540" y="650" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.openHouseTime}}</text>
                <text x="540" y="750" text-anchor="middle" font-family="Arial" font-size="20" fill="#718096">{{dyno.agentPhone}}</text>
                <text x="540" y="800" text-anchor="middle" font-family="Arial" font-size="18" fill="#718096">{{dyno.agentEmail}}</text>
                <rect x="90" y="900" width="900" height="400" fill="#e2e8f0" stroke="#cbd5e0" stroke-width="2"/>
                <text x="540" y="1120" text-anchor="middle" font-family="Arial" font-size="24" fill="#a0aec0">{{dyno.propertyImage}}</text>
            </svg>'''
        },
        {
            'id': 'open-house-photo-dyno',
            'name': 'Open House - Photo (with dyno)',
            'category': 'open-house',
            'template_role': 'photo',
            'svg_content': '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
                <rect width="1080" height="1350" fill="#f8f9fa"/>
                <rect x="90" y="90" width="900" height="600" fill="#e2e8f0" stroke="#cbd5e0" stroke-width="2"/>
                <text x="540" y="410" text-anchor="middle" font-family="Arial" font-size="24" fill="#a0aec0">{{dyno.propertyImage}}</text>
                <text x="540" y="800" text-anchor="middle" font-family="Arial" font-size="48" font-weight="bold" fill="#2d3748">{{dyno.price}}</text>
                <text x="540" y="870" text-anchor="middle" font-family="Arial" font-size="28" fill="#4a5568">{{dyno.propertyAddress}}</text>
                <text x="270" y="950" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.bedrooms}} bed</text>
                <text x="540" y="950" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.bathrooms}} bath</text>
                <text x="810" y="950" text-anchor="middle" font-family="Arial" font-size="24" fill="#4a5568">{{dyno.sqft}} sqft</text>
                <text x="540" y="1100" text-anchor="middle" font-family="Arial" font-size="32" fill="#2d3748">{{dyno.agentName}}</text>
                <text x="540" y="1150" text-anchor="middle" font-family="Arial" font-size="20" fill="#718096">{{dyno.agentPhone}}</text>
                <text x="540" y="1200" text-anchor="middle" font-family="Arial" font-size="18" fill="#718096">{{dyno.agentEmail}}</text>
            </svg>'''
        }
    ]
    
    for template in initial_templates:
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', (template['id'], template['name'], template['category'], 
              template['template_role'], template['svg_content']))

# ============= ОСТАЛЬНОЙ КОД API =============
# (Здесь будет весь остальной код из DATABASE_FIXED_app.py, но с заменой функций обработки SVG)

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
    try:
        ensure_db_exists()
        return render_template('index.html')
    except Exception as e:
        return f"Ошибка загрузки главной страницы: {e}", 500

@app.route('/templates')
def templates_page():
    """Страница управления шаблонами"""
    try:
        if not ensure_db_exists():
            return "Ошибка инициализации базы данных", 500
        
        conn = sqlite3.connect('templates.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
        templates = cursor.fetchall()
        conn.close()
        
        return render_template('templates.html', templates=templates)
    except Exception as e:
        return f"Ошибка загрузки шаблонов: {e}", 500

@app.route('/upload')
def upload_page():
    """Страница загрузки шаблонов"""
    try:
        ensure_db_exists()
        return render_template('upload.html')
    except Exception as e:
        return f"Ошибка загрузки страницы: {e}", 500

# ============= API ENDPOINTS =============

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        db_status = "healthy" if ensure_db_exists() else "error"
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'version': '3.0-advanced-dyno',
            'features': [
                'Template management',
                'Carousel creation',
                'Single image generation',
                'Advanced dyno field replacement',
                'Image URL processing',
                'Text wrapping',
                'CORS support',
                'File serving',
                'Database integration',
                'Auto DB initialization'
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/templates/all-previews')
def get_all_templates():
    """Получение всех шаблонов с превью"""
    try:
        if not ensure_db_exists():
            return jsonify({'error': 'Database initialization failed'}), 500
        
        conn = sqlite3.connect('templates.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates ORDER BY category, template_role, name')
        templates = cursor.fetchall()
        conn.close()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template['id'],
                'name': template['name'],
                'category': template['category'],
                'templateRole': template['template_role'],
                'previewUrl': f'/api/templates/{template["id"]}/preview',
                'createdAt': template['created_at']
            })
        
        return jsonify(template_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# SINGLE IMAGE GENERATION С ПРОДВИНУТОЙ ОБРАБОТКОЙ
@app.route('/api/image/generate', methods=['POST'])
def generate_single_image():
    """Генерация одного изображения из шаблона С ПРОДВИНУТОЙ ОБРАБОТКОЙ DYNO ПОЛЕЙ"""
    try:
        if not ensure_db_exists():
            return jsonify({'error': 'Database initialization failed'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        template_id = data.get('templateId')
        replacements = data.get('data', {})
        
        if not template_id:
            return jsonify({'error': 'templateId is required'}), 400
        
        print(f"🎯 Генерирую изображение для шаблона: {template_id}")
        print(f"📝 Замены: {replacements}")
        
        # Получаем шаблон из базы данных
        conn = sqlite3.connect('templates.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        template = cursor.fetchone()
        conn.close()
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        # ПРОДВИНУТАЯ обработка SVG
        svg_content = template['svg_content']
        processed_svg = process_svg_with_advanced_replacement(svg_content, replacements)
        
        # Генерируем уникальный ID для изображения
        image_id = str(uuid.uuid4())
        
        # Создаем папку для изображения
        image_dir = os.path.join('output', 'single')
        os.makedirs(image_dir, exist_ok=True)
        
        # ПРОДВИНУТАЯ генерация PNG
        png_data = generate_png_from_svg_advanced(processed_svg)
        
        # Сохраняем файл
        filename = f'{image_id}.png'
        filepath = os.path.join(image_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(png_data)
        
        # Возвращаем URL изображения
        image_url = f'/output/single/{filename}'
        
        print(f"✅ Изображение сгенерировано: {image_url}")
        
        return jsonify({
            'imageId': image_id,
            'imageUrl': image_url,
            'templateId': template_id,
            'status': 'completed',
            'createdAt': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    """Отдача сгенерированных файлов"""
    try:
        response = send_from_directory('output', filename)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Обработка ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # ПРИНУДИТЕЛЬНАЯ инициализация при запуске
    print("🚀 Запуск API с продвинутой обработкой dyno полей...")
    ensure_db_exists()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

