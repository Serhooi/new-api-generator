#!/usr/bin/env python3
"""
Тест доступности Supabase URL
"""

import requests

def test_supabase_urls():
    """Тестируем доступность URL из Supabase"""
    
    print("🔍 ТЕСТ ДОСТУПНОСТИ SUPABASE URL")
    print("=" * 50)
    
    # Тестовые URL из ошибки
    test_urls = [
        "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-templates/carousel/carousel_test_main.svg",
        "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/images/carousel/carousel_test_main.svg",
        "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-templates/carousel_test_main.svg"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\\n🌐 Тест {i}: {url}")
        
        try:
            # Делаем HEAD запрос
            response = requests.head(url, timeout=10)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ URL доступен")
                
                # Проверяем заголовки
                content_type = response.headers.get('content-type', 'unknown')
                print(f"📄 Content-Type: {content_type}")
                
                cors_origin = response.headers.get('access-control-allow-origin')
                if cors_origin:
                    print(f"🌐 CORS Origin: {cors_origin}")
                else:
                    print("⚠️ CORS заголовки отсутствуют")
                    
            elif response.status_code == 404:
                print("❌ Файл не найден (404)")
            elif response.status_code == 403:
                print("❌ Доступ запрещен (403)")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")

def test_bucket_access():
    """Тестируем доступ к разным bucket"""
    
    print("\\n🪣 ТЕСТ ДОСТУПА К BUCKET")
    print("=" * 40)
    
    base_url = "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public"
    
    buckets = [
        "images",
        "carousel-assets", 
        "carousel-templates",
        "templates",
        "generated"
    ]
    
    for bucket in buckets:
        url = f"{base_url}/{bucket}/"
        print(f"\\n🪣 Bucket: {bucket}")
        print(f"🌐 URL: {url}")
        
        try:
            response = requests.head(url, timeout=5)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code in [200, 403]:  # 403 может означать что bucket существует но пустой
                print("✅ Bucket доступен")
            else:
                print("❌ Bucket недоступен")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_supabase_urls()
    test_bucket_access()