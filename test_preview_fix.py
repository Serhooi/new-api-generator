#!/usr/bin/env python3
"""
Быстрый тест исправленных превью
"""

import requests
import json

def test_preview_api():
    """Тестируем API превью"""
    
    print("🧪 ТЕСТ ИСПРАВЛЕННЫХ ПРЕВЬЮ")
    print("=" * 50)
    
    # Запускаем сервер на порту 5002
    import subprocess
    import time
    import os
    
    # Устанавливаем переменные окружения
    env = os.environ.copy()
    env['SUPABASE_URL'] = 'https://vahgmyuowsilbxqdjjii.supabase.co'
    env['SUPABASE_SERVICE_ROLE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhaGdteXVvd3NpbGJ4cWRqamlpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTI1MDIxOSwiZXhwIjoyMDYwODI2MjE5fQ.7pfeWV0cnKALRb1IGYrhUQL68ggywFG6MetKc8DPvbE'
    
    print("🚀 Запускаю сервер на порту 5002...")
    
    # Изменяем порт в app.py временно
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Заменяем порт
    content_with_port = content.replace("app.run(debug=True, host='0.0.0.0', port=5000)", 
                                       "app.run(debug=True, host='0.0.0.0', port=5002)")
    
    with open('app_test.py', 'w') as f:
        f.write(content_with_port)
    
    # Запускаем сервер
    try:
        process = subprocess.Popen(['python3', 'app_test.py'], env=env)
        time.sleep(5)  # Ждем запуска
        
        # Тестируем health
        try:
            response = requests.get('http://localhost:5002/api/health', timeout=5)
            print(f"🏥 Health: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Сервер работает: {health_data}")
                
                # Тестируем получение шаблонов
                templates_response = requests.get('http://localhost:5002/api/templates/all-previews', timeout=10)
                print(f"📋 Templates: {templates_response.status_code}")
                
                if templates_response.status_code == 200:
                    templates_data = templates_response.json()
                    templates = templates_data.get('templates', [])
                    print(f"✅ Найдено шаблонов: {len(templates)}")
                    
                    # Показываем первые несколько
                    for i, template in enumerate(templates[:3]):
                        print(f"  {i+1}. {template.get('name')} - {template.get('preview_url')}")
                        
                        # Проверяем превью
                        preview_url = f"http://localhost:5002{template.get('preview_url')}"
                        try:
                            preview_response = requests.head(preview_url, timeout=5)
                            print(f"     Превью: {preview_response.status_code}")
                        except:
                            print(f"     Превью: недоступно")
                
                return True
            else:
                print("❌ Сервер не отвечает")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
            return False
            
    finally:
        # Убиваем процесс
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        
        # Удаляем временный файл
        try:
            os.remove('app_test.py')
        except:
            pass

if __name__ == "__main__":
    success = test_preview_api()
    if success:
        print("\n🎉 ПРЕВЬЮ РАБОТАЮТ!")
    else:
        print("\n❌ Есть проблемы с превью")