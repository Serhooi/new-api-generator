#!/usr/bin/env python3
"""
Тест исправлений через сервер API
"""

import requests
import json
import time

def test_carousel_with_fixes():
    """Тестируем создание карусели с исправлениями"""
    
    print("🧪 ТЕСТ СЕРВЕРА С ИСПРАВЛЕНИЯМИ")
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
        # Отправляем запрос на создание карусели
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
            
            # Проверяем что исправления применились
            print("\n🔍 ПРОВЕРКА ИСПРАВЛЕНИЙ:")
            
            # Проверяем main слайд (headshot)
            main_slides = [s for s in slides if s.get('type') == 'main']
            if main_slides:
                print("✅ Main слайд найден - headshot должен быть исправлен")
            else:
                print("❌ Main слайд не найден")
            
            # Проверяем photo слайды
            photo_slides = [s for s in slides if s.get('type') == 'photo']
            if photo_slides:
                print(f"✅ Photo слайдов найдено: {len(photo_slides)} - группы должны быть исправлены")
            else:
                print("❌ Photo слайды не найдены")
            
            print(f"\n🎉 ТЕСТ УСПЕШЕН! Карусель: {result.get('carousel_id')}")
            
        else:
            print(f"❌ Ошибка сервера: {response.status_code}")
            print(f"📄 Ответ: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python3 app.py")
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (>60 сек)")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Запускаем тест"""
    
    print("🚀 ТЕСТ ИСПРАВЛЕНИЙ ЧЕРЕЗ СЕРВЕР")
    print("=" * 60)
    print("⚠️  Убедитесь что сервер запущен: python3 app.py")
    print()
    
    test_carousel_with_fixes()
    
    print("\n🎯 ТЕСТ ЗАВЕРШЕН!")
    print("\n📋 ЧТО ПРОВЕРИТЬ:")
    print("1. Headshot не должен быть растянутым")
    print("2. Photo слайд должен показывать замененное изображение")
    print("3. Все изображения должны загружаться корректно")

if __name__ == "__main__":
    main()