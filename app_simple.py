"""
УПРОЩЕННАЯ ВЕРСИЯ API БЕЗ CAIROSVG
====================================

Версия для тестирования конвертации SVG в JPG
"""

import os
import re
import uuid
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import base64
import io
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app, origins="*")

# Устанавливаем максимальный размер загружаемого файла (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Конфигурация
DATABASE_PATH = 'templates.db'
OUTPUT_DIR = 'output'
ALLOWED_EXTENSIONS = {'svg'}

# Создаем директории
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('output/single', exist_ok=True)
os.makedirs('output/carousel', exist_ok=True)
os.makedirs('output/previews', exist_ok=True)

def has_dyno_fields_simple(svg_content):
    """Простая проверка наличия dyno полей в SVG"""
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
    """Простое извлечение dyno полей из SVG"""
    fields = set()
    
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
    """Безопасное экранирование для SVG"""
    if not text:
        return text
    
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

def process_svg_simple(svg_content, replacements):
    """Простая обработка SVG с заменами"""
    result = svg_content
    
    for key, value in replacements.items():
        print(f"🔄 Обрабатываю поле: {key} = {value}")
        
        # Безопасное экранирование
        safe_value = safe_escape_for_svg(str(value))
        
        # Проверяем, является ли это изображением
        if 'image' in key.lower() or 'photo' in key.lower() or 'headshot' in key.lower() or 'logo' in key.lower():
            print(f"   🖼️ Обрабатываю изображение: {key}")
            
            # Безопасное экранирование URL
            safe_url = str(value).replace('&', '&amp;')
            
            # Ищем элемент с id="key" для изображения
            element_pattern = f'<[^>]*id="{re.escape(key)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, result)
            
            if match:
                pattern_id = match.group(1)
                print(f"   ✅ Найден pattern: {pattern_id}")
                
                # Ищем image элемент в pattern
                image_pattern = f'<image[^>]*id="[^"]*image[^"]*"[^>]*>'
                image_match = re.search(image_pattern, result)
                
                if image_match:
                    old_image = image_match.group(0)
                    new_image = old_image
                    
                    # Заменяем URL
                    new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
                    new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                    
                    result = result.replace(old_image, new_image)
                    print(f"   ✅ Изображение {key} заменено!")
                else:
                    print(f"   ❌ Image элемент не найден")
            else:
                print(f"   ❌ Элемент с id {key} не найден")
        else:
            # Обработка текстовых полей
            print(f"   📝 Обрабатываю текстовое поле: {key}")
            
            # Ищем элемент с id="key" в SVG
            element_pattern = f'<text[^>]*id="{re.escape(key)}"[^>]*>(.*?)</text>'
            match = re.search(element_pattern, result, re.DOTALL)
            
            if match:
                print(f"   ✅ Найден элемент с id: {key}")
                old_element = match.group(0)
                old_content = match.group(1)
                
                # Заменяем содержимое элемента
                new_content = old_content.replace(f"{{{key}}}", safe_value)
                new_element = old_element.replace(old_content, new_content)
                
                result = result.replace(old_element, new_element)
                print(f"   ✅ Заменено: {key} → {safe_value}")
            else:
                print(f"   ⚠️ Элемент с id='{key}' не найден")
                
                # Fallback: ищем переменные в формате {dyno.field}
                patterns = [
                    f"{{{{{key}}}}}",
                    f"{{{{dyno.{key.replace('dyno.', '')}}}}}",
                    f"{{dyno.{key.replace('dyno.', '')}}}",
                    f"{{{key}}}"
                ]
                
                for pattern in patterns:
                    if pattern in result:
                        result = result.replace(pattern, safe_value)
                        print(f"   ✅ Заменено по fallback: {pattern} → {safe_value}")
                        break
    
    return result

def convert_svg_to_jpg_simple(svg_content, output_path, width=1200, height=800):
    """
    Простая конвертация SVG в JPG через создание изображения с текстом
    """
    try:
        print(f"🖼️ Создаю JPG изображение: {output_path}")
        
        # Создаем изображение с белым фоном
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Добавляем текст с информацией о SVG
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Извлекаем текст из SVG для отображения
        text_content = re.sub(r'<[^>]+>', '', svg_content)
        text_content = text_content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text_content = text_content[:100] + "..." if len(text_content) > 100 else text_content
        
        # Рисуем текст
        draw.text((50, 50), f"SVG Content Preview:", fill='black', font=font)
        draw.text((50, 100), text_content, fill='blue', font=font)
        draw.text((50, height - 100), f"Size: {width}x{height}", fill='gray', font=font)
        
        # Сохраняем как JPG
        img.save(output_path, 'JPEG', quality=95, optimize=True)
        
        print(f"✅ JPG файл создан: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания JPG: {e}")
        return False

