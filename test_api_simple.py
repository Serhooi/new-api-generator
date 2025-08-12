#!/usr/bin/env python3
"""
Простой тест API без запуска сервера
"""

import requests
import json
import time

def test_api_call():
    """Тестируем API вызов"""
    
    print("🧪 ТЕСТ API ВЫЗОВА")
    print("=" * 50)
    
    # Данные для тестирования
    test_data = {
        "dyno.agentName": "Тест Агент",
        "dyno.agentPhone": "+1234567890", 
        "dyno.agentEmail": "test@example.com",
        "dyno.price": "$500,000",
        "dyno.propertyAddress": "123 Test Street",
        "dyno.bedrooms": "3",
        "dyno.bathrooms": "2",
        "dyno.date": "Aug 12, 2025",
        "dyno.time": "2:00 PM",
        "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
        "dyno.propertyimage2": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300", 
        "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face",
        "dyno.logo": "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=142&h=56",
        "dyno.propertyfeatures": "Бассейн, гараж, сад"
    }
    
    print("📋 Тестовые данные подготовлены")
    print(f"🖼️ Изображения: {len([k for k in test_data.keys() if 'image' in k or 'headshot' in k or 'logo' in k])} шт.")
    
    try:
        print("📤 Отправляю запрос на создание карусели...")
        
        response = requests.post(
            'http://localhost:5000/api/carousel/create-and-generate',
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Карусель создана успешно!")
            print(f"🆔 ID карусели: {result.get('carousel_id', 'N/A')}")
            
            # Проверяем созданные слайды
            slides = result.get('slides', [])
            print(f"📊 Создано слайдов: {len(slides)}")
            
            for i, slide in enumerate(slides):
                slide_type = slide.get('type', 'unknown')
                slide_url = slide.get('url', 'N/A')
                print(f"   {i+1}. {slide_type}: {slide_url[:80]}...")
            
            print(f"\n🎉 ТЕСТ УСПЕШЕН! Карусель: {result.get('carousel_id')}")
            return True
            
        else:
            print(f"❌ Ошибка сервера: {response.status_code}")
            print(f"📄 Ответ: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python3 app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (>60 сек)")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Запускаем тест"""
    
    print("🚀 ПРОСТОЙ ТЕСТ API")
    print("=" * 60)
    print("⚠️  Убедитесь что сервер запущен: python3 app.py")
    print()
    
    success = test_api_call()
    
    print("\n🎯 ТЕСТ ЗАВЕРШЕН!")
    
    if success:
        print("\n✅ ВСЕ РАБОТАЕТ!")
        print("📋 ПРОВЕРЬТЕ:")
        print("1. Headshot должен быть правильного размера (не слишком большой)")
        print("2. Photo слайд должен показывать dyno.propertyimage2")
        print("3. Main слайд должен показывать dyno.propertyimage")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ")
        print("📋 ПРОВЕРЬТЕ:")
        print("1. Запущен ли сервер: python3 app.py")
        print("2. Нет ли ошибок в логах сервера")

if __name__ == "__main__":
    main()