#!/usr/bin/env python3
"""
Детальный тест PNG генерации с полным ответом
"""
import requests
import json

BASE_URL = "https://new-api-generator.onrender.com"

def test_detailed_png():
    """Детальный тест PNG генерации"""
    
    print("🔍 Детальный тест PNG генерации")
    print("=" * 50)
    
    # Тестовые данные
    test_data = {
        "main_template_id": "propertyimage2",
        "photo_template_id": "propertyimage2",
        "data": {
            "address": "123 Test Street, Beverly Hills, CA 90210",
            "price": "$500,000",
            "beds": "3",
            "baths": "2",
            "sqft": "1,500",
            "agent_name": "Test Agent",
            "agent_phone": "(555) 123-4567",
            "agent_email": "test@example.com"
        }
    }
    
    # 1. Тест основного endpoint с format: png
    print("\n1️⃣ Тест: /api/generate/carousel с format: 'png'")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel",
            json={**test_data, "format": "png"},
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Полный ответ:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Анализируем ответ
                if 'format' in result:
                    print(f"✅ Format: {result['format']}")
                
                if 'url' in result and result['url']:
                    print(f"✅ URL найден: {result['url']}")
                    
                    # Проверяем доступность файла
                    file_response = requests.head(result['url'])
                    print(f"Файл доступен: {file_response.status_code}")
                    print(f"Content-Type: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                    
                    if '.png' in result['url']:
                        print(f"✅ URL содержит .png")
                    else:
                        print(f"❌ URL НЕ содержит .png")
                        
                else:
                    print(f"❌ URL отсутствует или пустой")
                    
                if 'error' in result:
                    print(f"❌ Ошибка в ответе: {result['error']}")
                    
            except json.JSONDecodeError:
                print(f"❌ Ответ не является JSON:")
                print(response.text[:500])
        else:
            print(f"❌ Ошибка HTTP: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # 2. Тест PNG-simple endpoint
    print("\n2️⃣ Тест: /api/generate/carousel-png-simple")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel-png-simple",
            json=test_data,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Полный ответ:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if 'url' in result and result['url']:
                    print(f"✅ URL найден: {result['url']}")
                    
                    # Проверяем доступность файла
                    file_response = requests.head(result['url'])
                    print(f"Файл доступен: {file_response.status_code}")
                    print(f"Content-Type: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                else:
                    print(f"❌ URL отсутствует")
                    
            except json.JSONDecodeError:
                print(f"❌ Ответ не является JSON:")
                print(response.text[:500])
        else:
            print(f"❌ Ошибка HTTP: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_detailed_png()