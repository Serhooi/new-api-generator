#!/usr/bin/env python3
"""
Минимальный тестовый сервер для отладки
"""

import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Minimal server working'})

@app.route('/api/test-simple', methods=['POST'])
def test_simple():
    """Простой тест без Supabase"""
    
    try:
        # Создаем тестовый SVG
        test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="blue"/>
  <text x="50" y="50" text-anchor="middle" fill="white">OK</text>
</svg>'''
        
        # Генерируем имя файла
        test_filename = f"test_{uuid.uuid4().hex[:8]}.svg"
        
        # Сохраняем локально
        os.makedirs('output/test', exist_ok=True)
        local_path = os.path.join('output/test', test_filename)
        
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(test_svg)
        
        return jsonify({
            'success': True,
            'message': 'Файл сохранен локально',
            'filename': test_filename,
            'path': local_path,
            'url': f'/output/test/{test_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/api/test-supabase-connection', methods=['POST'])
def test_supabase_connection():
    """Тест подключения к Supabase"""
    
    try:
        from supabase import create_client, Client
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return jsonify({
                'success': False,
                'message': 'Переменные окружения не установлены',
                'supabase_url': bool(supabase_url),
                'supabase_key': bool(supabase_key)
            })
        
        # Создаем клиент
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Проверяем доступ к storage
        buckets = supabase.storage.list_buckets()
        
        return jsonify({
            'success': True,
            'message': 'Supabase подключен',
            'url': supabase_url,
            'buckets_count': len(buckets),
            'buckets': [bucket.name for bucket in buckets]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка подключения: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Запуск минимального тестового сервера...")
    app.run(debug=True, host='0.0.0.0', port=5000)