#!/usr/bin/env python3
"""
Отладка удаления шаблонов
"""

import sqlite3
import requests
import json

def check_templates_in_db():
    """Проверяем какие шаблоны есть в базе"""
    
    print("🔍 ПРОВЕРКА ШАБЛОНОВ В БАЗЕ")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Получаем все шаблоны
        cursor.execute('SELECT id, name, category, template_role FROM templates')
        templates = cursor.fetchall()
        
        print(f"📊 Всего шаблонов в базе: {len(templates)}")
        
        if templates:
            print("\n📋 Список шаблонов:")
            for template in templates:
                template_id, name, category, role = template
                print(f"  🎯 {name}")
                print(f"     ID: {template_id}")
                print(f"     Category: {category}")
                print(f"     Role: {role}")
                print()
        
        conn.close()
        return templates
        
    except Exception as e:
        print(f"❌ Ошибка чтения базы: {e}")
        return []

def test_template_deletion_api():
    """Тестируем API удаления шаблонов"""
    
    print("🧪 ТЕСТ API УДАЛЕНИЯ ШАБЛОНОВ")
    print("=" * 50)
    
    # Сначала получаем список шаблонов через API
    try:
        response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
        print(f"📊 API статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"📋 Шаблонов через API: {len(templates)}")
            
            # Ищем тестовые шаблоны
            test_templates = [t for t in templates if 'test' in t.get('name', '').lower()]
            print(f"🧪 Тестовых шаблонов: {len(test_templates)}")
            
            if test_templates:
                print("\n🎯 Тестовые шаблоны:")
                for template in test_templates:
                    print(f"  - {template.get('name')} (ID: {template.get('id')})")
                
                # Пробуем удалить первый тестовый шаблон
                test_template = test_templates[0]
                template_id = test_template.get('id')
                template_name = test_template.get('name')
                
                print(f"\n🗑️ Пробую удалить: {template_name} (ID: {template_id})")
                
                delete_response = requests.delete(
                    f"http://localhost:5000/api/templates/{template_id}/delete",
                    timeout=10
                )
                
                print(f"📊 Удаление статус: {delete_response.status_code}")
                print(f"📋 Ответ: {delete_response.text}")
                
                if delete_response.status_code == 200:
                    print("✅ Шаблон успешно удален через API")
                    
                    # Проверяем что шаблон действительно удален
                    check_response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
                    if check_response.status_code == 200:
                        new_data = check_response.json()
                        new_templates = new_data.get('templates', [])
                        new_count = len([t for t in new_templates if t.get('id') == template_id])
                        
                        if new_count == 0:
                            print("✅ Шаблон действительно удален из списка")
                        else:
                            print("❌ Шаблон все еще в списке!")
                else:
                    print(f"❌ Ошибка удаления: {delete_response.text}")
            else:
                print("ℹ️ Тестовых шаблонов не найдено")
        else:
            print(f"❌ Ошибка получения шаблонов: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")

def check_server_status():
    """Проверяем статус сервера"""
    
    print("🏥 ПРОВЕРКА СЕРВЕРА")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Сервер работает")
            return True
        else:
            print("❌ Сервер не отвечает правильно")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Сервер недоступен: {e}")
        return False

def main():
    """Основная функция отладки"""
    
    print("🔧 ОТЛАДКА УДАЛЕНИЯ ШАБЛОНОВ")
    print("=" * 60)
    
    # Проверяем базу данных
    db_templates = check_templates_in_db()
    
    # Проверяем сервер
    server_ok = check_server_status()
    
    if server_ok:
        # Тестируем API
        test_template_deletion_api()
    else:
        print("⚠️ Сервер не работает, API тесты пропущены")
    
    print("\n📊 ИТОГИ:")
    print(f"📋 Шаблонов в базе: {len(db_templates)}")
    print(f"🏥 Сервер работает: {'✅' if server_ok else '❌'}")

if __name__ == "__main__":
    main()