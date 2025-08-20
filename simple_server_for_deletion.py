#!/usr/bin/env python3
"""
Простой сервер для тестирования удаления шаблонов (без Cairo)
"""

import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_PATH = 'templates.db'

def ensure_db_exists():
    """Создает базу данных если не существует"""
    if not os.path.exists(DATABASE_PATH):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                template_role TEXT,
                svg_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Simple server working"})

@app.route('/api/templates/all-previews')
def get_all_templates():
    """Получает все шаблоны"""
    try:
        ensure_db_exists()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, category, template_role, created_at 
            FROM templates 
            ORDER BY created_at DESC
        ''')
        
        templates = []
        for row in cursor.fetchall():
            template_id, name, category, role, created_at = row
            templates.append({
                'id': template_id,
                'name': name,
                'category': category,
                'template_role': role,
                'preview_url': f'/output/previews/{template_id}_preview.png',
                'created_at': created_at
            })
        
        conn.close()
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка получения шаблонов: {str(e)}'}), 500

@app.route('/api/templates/<template_id>/delete', methods=['DELETE'])
def delete_template(template_id):
    """Удаляет шаблон"""
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
        
        print(f"🗑️ Удаляю шаблон: {template_name} (ID: {template_id})")
        
        # Удаляем шаблон
        cursor.execute('DELETE FROM templates WHERE id = ?', [template_id])
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ Удалено строк: {rows_affected}")
        
        return jsonify({
            'success': True,
            'message': f'Шаблон "{template_name}" успешно удален',
            'rows_affected': rows_affected
        })
        
    except Exception as e:
        print(f"❌ Ошибка удаления: {e}")
        return jsonify({'error': f'Ошибка удаления: {str(e)}'}), 500

@app.route('/api/templates/delete-all-test', methods=['DELETE'])
def delete_all_test_templates():
    """Удаляет все тестовые шаблоны"""
    try:
        ensure_db_exists()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Удаляем все шаблоны с category='test' или содержащие 'test' в названии
        cursor.execute('''
            DELETE FROM templates 
            WHERE category = 'test' OR LOWER(name) LIKE '%test%'
        ''')
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🗑️ Удалено тестовых шаблонов: {rows_affected}")
        
        return jsonify({
            'success': True,
            'message': f'Удалено {rows_affected} тестовых шаблонов',
            'rows_affected': rows_affected
        })
        
    except Exception as e:
        print(f"❌ Ошибка удаления: {e}")
        return jsonify({'error': f'Ошибка удаления: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Запуск простого сервера для удаления шаблонов...")
    app.run(debug=True, host='0.0.0.0', port=5000)