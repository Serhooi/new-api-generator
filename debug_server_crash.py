#!/usr/bin/env python3
"""
Диагностика падения сервера при генерации карусели
"""

import requests
import json
import time

def test_carousel_generation():
    """Тестируем генерацию карусели с детальным логированием"""
    
    url = "https://new-api-generator-1.onrender.com/generate-carousel"
    
    # Минимальные данные для теста
    test_data = {
        "template_id": "propertyimage2",
        "data": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем генерацию карусели...")
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем запрос с таймаутом
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        print(f"📊 Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут запроса (30 секунд)")
    except requests.exceptions.ConnectionError as e:
        print(f"🔌 Ошибка соединения: {e}")
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")

def test_server_health():
    """Проверяем здоровье сервера"""
    
    health_url = "https://new-api-generator-1.onrender.com/"
    
    print("\n🏥 Проверяем здоровье сервера...")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"📊 Статус: {response.status_code}")
        print(f"📊 Ответ: {response.text[:200]}...")
        
    except Exception as e:
        print(f"💥 Сервер недоступен: {e}")

if __name__ == "__main__":
    print("🚀 Диагностика падения сервера")
    print("=" * 50)
    
    # Проверяем здоровье сервера
    test_server_health()
    
    # Ждем немного
    time.sleep(2)
    
    # Тестируем генерацию карусели
    test_carousel_generation()