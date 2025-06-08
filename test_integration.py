#!/usr/bin/env python3
"""
Тестирование интеграции API с реальными данными
"""

import requests
import json
import time

# Конфигурация
API_BASE_URL = "http://localhost:9999"

def test_templates_endpoint():
    """Тест получения шаблонов"""
    print("🔍 Тестирование получения шаблонов...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/templates/all-previews")
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Найдено шаблонов: {len(data.get('templates', []))}")
            for template in data.get('templates', []):
                print(f"  - {template['name']} ({template['id']})")
            return True
        else:
            print(f"Ошибка: {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_carousel_creation():
    """Тест создания и генерации карусели"""
    print("\n🎠 Тестирование создания карусели...")
    
    carousel_data = {
        "name": "Test Property Carousel",
        "slides": [
            {
                "templateId": "open-house-main",
                "replacements": {
                    "dyno.agentName": "John Smith",
                    "dyno.propertyAddress": "123 Main Street, City, State 12345",
                    "dyno.price": "$450,000",
                    "dyno.bedrooms": "3",
                    "dyno.bathrooms": "2",
                    "dyno.sqft": "1,850",
                    "dyno.agentPhone": "(555) 123-4567",
                    "dyno.agentEmail": "john@realty.com",
                    "dyno.openHouseDate": "Saturday, June 8th",
                    "dyno.openHouseTime": "2:00 PM - 4:00 PM"
                },
                "imagePath": "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
            },
            {
                "templateId": "open-house-photo",
                "replacements": {
                    "dyno.propertyImage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
                },
                "imagePath": "https://images.unsplash.com/photo-1560518883-ce09059eeffa"
            },
            {
                "templateId": "open-house-photo",
                "replacements": {
                    "dyno.propertyImage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be"
                },
                "imagePath": "https://images.unsplash.com/photo-1570129477492-45c003edd2be"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/carousel/create-and-generate",
            json=carousel_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            carousel_id = data.get('carousel_id')
            print(f"Карусель создана: {carousel_id}")
            return carousel_id
        else:
            print(f"Ошибка: {response.text}")
            return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def test_carousel_status(carousel_id, max_attempts=15):
    """Тест проверки статуса карусели"""
    print(f"\n📊 Проверка статуса карусели {carousel_id}...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/api/carousel/{carousel_id}/slides")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                slides = data.get('slides', [])
                
                print(f"Попытка {attempt + 1}: Статус = {status}")
                
                completed_slides = [s for s in slides if s.get('status') == 'completed']
                print(f"Готовых слайдов: {len(completed_slides)}/{len(slides)}")
                
                if status == 'completed':
                    print("✅ Генерация завершена!")
                    for slide in slides:
                        print(f"  Слайд {slide['slide_number']}: {slide['image_url']}")
                    return data
                elif status == 'error':
                    print("❌ Ошибка генерации")
                    return None
                
                time.sleep(2)
            else:
                print(f"Ошибка запроса: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    
    print("⏰ Превышено время ожидания")
    return None

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ API")
    print("=" * 50)
    
    # 1. Тест получения шаблонов
    if not test_templates_endpoint():
        print("❌ Тест шаблонов провален")
        return
    
    # 2. Тест создания карусели
    carousel_id = test_carousel_creation()
    if not carousel_id:
        print("❌ Тест создания карусели провален")
        return
    
    # 3. Тест проверки статуса
    result = test_carousel_status(carousel_id)
    if result:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\n📋 РЕЗУЛЬТАТЫ:")
        for slide in result.get('slides', []):
            print(f"  Слайд {slide['slide_number']}: {slide['image_url']}")
    else:
        print("❌ Тест статуса провален")

if __name__ == "__main__":
    main()

