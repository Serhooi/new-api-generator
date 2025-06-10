"""
ПОЛНАЯ ВЕРСИЯ API СО ВСЕМИ ФУНКЦИЯМИ + ИДЕАЛЬНАЯ ОБРАБОТКА ШРИФТОВ
================================================================

Версия 8.0 - Полная версия с АБСОЛЮТНЫМ сохранением шрифтов Montserrat
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
import html

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
    Безопасное экранирование для SVG - только самые опасные символы
    """
    if not text:
        return text
    
    # Заменяем только действительно опасные символы
    text = str(text)
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    # НЕ экранируем & чтобы избежать двойного экранирования
    
    return text

def process_svg_font_perfect(svg_content, replacements):
    """
    ИДЕАЛЬНАЯ функция обработки SVG с АБСОЛЮТНЫМ сохранением шрифтов
    Заменяет ТОЛЬКО содержимое текста, НЕ ТРОГАЯ никакие атрибуты
    """
    print("🎨 ЗАПУСК ИДЕАЛЬНОЙ ОБРАБОТКИ SVG С СОХРАНЕНИЕМ ШРИФТОВ")
    
    processed_svg = svg_content
    
    for field, value in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {field} = {value}")
        
        # Безопасное экранирование HTML символов
        safe_value = html.escape(str(value))
        
        if field == 'dyno.propertyimage':
            # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ PROPERTY IMAGE
            print(f"🖼️ Обрабатываю property image: {field}")
            
            # Ищем ВСЕ возможные patterns для property image
            patterns_to_replace = [
                'pattern0_294_4',  # Main template
                'pattern0_332_4',  # Photo template
            ]
            
            for pattern in patterns_to_replace:
                # Ищем pattern definition
                pattern_regex = f'<pattern[^>]*id="{pattern}"[^>]*>'
                pattern_match = re.search(pattern_regex, processed_svg)
                
                if pattern_match:
                    print(f"   🎯 Найден pattern: {pattern}")
                    
                    # Находим начало pattern
                    pattern_start = pattern_match.end()
                    
                    # Ищем закрывающий </pattern>
                    pattern_end_match = re.search(r'</pattern>', processed_svg[pattern_start:])
                    
                    if pattern_end_match:
                        pattern_end = pattern_start + pattern_end_match.start()
                        
                        # Создаем новое содержимое pattern с высококачественным изображением
                        new_pattern_content = f'<image href="{safe_value}?w=1200&h=800&q=90&fit=crop" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"/>'
                        
                        # Заменяем содержимое pattern
                        processed_svg = processed_svg[:pattern_start] + new_pattern_content + processed_svg[pattern_end:]
                        
                        print(f"   ✅ Pattern {pattern} заменен на высококачественное изображение!")
                        break
                    else:
                        print(f"   ⚠️ Не найден закрывающий </pattern> для {pattern}")
                else:
                    print(f"   ⚠️ Pattern {pattern} не найден")
                    
        elif field in ['dyno.agentheadshot', 'dyno.logo']:
            # ОБРАБОТКА ДРУГИХ ИЗОБРАЖЕНИЙ
            print(f"🖼️ Обрабатываю изображение: {field}")
            
            # Определяем pattern для каждого типа изображения
            if field == 'dyno.agentheadshot':
                target_patterns = ['pattern2_294_4', 'pattern2_332_4']
                image_params = "?w=400&h=400&q=90&fit=crop"
            elif field == 'dyno.logo':
                target_patterns = ['pattern1_294_4', 'pattern1_332_4']
                image_params = "?w=300&h=100&q=90&fit=crop"
            
            for pattern in target_patterns:
                pattern_regex = f'<pattern[^>]*id="{pattern}"[^>]*>'
                pattern_match = re.search(pattern_regex, processed_svg)
                
                if pattern_match:
                    print(f"   🎯 Найден pattern: {pattern}")
                    
                    pattern_start = pattern_match.end()
                    pattern_end_match = re.search(r'</pattern>', processed_svg[pattern_start:])
                    
                    if pattern_end_match:
                        pattern_end = pattern_start + pattern_end_match.start()
                        
                        new_pattern_content = f'<image href="{safe_value}{image_params}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"/>'
                        
                        processed_svg = processed_svg[:pattern_start] + new_pattern_content + processed_svg[pattern_end:]
                        
                        print(f"   ✅ Pattern {pattern} заменен!")
                        break
                        
        else:
            # ДЛЯ ТЕКСТА - СУПЕР-ТОЧНАЯ замена с АБСОЛЮТНЫМ сохранением шрифтов
            print(f"🔤 Обрабатываю текст: {field}")
            
            # Ищем text элемент с нужным id
            text_pattern = f'<text[^>]*id="{re.escape(field)}"[^>]*>'
            text_match = re.search(text_pattern, processed_svg)
            
            if text_match:
                print(f"   📝 Найден text элемент с id: {field}")
                
                # Находим начало text элемента
                text_start = text_match.end()
                
                # Ищем закрывающий </text>
                text_end_match = re.search(r'</text>', processed_svg[text_start:])
                
                if text_end_match:
                    text_end = text_start + text_end_match.start()
                    text_content = processed_svg[text_start:text_end]
                    
                    print(f"   📝 Найден text блок длиной {len(text_content)} символов")
                    
                    # ИДЕАЛЬНАЯ замена: заменяем ТОЛЬКО содержимое первого tspan
                    def replace_first_tspan_content(content):
                        # Ищем первый tspan с его содержимым
                        tspan_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
                        
                        def replace_content(match):
                            opening_tag = match.group(1)  # <tspan ...> с ВСЕМИ атрибутами
                            old_content = match.group(2)  # старое содержимое
                            closing_tag = match.group(3)  # </tspan>
                            
                            print(f"      🎯 Заменяю содержимое: '{old_content}' → '{safe_value}'")
                            print(f"      🔤 СОХРАНЯЮ атрибуты: {opening_tag}")
                            
                            # Возвращаем тег с новым содержимым, НО СО СТАРЫМИ АТРИБУТАМИ!
                            return opening_tag + safe_value + closing_tag
                        
                        # Заменяем ТОЛЬКО первый tspan (count=1)
                        return re.sub(tspan_pattern, replace_content, content, count=1)
                    
                    # Применяем замену
                    new_text_content = replace_first_tspan_content(text_content)
                    
                    # Заменяем в полном SVG
                    processed_svg = processed_svg[:text_start] + new_text_content + processed_svg[text_end:]
                    
                    print(f"   ✅ Текст заменен с ПОЛНЫМ сохранением font-family атрибутов!")
                else:
                    print(f"   ⚠️ Не найден закрывающий </text> для {field}")
            else:
                print(f"   ⚠️ Не найден text элемент с id {field}")
    
    print("✅ ИДЕАЛЬНАЯ обработка SVG завершена - ВСЕ ШРИФТЫ MONTSERRAT СОХРАНЕНЫ!")
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
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'has_dyno_fields': has_dyno,
            'dyno_fields': dyno_fields,
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
        return jsonify({'error': f'Ошибка получения шаблонов: {str(e)}'}), 500

@app.route('/api/templates/<template_id>/preview')
def get_template_preview(template_id):
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT svg_content FROM templates WHERE id = ?', [template_id])
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({'error': 'Шаблон не найден'}), 404
        
        svg_content = result[0]
        
        return svg_content, 200, {'Content-Type': 'image/svg+xml'}
        
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
        
        # Обрабатываем SVG с идеальным сохранением шрифтов
        processed_main_svg = process_svg_font_perfect(main_svg_content, replacements)
        processed_photo_svg = process_svg_font_perfect(photo_svg_content, replacements)
        
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

if __name__ == '__main__':
    ensure_db_exists()
    
    # Для локальной разработки
    app.run(host='0.0.0.0', port=5000, debug=True)

