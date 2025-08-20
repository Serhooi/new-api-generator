#!/usr/bin/env python3
"""
Тест текущего состояния развертывания - проверяем все PNG endpoints
"""
import requests
import json

# URL вашего API
BASE_URL = "https://new-api-generator.onrender.com"

def test_png_endpoints():
    """Тестируем все PNG endpoints"""
    
    # Тестовые данные
    test_data = {
        "main_template_id": "propertyimage2",
        "photo_template_id": "propertyimage2",
        "data": {
            "address": "123 Test Street",
            "price": "$500,000",
            "beds": "3",
            "baths": "2",
            "sqft": "1,500",
            "agent_name": "Test Agent",
            "agent_phone": "(555) 123-4567",
            "agent_email": "test@example.com"
        }
    }
    
    print("🔍 Тестируем PNG endpoints...")
    print("=" * 50)
    
    # 1. Основной endpoint с format: png
    print("\n1️⃣ Тест: /api/generate/carousel с format: 'png'")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel",
            json={**test_data, "format": "png"},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Format в ответе: {result.get('format', 'НЕ УКАЗАН')}")
            print(f"URL: {result.get('url', 'НЕТ URL')}")
            
            # Проверяем Content-Type файла
            if 'url' in result:
                file_response = requests.head(result['url'])
                print(f"Content-Type файла: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                print(f"Расширение в URL: {'.png' if '.png' in result['url'] else '.svg' if '.svg' in result['url'] else 'НЕИЗВЕСТНО'}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    
    # 2. PNG endpoint
    print("\n2️⃣ Тест: /api/generate/carousel-png")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel-png",
            json=test_data,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"URL: {result.get('url', 'НЕТ URL')}")
            
            # Проверяем Content-Type файла
            if 'url' in result:
                file_response = requests.head(result['url'])
                print(f"Content-Type файла: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                print(f"Расширение в URL: {'.png' if '.png' in result['url'] else '.svg' if '.svg' in result['url'] else 'НЕИЗВЕСТНО'}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    
    # 3. Простой PNG endpoint
    print("\n3️⃣ Тест: /api/generate/carousel-png-simple")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel-png-simple",
            json=test_data,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"URL: {result.get('url', 'НЕТ URL')}")
            
            # Проверяем Content-Type файла
            if 'url' in result:
                file_response = requests.head(result['url'])
                print(f"Content-Type файла: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                print(f"Расширение в URL: {'.png' if '.png' in result['url'] else '.svg' if '.svg' in result['url'] else 'НЕИЗВЕСТНО'}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    
    # 4. Проверяем обычный SVG для сравнения
    print("\n4️⃣ Тест: /api/generate/carousel (обычный SVG)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate/carousel",
            json=test_data,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Format в ответе: {result.get('format', 'НЕ УКАЗАН')}")
            print(f"URL: {result.get('url', 'НЕТ URL')}")
            
            # Проверяем Content-Type файла
            if 'url' in result:
                file_response = requests.head(result['url'])
                print(f"Content-Type файла: {file_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                print(f"Расширение в URL: {'.png' if '.png' in result['url'] else '.svg' if '.svg' in result['url'] else 'НЕИЗВЕСТНО'}")
        else:
            print(f"Ошибка: {response.text}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")

if __name__ == "__main__":
    test_png_endpoints()