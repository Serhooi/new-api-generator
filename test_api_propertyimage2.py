#!/usr/bin/env python3
"""
Тест API для dyno.propertyimage2
"""

import requests
import json
import time

API_URL = "http://localhost:5000"

def test_carousel_generation():
    """Тестирует генерацию карусели с dyno.propertyimage2"""
    
    print("🧪 ТЕСТ API ДЛЯ DYNO.PROPERTYIMAGE2")
    print("=" * 50)
    
    # Получаем ID шаблонов
    main_template_id = "0f30799d-37bb-487f-853a-6bc70bdd577c"  # из вывода create_test_templates.py
    photo_template_id = "dcdad5a5-9c18-45f6-ab87-e6b14d5b5c59"
    
    # Тестовые данные
    test_data = {
        "main_template_id": main_template_id,
        "photo_template_id": photo_template_id,
        "data": {
            # Для main слайда
            "dyno.propertyimage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1080&h=600&fit=crop",
            "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            
            # Для photo слайда
            "dyno.propertyimage2": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1080&h=800&fit=crop",
            
            # Общие поля
            "dyno.propertyaddress": "123 Main Street, Beverly Hills, CA 90210",
            "dyno.price": "$450,000",
            "dyno.name": "John Smith",
            "dyno.phone": "(555) 123-4567"
        }
    }
    
    print(f"📋 Тестовые данные:")
    print(f"   Main template: {main_template_id}")
    print(f"   Photo template: {photo_template_id}")
    print(f"   dyno.propertyimage2: {test_data['data']['dyno.propertyimage2'][:50]}...")
    
    print(f"\n🔄 Отправляю запрос на генерацию карусели...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/generate/carousel",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Карусель создана успешно!")
            print(f"   Carousel ID: {result.get('carousel_id', 'N/A')}")
            print(f"   Количество слайдов: {len(result.get('slides', []))}")
            
            # Проверяем слайды
            for i, slide in enumerate(result.get('slides', [])):
                print(f"   Слайд {i+1}: {slide.get('filename', 'N/A')}")
                
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"   Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удается подключиться к серверу на {API_URL}")
        print(f"   Убедитесь, что сервер запущен: python3 app.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_carousel_generation()