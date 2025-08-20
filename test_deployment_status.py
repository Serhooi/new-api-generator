#!/usr/bin/env python3
"""
Проверяем статус развертывания и доступность API
"""
import requests
import time

BASE_URL = "https://new-api-generator-1.onrender.com"

def check_deployment_status():
    """Проверяем статус развертывания"""
    
    print("🔍 Проверяем статус развертывания...")
    print("=" * 50)
    
    # 1. Проверяем основной endpoint
    print("\n1️⃣ Проверяем основной endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Сервер доступен!")
        else:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # 2. Проверяем API endpoints
    print("\n2️⃣ Проверяем API endpoints")
    
    # Список endpoints для проверки
    endpoints = [
        "/api/templates",
        "/api/generate/carousel",
        "/api/generate/carousel-png",
        "/api/generate/carousel-png-simple"
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint == "/api/templates":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            else:
                # Для POST endpoints делаем HEAD запрос
                response = requests.head(f"{BASE_URL}{endpoint}", timeout=10)
            
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ❌ Endpoint {endpoint} не найден")
            elif response.status_code in [200, 405]:  # 405 = Method Not Allowed (нормально для HEAD на POST)
                print(f"   ✅ Endpoint {endpoint} доступен")
            else:
                print(f"   ⚠️ Endpoint {endpoint}: статус {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка {endpoint}: {e}")
    
    return True

def test_simple_png_generation():
    """Тестируем простую PNG генерацию"""
    
    print("\n3️⃣ Тестируем PNG генерацию")
    
    test_data = {
        "main_template_id": "propertyimage2",
        "data": {
            "address": "123 Test Street",
            "price": "$500,000"
        }
    }
    
    try:
        print("   📤 Отправляем запрос на PNG генерацию...")
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel-png-simple",
            json=test_data,
            timeout=30
        )
        
        print(f"   📥 Ответ: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ PNG успешно сгенерирован!")
            print(f"   🔗 URL: {result.get('url', 'НЕТ URL')}")
            
            # Проверяем Content-Type
            if 'url' in result:
                file_response = requests.head(result['url'])
                content_type = file_response.headers.get('content-type', 'НЕ УКАЗАН')
                print(f"   📄 Content-Type: {content_type}")
                
                if '.png' in result['url']:
                    print(f"   ✅ Файл имеет расширение .png")
                else:
                    print(f"   ❌ Файл НЕ имеет расширение .png")
                    
        else:
            print(f"   ❌ Ошибка генерации: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    print("🚀 Проверка статуса развертывания API")
    print(f"🌐 URL: {BASE_URL}")
    print(f"⏰ Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if check_deployment_status():
        test_simple_png_generation()
    
    print("\n" + "=" * 50)
    print("✅ Проверка завершена!")