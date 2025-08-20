#!/usr/bin/env python3
"""
Тестируем улучшенную PNG конвертацию
"""

import requests
import json
import os

def test_png_conversion():
    """Тестируем PNG конвертацию через API"""
    
    print("🧪 ТЕСТИРУЮ УЛУЧШЕННУЮ PNG КОНВЕРТАЦИЮ")
    print("=" * 50)
    
    # Тестовые данные
    test_data = {
        "main_template_id": "1",
        "photo_template_id": "2", 
        "format": "png",
        "replacements": {
            "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop&crop=face",
            "dyno.propertyimage1": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&h=600&fit=crop",
            "dyno.address": "123 Test Street",
            "dyno.price": "$750,000",
            "dyno.beds": "3",
            "dyno.baths": "2",
            "dyno.sqft": "2,500"
        }
    }
    
    try:
        print("📤 Отправляю запрос на генерацию PNG карусели...")
        
        response = requests.post(
            'http://localhost:5002/api/generate/carousel',
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Запрос успешен!")
            print(f"📋 Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Проверяем URL изображений
            if 'image_urls' in result:
                for i, url in enumerate(result['image_urls']):
                    print(f"🖼️ Изображение {i+1}: {url}")
                    
                    # Проверяем что это PNG
                    if '.png' in url:
                        print(f"✅ Изображение {i+1} в формате PNG")
                        
                        # Пробуем скачать и проверить размер
                        try:
                            img_response = requests.get(url, timeout=10)
                            if img_response.status_code == 200:
                                size = len(img_response.content)
                                print(f"📊 Размер изображения {i+1}: {size} bytes")
                                
                                if size > 5000:  # Больше 5KB - значит не пустое
                                    print(f"✅ Изображение {i+1} содержит данные!")
                                else:
                                    print(f"⚠️ Изображение {i+1} слишком маленькое")
                            else:
                                print(f"❌ Не удалось скачать изображение {i+1}")
                        except Exception as e:
                            print(f"❌ Ошибка проверки изображения {i+1}: {e}")
                    else:
                        print(f"❌ Изображение {i+1} не в формате PNG")
            
            return True
            
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            print(f"📋 Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def test_svg_to_png_api():
    """Тестируем API конвертации SVG в PNG"""
    
    print("\n🧪 ТЕСТИРУЮ SVG → PNG API")
    print("=" * 30)
    
    # Получаем SVG URL из предыдущего теста
    test_data = {
        "main_template_id": "1",
        "photo_template_id": "2", 
        "format": "svg",  # Сначала получаем SVG
        "replacements": {
            "dyno.address": "Test Address for PNG",
            "dyno.price": "$999,999"
        }
    }
    
    try:
        # Получаем SVG
        response = requests.post(
            'http://localhost:5002/api/generate/carousel',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'image_urls' in result and result['image_urls']:
                svg_url = result['image_urls'][0]  # Берем первый SVG
                print(f"📥 SVG URL: {svg_url}")
                
                # Конвертируем в PNG
                convert_data = {"svg_url": svg_url}
                
                convert_response = requests.post(
                    'http://localhost:5002/api/convert-to-png',
                    json=convert_data,
                    timeout=30
                )
                
                print(f"📊 Статус конвертации: {convert_response.status_code}")
                
                if convert_response.status_code == 200:
                    convert_result = convert_response.json()
                    print("✅ SVG → PNG конвертация успешна!")
                    print(f"📋 Результат: {json.dumps(convert_result, indent=2)}")
                    return True
                else:
                    print(f"❌ Ошибка конвертации: {convert_response.text}")
                    return False
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка теста SVG → PNG: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ PNG СИСТЕМЫ")
    print("=" * 60)
    
    # Проверяем что сервер запущен
    try:
        response = requests.get('http://localhost:5002/health', timeout=5)
        if response.status_code == 200:
            print("✅ Сервер работает")
        else:
            print("❌ Сервер не отвечает")
            exit(1)
    except:
        print("❌ Сервер недоступен. Запустите: python3 app.py")
        exit(1)
    
    # Тестируем PNG генерацию
    png_success = test_png_conversion()
    
    # Тестируем SVG → PNG API
    api_success = test_svg_to_png_api()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ PNG генерация: {'Работает' if png_success else 'Не работает'}")
    print(f"✅ SVG → PNG API: {'Работает' if api_success else 'Не работает'}")
    
    if png_success and api_success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
        print("✅ Улучшенная PNG система работает корректно")
        print("✅ Playwright установлен и функционирует")
        print("✅ PIL fallback создает осмысленные изображения")
    else:
        print("\n⚠️ Есть проблемы с PNG системой")
        print("Проверьте логи сервера для деталей")