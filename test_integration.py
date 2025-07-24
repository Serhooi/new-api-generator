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
    """Тест создания и генерации полноценной карусели с множественными фото"""
    print("\n🎠 Тестирование создания полноценной карусели...")
    
    # Тестовые фотографии недвижимости
    property_photos = [
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa",  # Экстерьер
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be",  # Гостиная
        "https://images.unsplash.com/photo-1586023492125-27b2c045efd7",  # Кухня
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2",   # Спальня
        "https://images.unsplash.com/photo-1560448075-bb485b067938",   # Ванная
        "https://images.unsplash.com/photo-1560448204-61dc36dc98c8",   # Столовая
    ]
    
    carousel_data = {
        "name": "Test Property Carousel - Full Version",
        "slides": [
            # Main слайд
            {
                "templateId": "open-house-main",
                "replacements": {
                    "dyno.agentName": "John Smith",
                    "dyno.propertyAddress": "123 Main Street, Beverly Hills, CA 90210",
                    "dyno.price": "$450,000",
                    "dyno.bedrooms": "3",
                    "dyno.bathrooms": "2",
                    "dyno.sqft": "1,850",
                    "dyno.agentPhone": "(555) 123-4567",
                    "dyno.agentEmail": "john@realty.com",
                    "dyno.openHouseDate": "Saturday, June 8th",
                    "dyno.openHouseTime": "2:00 PM - 4:00 PM",
                    "dyno.agentPhoto": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"
                },
                "imagePath": property_photos[0]
            }
        ]
    }
    
    # Добавляем фото слайды с правильными полями dyno.propertyimage2, dyno.propertyimage3, etc.
    for i, photo_url in enumerate(property_photos):
        carousel_data["slides"].append({
            "templateId": "open-house-photo",
            "replacements": {
                f"dyno.propertyimage{i + 2}": photo_url  # dyno.propertyimage2, dyno.propertyimage3, etc.
            },
            "imagePath": photo_url
        })
    
    print(f"📊 Создаю карусель с {len(carousel_data['slides'])} слайдами:")
    print(f"   - 1 main слайд")
    print(f"   - {len(property_photos)} фото слайдов (dyno.propertyimage2-{len(property_photos)+1})")
    
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

