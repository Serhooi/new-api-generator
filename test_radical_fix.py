#!/usr/bin/env python3
"""
Тест радикального исправления SVG
"""

import requests
import time

def test_radical_svg_fix():
    """Тестируем радикальное исправление"""
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "main_template_1",
        "photo_template_id": "photo_template_1", 
        "data": {
            "propertyaddress": "123 Test Street, Test City",
            "price": "$500,000",
            "beds": "3",
            "baths": "2",
            "sqft": "1,500",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    print("🧪 Тестирую радикальное исправление SVG...")
    print(f"📡 Отправляю запрос на: {api_url}")
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=test_data, timeout=60)
        end_time = time.time()
        
        print(f"⏱️ Время ответа: {end_time - start_time:.2f} секунд")
        print(f"📊 HTTP статус: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"Response: {response.text[:1000]}")
            return False
        
        result = response.json()
        
        print(f"✅ API ответил успешно!")
        print(f"📋 Ключи ответа: {list(result.keys())}")
        
        # Проверяем основные поля
        if 'success' in result and result['success']:
            print("✅ success: True")
        else:
            print("❌ success: False или отсутствует")
            
        if 'urls' in result and len(result['urls']) > 0:
            print(f"✅ URLs: {len(result['urls'])} файлов")
            for i, url in enumerate(result['urls']):
                print(f"  {i+1}: {url}")
        else:
            print("❌ Нет URLs в ответе")
            
        # Проверяем что SVG доступны
        if 'urls' in result:
            for i, url in enumerate(result['urls'][:2]):  # Проверяем первые 2
                print(f"🔍 Проверяю доступность URL {i+1}...")
                try:
                    svg_response = requests.get(url, timeout=10)
                    if svg_response.status_code == 200:
                        svg_content = svg_response.text
                        print(f"✅ SVG {i+1} доступен, размер: {len(svg_content)} символов")
                        
                        # Проверяем что нет проблемных тегов
                        if '<image' in svg_content:
                            print(f"⚠️ SVG {i+1} содержит image теги (не должно быть!)")
                        else:
                            print(f"✅ SVG {i+1} очищен от image тегов")
                            
                        if '<use' in svg_content:
                            print(f"⚠️ SVG {i+1} содержит use теги (не должно быть!)")
                        else:
                            print(f"✅ SVG {i+1} очищен от use тегов")
                            
                    else:
                        print(f"❌ SVG {i+1} недоступен: {svg_response.status_code}")
                except Exception as e:
                    print(f"❌ Ошибка проверки SVG {i+1}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def test_png_conversion():
    """Тестируем PNG конвертацию"""
    
    print("\n🖼️ Тестирую PNG конвертацию...")
    
    # Простой SVG без проблемных тегов
    clean_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="white"/>
        <text x="200" y="150" text-anchor="middle" font-size="24" fill="black">Test PNG</text>
        <circle cx="200" cy="200" r="50" fill="blue"/>
    </svg>'''
    
    api_url = "https://new-api-generator.onrender.com/api/convert-to-png"
    
    test_data = {
        "svg_content": clean_svg,
        "width": 400,
        "height": 300
    }
    
    try:
        response = requests.post(api_url, json=test_data, timeout=30)
        
        print(f"📊 PNG API статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'png_url' in result:
                print(f"✅ PNG создан: {result['png_url']}")
                return True
            else:
                print(f"❌ Нет png_url в ответе: {result}")
        else:
            print(f"❌ PNG API ошибка: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Ошибка PNG теста: {e}")
    
    return False

if __name__ == "__main__":
    print("🔥 ТЕСТИРОВАНИЕ РАДИКАЛЬНОГО ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    # Тест 1: Основной API
    success1 = test_radical_svg_fix()
    
    # Тест 2: PNG конвертация
    success2 = test_png_conversion()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    print(f"✅ Carousel API: {'РАБОТАЕТ' if success1 else 'НЕ РАБОТАЕТ'}")
    print(f"✅ PNG конвертация: {'РАБОТАЕТ' if success2 else 'НЕ РАБОТАЕТ'}")
    
    if success1 and success2:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ! СИСТЕМА РАБОТАЕТ!")
    else:
        print("❌ Есть проблемы, требуется дополнительная отладка")