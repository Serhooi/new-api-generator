#!/usr/bin/env python3
"""
Полный интеграционный тест системы замены изображений через API
"""

import requests
import json
import time

def test_api_with_images():
    """Тестируем API с заменой изображений"""
    
    print("🧪 ПОЛНЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ API")
    print("=" * 60)
    
    # URL вашего API (замените на актуальный)
    api_url = "http://localhost:5000/api/preview"
    
    # Тестовые данные с изображениями
    test_data = {
        "template": "main",  # или путь к SVG файлу
        "data": {
            # Текстовые поля
            "dyno.date": "DECEMBER 15 2024",
            "dyno.time": "2:00 PM - 4:00 PM", 
            "dyno.price": "$850,000",
            "dyno.propertyaddress": "123 Main Street, Anytown",
            "dyno.bedrooms": "4",
            "dyno.bathrooms": "3",
            "dyno.name": "John Smith",
            "dyno.phone": "(555) 123-4567",
            "dyno.email": "john@example.com",
            "dyno.propertyfeatures": "Pool, Garden, Garage",
            
            # Изображения - это ключевая часть теста!
            "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&h=600&fit=crop",
            "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face",
            "dyno.logo": "https://via.placeholder.com/142x56/4F46E5/FFFFFF?text=LOGO"
        },
        "preview_type": "base64"
    }
    
    print(f"📤 Отправляю запрос на: {api_url}")
    print(f"📋 Данные включают {len(test_data['data'])} полей")
    
    # Подсчитываем поля изображений
    image_fields = [k for k in test_data['data'].keys() 
                   if any(word in k.lower() for word in ['image', 'photo', 'logo', 'headshot'])]
    print(f"🖼️ Поля изображений: {image_fields}")
    
    try:
        # Отправляем запрос
        start_time = time.time()
        response = requests.post(api_url, json=test_data, timeout=60)
        end_time = time.time()
        
        print(f"⏱️ Время обработки: {end_time - start_time:.2f} секунд")
        print(f"📊 HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ API ответил успешно!")
            print(f"📋 Ключи ответа: {list(result.keys())}")
            
            if result.get('success'):
                print(f"🎉 Превью создано успешно!")
                
                # Проверяем наличие base64 данных
                if 'base64' in result:
                    base64_length = len(result['base64'])
                    print(f"📊 Размер base64: {base64_length} символов")
                    
                    # Проверяем что это валидный base64 изображения
                    if result['base64'].startswith('data:image/'):
                        print(f"✅ Валидный base64 изображения!")
                    else:
                        print(f"⚠️ Неожиданный формат base64")
                
                # Проверяем информацию о заменах
                if 'replacements_count' in result:
                    print(f"🔄 Количество замен: {result['replacements_count']}")
                
                if 'has_data' in result:
                    print(f"📝 Данные применены: {result['has_data']}")
                
                print(f"\n🎯 ТЕСТ ПРОЙДЕН УСПЕШНО!")
                return True
                
            else:
                print(f"❌ API вернул ошибку: {result.get('error', 'Неизвестная ошибка')}")
                return False
                
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout - API не ответил за 60 секунд")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 Ошибка подключения - убедитесь что сервер запущен на {api_url}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_server_status():
    """Проверяем что сервер запущен"""
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Сервер запущен и отвечает")
            return True
        else:
            print(f"⚠️ Сервер отвечает с кодом: {response.status_code}")
            return False
    except:
        print("❌ Сервер не запущен или недоступен")
        print("💡 Запустите сервер командой: python3 app.py")
        return False

if __name__ == "__main__":
    print("🚀 ЗАПУСК ПОЛНОГО ИНТЕГРАЦИОННОГО ТЕСТА")
    print("=" * 60)
    
    # Проверяем сервер
    if test_server_status():
        print()
        # Тестируем API
        success = test_api_with_images()
        
        if success:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print("✅ Система замены изображений работает корректно")
            print("✅ Можно загружать свои файлы и использовать API")
        else:
            print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ")
            print("🔧 Требуется дополнительная отладка")
    else:
        print("\n🔧 Сначала запустите сервер!")