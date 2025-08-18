#!/usr/bin/env python3
"""
Тест исправления удаления шаблонов
"""

import sqlite3
import requests

def create_test_template():
    """Создаем тестовый шаблон для удаления"""
    
    print("🧪 СОЗДАНИЕ ТЕСТОВОГО ШАБЛОНА")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Создаем тестовый шаблон
        test_template = {
            'id': 'test-deletion-template',
            'name': 'Test Deletion Template',
            'category': 'test',
            'template_role': 'main',
            'svg_content': '<svg><rect width="100" height="100" fill="red"/></svg>'
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            test_template['id'],
            test_template['name'], 
            test_template['category'],
            test_template['template_role'],
            test_template['svg_content']
        ])
        
        conn.commit()
        conn.close()
        
        print(f"✅ Создан тестовый шаблон: {test_template['name']}")
        return test_template['id']
        
    except Exception as e:
        print(f"❌ Ошибка создания: {e}")
        return None

def test_web_deletion(template_id):
    """Тестируем удаление через веб-форму"""
    
    print(f"\n🗑️ ТЕСТ УДАЛЕНИЯ ЧЕРЕЗ ВЕБ-ФОРМУ")
    print("=" * 50)
    
    try:
        # Отправляем POST запрос как форма
        response = requests.post(
            f"http://localhost:5000/delete/{template_id}",
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📋 Ответ: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Запрос прошел успешно")
            
            # Проверяем что шаблон удален из базы
            conn = sqlite3.connect('templates.db')
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM templates WHERE id = ?', [template_id])
            result = cursor.fetchone()
            conn.close()
            
            if result is None:
                print("✅ Шаблон успешно удален из базы")
                return True
            else:
                print("❌ Шаблон все еще в базе")
                return False
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def test_api_deletion():
    """Тестируем удаление через API"""
    
    print(f"\n🔌 ТЕСТ УДАЛЕНИЯ ЧЕРЕЗ API")
    print("=" * 40)
    
    # Создаем еще один тестовый шаблон
    template_id = 'test-api-deletion'
    
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, template_role, svg_content)
            VALUES (?, ?, ?, ?, ?)
        ''', [template_id, 'Test API Deletion', 'test', 'main', '<svg></svg>'])
        
        conn.commit()
        conn.close()
        
        print(f"✅ Создан шаблон для API теста: {template_id}")
        
        # Тестируем API удаление
        response = requests.delete(
            f"http://localhost:5000/api/templates/{template_id}/delete",
            timeout=10
        )
        
        print(f"📊 API статус: {response.status_code}")
        print(f"📋 API ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ API удаление работает")
            return True
        else:
            print(f"❌ API ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка API теста: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🔧 ТЕСТ ИСПРАВЛЕНИЯ УДАЛЕНИЯ ШАБЛОНОВ")
    print("=" * 60)
    
    # Проверяем что сервер работает
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Сервер не работает")
            return
    except:
        print("❌ Сервер недоступен")
        return
    
    print("✅ Сервер работает")
    
    # Создаем тестовый шаблон
    template_id = create_test_template()
    
    if template_id:
        # Тестируем веб-удаление
        web_success = test_web_deletion(template_id)
        
        # Тестируем API удаление
        api_success = test_api_deletion()
        
        print(f"\n📊 ИТОГИ:")
        print(f"🌐 Веб-форма удаление: {'✅' if web_success else '❌'}")
        print(f"🔌 API удаление: {'✅' if api_success else '❌'}")
        
        if web_success and api_success:
            print("🎉 Удаление шаблонов работает!")
        else:
            print("⚠️ Есть проблемы с удалением")

if __name__ == "__main__":
    main()