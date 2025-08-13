#!/usr/bin/env python3
"""
Исправленная версия приложения с рабочим Supabase
"""

import os
import sqlite3
import uuid
import re
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests
from supabase import create_client, Client

# Инициализация Flask
app = Flask(__name__)
CORS(app)

# Устанавливаем максимальный размер загружаемого файла (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

# Конфигурация
DATABASE_PATH = 'templates.db'
OUTPUT_DIR = 'output'
ALLOWED_EXTENSIONS = {'svg'}

# Supabase конфигурация - используем service role для загрузки
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

# Инициализация Supabase клиента с service role для загрузки файлов
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print(f"✅ Supabase клиент инициализирован с service role: {SUPABASE_URL}")
    except Exception as e:
        print(f"❌ Ошибка инициализации Supabase: {e}")
        supabase = None
else:
    print("ℹ️ Supabase переменные не установлены, работаем локально")

# Создаем директории
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('output/single', exist_ok=True)
os.makedirs('output/carousel', exist_ok=True)
os.makedirs('output/previews', exist_ok=True)

def upload_to_supabase_storage(file_content, filename, folder="carousel"):
    """Загружает файл в Supabase Storage"""
    
    if not supabase:
        print("❌ Supabase клиент не инициализирован")
        return None
    
    try:
        # Создаем путь к файлу
        file_path = f"{folder}/{filename}"
        
        # Определяем content-type
        if filename.lower().endswith('.svg'):
            file_data = file_content.encode('utf-8') if isinstance(file_content, str) else file_content
            content_type = "image/svg+xml"
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            file_data = file_content
            content_type = "image/jpeg"
        else:
            file_data = file_content.encode('utf-8') if isinstance(file_content, str) else file_content
            content_type = "application/octet-stream"
        
        print(f"📤 Загружаю в Supabase: {file_path}")
        
        # Загружаем файл в carousel-assets bucket
        result = supabase.storage.from_("carousel-assets").upload(
            path=file_path,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        # Получаем публичный URL
        public_url = supabase.storage.from_("carousel-assets").get_public_url(file_path)
        
        print(f"✅ Файл загружен в Supabase: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ Ошибка загрузки в Supabase: {e}")
        return None

def save_file_locally_or_supabase(content, filename, folder="carousel"):
    """Сохраняет файл локально или в Supabase"""
    
    # Если есть Supabase - используем его
    if supabase:
        return upload_to_supabase_storage(content, filename, folder)
    else:
        # Локально - сохраняем в файл
        local_path = os.path.join(OUTPUT_DIR, folder, filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            mode = 'wb' if isinstance(content, bytes) else 'w'
            encoding = None if isinstance(content, bytes) else 'utf-8'
            
            with open(local_path, mode, encoding=encoding) as f:
                f.write(content)
            print(f"✅ Файл сохранен локально: {local_path}")
            return f"/output/{folder}/{filename}"
        except Exception as e:
            print(f"❌ Ошибка сохранения локально: {e}")
            return None

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok", 
        "message": "API работает",
        "supabase_connected": supabase is not None,
        "supabase_url": SUPABASE_URL if SUPABASE_URL else "не установлен"
    })

@app.route('/api/test-upload', methods=['POST'])
def test_upload():
    """Тестовый endpoint для проверки загрузки"""
    
    try:
        # Создаем тестовый SVG
        test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="300" fill="purple"/>
  <text x="150" y="150" text-anchor="middle" fill="white" font-size="24">API TEST</text>
</svg>'''
        
        # Генерируем уникальное имя файла
        test_filename = f"api_test_{uuid.uuid4().hex[:8]}.svg"
        
        # Загружаем файл
        url = save_file_locally_or_supabase(test_svg, test_filename, "test")
        
        if url:
            return jsonify({
                'success': True,
                'message': 'Тестовый файл загружен',
                'filename': test_filename,
                'url': url
            })
        else:
            return jsonify({'error': 'Не удалось загрузить файл'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/generate/carousel', methods=['POST'])
def generate_carousel():
    """Простой endpoint для генерации карусели"""
    
    try:
        data = request.get_json()
        print(f"📥 Получен запрос: {data}")
        
        # Создаем тестовые SVG файлы
        main_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="400" fill="blue"/>
  <text x="200" y="200" text-anchor="middle" fill="white" font-size="32">MAIN SLIDE</text>
</svg>'''
        
        photo_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="400" fill="red"/>
  <text x="200" y="200" text-anchor="middle" fill="white" font-size="32">PHOTO SLIDE</text>
</svg>'''
        
        # Генерируем уникальный ID карусели
        carousel_id = str(uuid.uuid4())
        
        # Имена файлов
        main_filename = f"carousel_{carousel_id}_main.svg"
        photo_filename = f"carousel_{carousel_id}_photo.svg"
        
        # Загружаем файлы
        main_url = save_file_locally_or_supabase(main_svg, main_filename, "carousel")
        photo_url = save_file_locally_or_supabase(photo_svg, photo_filename, "carousel")
        
        if not main_url or not photo_url:
            return jsonify({'error': 'Ошибка сохранения файлов'}), 500
        
        # Формируем ответ в формате который ожидает фронтенд
        response_data = {
            'success': True,
            'carousel_id': carousel_id,
            'images': [main_url, photo_url],  # Простой массив URL
            'slides': [main_url, photo_url],  # Дублируем для совместимости
            'main_url': main_url,
            'photo_url': photo_url,
            'status': 'completed',
            'slides_count': 2
        }
        
        print(f"✅ Ответ: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500

# Статические файлы
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    print("🚀 Запуск исправленного сервера...")
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Service Key: {'установлен' if SUPABASE_SERVICE_KEY else 'не установлен'}")
    print(f"🔗 Supabase клиент: {'✅ подключен' if supabase else '❌ не подключен'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)