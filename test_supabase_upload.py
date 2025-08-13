#!/usr/bin/env python3
"""
Тест загрузки в Supabase
"""

import requests
import json

def test_supabase_upload():
    """Тестируем загрузку файла в Supabase"""
    
    print("🧪 ТЕСТ ЗАГРУЗКИ В SUPABASE")
    print("=" * 50)
    
    try:
        # Отправляем POST запрос на тестовый endpoint
        response = requests.post(
            "http://localhost:5000/api/test-supabase",
            json={},
            timeout=30
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Загрузка успешна!")
            print(f"📄 Файл: {result.get('filename')}")
            print(f"🌐 URL: {result.get('url')}")
            
            # Проверяем доступность URL
            file_url = result.get('url')
            if file_url:
                print(f"\n🔍 Проверяю доступность URL...")
                try:
                    url_response = requests.head(file_url, timeout=10)
                    print(f"📊 URL статус: {url_response.status_code}")
                    
                    if url_response.status_code == 200:
                        print("✅ Файл доступен по URL!")
                        
                        # Проверяем заголовки
                        content_type = url_response.headers.get('content-type', 'unknown')
                        print(f"📄 Content-Type: {content_type}")
                        
                        cors_origin = url_response.headers.get('access-control-allow-origin')
                        if cors_origin:
                            print(f"🌐 CORS Origin: {cors_origin}")
                        else:
                            print("⚠️ CORS заголовки отсутствуют")
                            
                    else:
                        print(f"❌ Файл недоступен: {url_response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ Ошибка проверки URL: {e}")
            
            return True
            
        else:
            print(f"❌ Ошибка загрузки: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

if __name__ == "__main__":
    test_supabase_upload()