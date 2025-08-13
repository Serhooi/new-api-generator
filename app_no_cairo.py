#!/usr/bin/env python3
"""
Временная версия app.py без Cairo для тестирования Supabase
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

# Supabase конфигурация
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')

# Инициализация Supabase клиента
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase клиент инициализирован: {SUPABASE_URL}")
    except Exception as e:
        print(f"❌ Ошибка инициализации Supabase: {e}")
        supabase = None
else:
    print("ℹ️ Supabase переменные не установлены, работаем локально")

# Создаем директории (для локальной разработки)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs('output/single', exist_ok=True)
os.makedirs('output/carousel', exist_ok=True)
os.makedirs('output/previews', exist_ok=True)

def upload_to_supabase_storage(file_content, filename, folder="generated"):
    """
    Загружает файл в Supabase Storage
    """
    if not supabase:
        print("❌ Supabase клиент не инициализирован")
        return None
    
    try:
        # Создаем путь к файлу
        file_path = f"{folder}/{filename}"
        
        # Определяем content-type и обработку файла
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            # JPG файл - передаем bytes как есть
            file_data = file_content
            content_type = "image/jpeg"
        elif filename.lower().endswith('.png'):
            # PNG файл - передаем bytes как есть
            file_data = file_content
            content_type = "image/png"
        else:
            # SVG или текстовый файл - кодируем в UTF-8
            file_data = file_content.encode('utf-8') if isinstance(file_content, str) else file_content
            content_type = "image/svg+xml"
        
        # Загружаем файл в Storage
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
    """
    Сохраняет файл локально (для разработки) или в Supabase (для продакшена)
    """
    # Определяем, работаем ли мы на Render или есть Supabase
    is_render = os.environ.get('RENDER', False) or bool(os.environ.get('SUPABASE_URL'))
    
    if is_render and supabase:
        # На Render - загружаем в Supabase
        return upload_to_supabase_storage(content, filename, folder)
    else:
        # Локально - сохраняем в файл
        local_path = os.path.join(OUTPUT_DIR, folder, filename)
        try:
            # Определяем режим записи в зависимости от типа контента
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

@app.route('/api/test-supabase', methods=['POST'])
def test_supabase():
    """Тестовый endpoint для проверки Supabase"""
    
    if not supabase:
        return jsonify({'error': 'Supabase не инициализирован'}), 500
    
    try:
        # Создаем тестовый SVG
        test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="red"/>
  <text x="50" y="50" text-anchor="middle" fill="white">TEST</text>
</svg>'''
        
        # Генерируем уникальное имя файла
        test_filename = f"test_{uuid.uuid4().hex[:8]}.svg"
        
        # Загружаем в Supabase
        url = save_file_locally_or_supabase(test_svg, test_filename, "test")
        
        if url:
            return jsonify({
                'success': True,
                'message': 'Тестовый файл загружен в Supabase',
                'filename': test_filename,
                'url': url
            })
        else:
            return jsonify({'error': 'Не удалось загрузить файл'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Ошибка тестирования Supabase: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Запуск тестового сервера без Cairo...")
    print(f"🌐 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 Supabase Key: {'установлен' if SUPABASE_KEY else 'не установлен'}")
    print(f"🔗 Supabase клиент: {'✅ подключен' if supabase else '❌ не подключен'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)