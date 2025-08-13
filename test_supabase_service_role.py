#!/usr/bin/env python3
"""
Тест загрузки в Supabase с service role ключом
"""

import os
import uuid
from supabase import create_client, Client

def test_service_role_upload():
    """Тестируем загрузку с service role ключом"""
    
    print("🧪 ТЕСТ ЗАГРУЗКИ С SERVICE ROLE")
    print("=" * 50)
    
    # Получаем переменные окружения
    supabase_url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Переменные не установлены")
        return False
    
    try:
        # Создаем клиент с service role ключом
        supabase: Client = create_client(supabase_url, service_key)
        print(f"✅ Supabase клиент создан с service role")
        
        # Создаем тестовый SVG
        test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="green"/>
  <text x="100" y="100" text-anchor="middle" fill="white" font-size="20">SERVICE ROLE TEST</text>
</svg>'''
        
        # Генерируем уникальное имя файла
        test_filename = f"service_test_{uuid.uuid4().hex[:8]}.svg"
        file_path = f"carousel/{test_filename}"
        
        print(f"📤 Загружаю файл: {file_path}")
        
        # Загружаем в carousel-assets bucket
        result = supabase.storage.from_("carousel-assets").upload(
            path=file_path,
            file=test_svg.encode('utf-8'),
            file_options={"content-type": "image/svg+xml"}
        )
        
        print(f"✅ Файл загружен: {result}")
        
        # Получаем публичный URL
        public_url = supabase.storage.from_("carousel-assets").get_public_url(file_path)
        print(f"🌐 Публичный URL: {public_url}")
        
        # Тестируем доступность URL
        import requests
        try:
            response = requests.head(public_url, timeout=10)
            print(f"📊 URL статус: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Файл доступен по публичному URL!")
                
                # Проверяем заголовки
                content_type = response.headers.get('content-type', 'unknown')
                print(f"📄 Content-Type: {content_type}")
                
                cors_origin = response.headers.get('access-control-allow-origin')
                if cors_origin:
                    print(f"🌐 CORS Origin: {cors_origin}")
                else:
                    print("⚠️ CORS заголовки отсутствуют")
                    
                return True
                
            else:
                print(f"❌ Файл недоступен: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка проверки URL: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return False

def test_anon_key_access():
    """Тестируем доступ с anon ключом"""
    
    print("\n🧪 ТЕСТ ДОСТУПА С ANON KEY")
    print("=" * 40)
    
    supabase_url = os.environ.get('SUPABASE_URL')
    anon_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not supabase_url or not anon_key:
        print("❌ Переменные не установлены")
        return False
    
    try:
        # Создаем клиент с anon ключом
        supabase: Client = create_client(supabase_url, anon_key)
        print(f"✅ Supabase клиент создан с anon key")
        
        # Пробуем получить список файлов
        try:
            files = supabase.storage.from_("carousel-assets").list("carousel")
            print(f"✅ Список файлов получен: {len(files)} файлов")
            
            if files:
                print("📋 Последние файлы:")
                for file in files[-3:]:  # Показываем последние 3
                    print(f"  - {file['name']} ({file['metadata']['size']} bytes)")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка получения списка файлов: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Проверяю переменные окружения...")
    print(f"SUPABASE_URL: {'✅' if os.environ.get('SUPABASE_URL') else '❌'}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅' if os.environ.get('SUPABASE_SERVICE_ROLE_KEY') else '❌'}")
    print(f"SUPABASE_ANON_KEY: {'✅' if os.environ.get('SUPABASE_ANON_KEY') else '❌'}")
    
    # Тест с service role
    service_success = test_service_role_upload()
    
    # Тест с anon key
    anon_success = test_anon_key_access()
    
    print(f"\n📊 ИТОГИ:")
    print(f"Service role загрузка: {'✅' if service_success else '❌'}")
    print(f"Anon key доступ: {'✅' if anon_success else '❌'}")
    
    if service_success and anon_success:
        print("🎉 Supabase настроен правильно!")
    else:
        print("⚠️ Есть проблемы с настройкой Supabase")