def ensure_db_exists():
    """Создает базу данных если не существует"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            template_role TEXT,
            svg_content TEXT NOT NULL,
            dyno_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carousels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            main_template_id TEXT,
            photo_template_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (main_template_id) REFERENCES templates (id),
            FOREIGN KEY (photo_template_id) REFERENCES templates (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Проверяет разрешенное расширение файла"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Создаем тестовые шаблоны
def create_test_templates():
    """Создает тестовые шаблоны в базе данных"""
    ensure_db_exists()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже тестовые шаблоны
    cursor.execute('SELECT id FROM templates WHERE id IN (?, ?)', 
                   ['test-main-template', 'test-photo-template'])
    existing = cursor.fetchall()
    
    if len(existing) < 2:
        # Создаем main template
        main_svg = '''<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
            <rect width="1080" height="1080" fill="#667eea"/>
            <text x="540" y="300" text-anchor="middle" fill="white" font-size="48" font-weight="bold">MAIN TEMPLATE</text>
            <text x="540" y="400" text-anchor="middle" fill="white" font-size="32">{{dyno.propertyAddress}}</text>
            <text x="540" y="500" text-anchor="middle" fill="white" font-size="28">{{dyno.price}}</text>
            <text x="540" y="600" text-anchor="middle" fill="white" font-size="24">{{dyno.agentName}}</text>
            <text x="540" y="700" text-anchor="middle" fill="white" font-size="20">{{dyno.agentPhone}}</text>
        </svg>'''
        
        # Создаем photo template
        photo_svg = '''<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
            <rect width="1080" height="1080" fill="#764ba2"/>
            <rect x="90" y="90" width="900" height="600" fill="#f0f0f0" stroke="#333" stroke-width="2"/>
            <text x="540" y="750" text-anchor="middle" fill="white" font-size="32">{{dyno.propertyAddress}}</text>
            <text x="540" y="800" text-anchor="middle" fill="white" font-size="24">{{dyno.agentName}}</text>
            <text x="540" y="850" text-anchor="middle" fill="white" font-size="20">{{dyno.agentPhone}}</text>
            <text x="540" y="400" text-anchor="middle" fill="#666" font-size="24">PHOTO TEMPLATE</text>
        </svg>'''
        
        # Добавляем main template
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ['test-main-template', 'Test Main Template', 'test', 'main', main_svg, 'dyno.propertyAddress,dyno.price,dyno.agentName,dyno.agentPhone'])
        
        # Добавляем photo template
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, template_role, svg_content, dyno_fields)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ['test-photo-template', 'Test Photo Template', 'test', 'photo', photo_svg, 'dyno.propertyAddress,dyno.agentName,dyno.agentPhone'])
        
        conn.commit()
        print("✅ Тестовые шаблоны созданы")
    
    conn.close()

def create_dynamic_template(template_id, template_role):
    """Создает динамический шаблон на лету, если его нет в базе"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Проверяем, существует ли шаблон
    cursor.execute('SELECT id FROM templates WHERE id = ?', (template_id,))
    if cursor.fetchone():
        conn.close()
        return True
    
    # Создаем динамический шаблон
    if template_role == 'main':
        content = '''<svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white"/>
            <text x="600" y="200" text-anchor="middle" font-size="48" fill="black">Dynamic Main Template</text>
            <text id="dyno.agentName" x="600" y="300" text-anchor="middle" font-size="24" fill="blue">Agent: {dyno.agentName}</text>
            <text id="dyno.propertyAddress" x="600" y="350" text-anchor="middle" font-size="20" fill="green">Address: {dyno.propertyAddress}</text>
            <text id="dyno.price" x="600" y="400" text-anchor="middle" font-size="32" fill="red">Price: {dyno.price}</text>
            <text id="dyno.agentPhone" x="600" y="450" text-anchor="middle" font-size="18" fill="purple">Phone: {dyno.agentPhone}</text>
            <text id="dyno.agentEmail" x="600" y="500" text-anchor="middle" font-size="16" fill="orange">Email: {dyno.agentEmail}</text>
            <text id="dyno.bedrooms" x="600" y="550" text-anchor="middle" font-size="20" fill="brown">Bedrooms: {dyno.bedrooms}</text>
            <text id="dyno.bathrooms" x="600" y="580" text-anchor="middle" font-size="20" fill="brown">Bathrooms: {dyno.bathrooms}</text>
            <text id="dyno.date" x="600" y="620" text-anchor="middle" font-size="18" fill="darkgreen">Date: {dyno.date}</text>
            <text id="dyno.time" x="600" y="650" text-anchor="middle" font-size="18" fill="darkgreen">Time: {dyno.time}</text>
            <text id="dyno.propertyfeatures" x="600" y="680" text-anchor="middle" font-size="14" fill="gray">Features: {dyno.propertyfeatures}</text>
        </svg>'''
        name = f"Dynamic Main Template ({template_id[:8]})"
    else:
        content = '''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="lightblue"/>
            <text x="400" y="200" text-anchor="middle" font-size="36" fill="black">Dynamic Photo Template</text>
            <rect id="dyno.propertyimage1" x="100" y="250" width="600" height="300" fill="url(#property_pattern)"/>
            <defs>
                <pattern id="property_pattern" patternUnits="objectBoundingBox" width="1" height="1">
                    <image id="property_image" href="https://via.placeholder.com/600x300/cccccc/666666?text=Property+Image" preserveAspectRatio="xMidYMid slice"/>
                </pattern>
            </defs>
        </svg>'''
        name = f"Dynamic Photo Template ({template_id[:8]})"
    
    cursor.execute('''
        INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (template_id, name, 'dynamic', template_role, content, 'dyno.propertyimage1'))
    
    conn.commit()
    conn.close()
    print(f"✅ Создан динамический шаблон: {template_id}")
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo_solution.html')
def demo_solution():
    return render_template('demo_solution.html')

@app.route('/test_jpg_urls.html')
def test_jpg_urls():
    return render_template('test_jpg_urls.html')

@app.route('/test_frontend_access.html')
def test_frontend_access():
    return render_template('test_frontend_access.html')

@app.route('/test_fixed_processing.html')
def test_fixed_processing():
    return render_template('test_fixed_processing.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'API работает'})

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/api/generate/carousel', methods=['POST'])
def generate_carousel():
    try:
        data = request.get_json()
        main_template_id = data.get('main_template_id')
        photo_template_id = data.get('photo_template_id')
        replacements = data.get('data', data.get('replacements', {}))
        
        print(f"🔍 Received data: {data}")
        print(f"📋 Replacements: {replacements}")
        
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
        
        # Если шаблоны не найдены, создаем динамические шаблоны
        if not main_result:
            print(f"⚠️ Шаблон {main_template_id} не найден, создаю динамический")
            create_dynamic_template(main_template_id, 'main')
            cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [main_template_id])
            main_result = cursor.fetchone()
        
        if not photo_result:
            print(f"⚠️ Шаблон {photo_template_id} не найден, создаю динамический")
            create_dynamic_template(photo_template_id, 'photo')
            cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [photo_template_id])
            photo_result = cursor.fetchone()
        
        conn.close()
        
        if not main_result or not photo_result:
            return jsonify({'error': 'Не удалось создать один или оба шаблона'}), 500
        
        main_name, main_svg_content = main_result
        photo_name, photo_svg_content = photo_result
        
        # Обрабатываем SVG с заменами
        processed_main_svg = process_svg_simple(main_svg_content, replacements)
        processed_photo_svg = process_svg_simple(photo_svg_content, replacements)
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Сохраняем обработанные SVG и конвертируем в JPG
        main_svg_filename = f"carousel_{carousel_id}_main.svg"
        photo_svg_filename = f"carousel_{carousel_id}_photo.svg"
        main_jpg_filename = f"carousel_{carousel_id}_main.jpg"
        photo_jpg_filename = f"carousel_{carousel_id}_photo.jpg"
        
        # Создаем папку carousel если не существует
        carousel_output_dir = os.path.join(OUTPUT_DIR, 'carousel')
        os.makedirs(carousel_output_dir, exist_ok=True)
        
        # Сохраняем SVG файлы
        main_svg_path = os.path.join(carousel_output_dir, main_svg_filename)
        photo_svg_path = os.path.join(carousel_output_dir, photo_svg_filename)
        
        with open(main_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_main_svg)
        
        with open(photo_svg_path, 'w', encoding='utf-8') as f:
            f.write(processed_photo_svg)
        
        # Конвертируем в JPG
        main_jpg_path = os.path.join(carousel_output_dir, main_jpg_filename)
        photo_jpg_path = os.path.join(carousel_output_dir, photo_jpg_filename)
        
        main_jpg_success = convert_svg_to_jpg_simple(processed_main_svg, main_jpg_path)
        photo_jpg_success = convert_svg_to_jpg_simple(processed_photo_svg, photo_jpg_path)
        
        # Создаем простые массивы URL для фронтенда (предпочитаем JPG)
        image_urls = [
            f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
            f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}'
        ]
        
        response_data = {
            'success': True,
            'carousel_id': carousel_id,
            'main_template_name': main_name,
            'photo_template_name': photo_name,
            'main_url': f'/output/carousel/{main_jpg_filename}' if main_jpg_success else f'/output/carousel/{main_svg_filename}',
            'photo_url': f'/output/carousel/{photo_jpg_filename}' if photo_jpg_success else f'/output/carousel/{photo_svg_filename}',
            'replacements_applied': len(replacements),
            'images': image_urls,
            'slides': image_urls,
            'urls': image_urls,
            'image_url': image_urls[0],
            'data': {'images': image_urls},
            'slides_count': 2,
            'status': 'completed',
            'format': 'jpg' if main_jpg_success and photo_jpg_success else 'svg'
        }
        
        print(f"🔍 /api/generate/carousel response: {response_data}")
        print(f"📊 Images count: {len(image_urls)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации карусели: {str(e)}'}), 500

@app.route('/api/carousels', methods=['GET'])
def get_carousels():
    """Получает список всех каруселей"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, main_template_id, photo_template_id, created_at
            FROM carousels
            ORDER BY created_at DESC
        ''')
        
        carousels = []
        for row in cursor.fetchall():
            carousels.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'main_template_id': row[3],
                'photo_template_id': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'carousels': carousels
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения каруселей: {str(e)}'}), 500

if __name__ == '__main__':
    create_test_templates()
    app.run(debug=True, host='0.0.0.0', port=5001) 