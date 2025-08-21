#!/usr/bin/env python3
"""
Финальный тест всей системы с реальными данными
"""

import requests
import time
import subprocess
import os

def test_real_carousel_generation():
    """Тестируем реальную генерацию карусели"""
    
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ СИСТЕМЫ")
    print("=" * 50)
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    # Реальные данные для теста
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "1234 Sunset Boulevard, Los Angeles, CA 90028",
            "price": "$2,500,000",
            "beds": "4",
            "baths": "3",
            "sqft": "2,800",
            "propertyfeatures": "Pool, Garage, Garden, Modern Kitchen",
            "name": "John Smith",
            "phone": "+1 (555) 123-4567",
            "email": "john.smith@realestate.com",
            "date": "March 15, 2025",
            "time": "2:00 PM - 5:00 PM",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1200&h=800&fit=crop",
            "agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face"
        }
    }
    
    print("📡 Отправляю запрос на генерацию карусели...")
    print(f"🏠 Адрес: {test_data['data']['propertyaddress']}")
    print(f"💰 Цена: {test_data['data']['price']}")
    print(f"🖼️ Изображения: propertyimage2 + agentheadshot")
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=test_data, timeout=120)
        end_time = time.time()
        
        print(f"⏱️ Время ответа: {end_time - start_time:.2f} секунд")
        print(f"📊 HTTP статус: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"Response: {response.text[:1000]}")
            return False
        
        result = response.json()
        
        print(f"✅ API ответил успешно!")
        
        # Проверяем основные поля
        if result.get('success'):
            print("✅ success: True")
        else:
            print("❌ success: False")
            return False
        
        # Проверяем URLs
        if 'urls' in result and len(result['urls']) >= 2:
            print(f"✅ URLs: {len(result['urls'])} файлов")
            main_svg_url = result['urls'][0]
            photo_svg_url = result['urls'][1]
            
            print(f"📄 Main SVG: {main_svg_url}")
            print(f"📄 Photo SVG: {photo_svg_url}")
        else:
            print("❌ Недостаточно URLs в ответе")
            return False
        
        # Проверяем PNG URLs
        png_urls = []
        if 'images_detailed' in result:
            for img in result['images_detailed']:
                if 'png_url' in img:
                    png_urls.append(img['png_url'])
        
        print(f"🖼️ PNG URLs: {len(png_urls)}")
        for i, png_url in enumerate(png_urls):
            print(f"  {i+1}: {png_url}")
        
        # Тестируем доступность файлов
        print("\n🔍 Проверяю доступность файлов...")
        
        # Тест 1: Main SVG
        print("📄 Тестирую Main SVG...")
        svg_response = requests.get(main_svg_url, timeout=10)
        if svg_response.status_code == 200:
            main_svg_content = svg_response.text
            print(f"✅ Main SVG доступен: {len(main_svg_content)} символов")
            
            # Проверяем содержимое
            if 'data:image/' in main_svg_content:
                print("✅ Main SVG содержит изображения")
            else:
                print("⚠️ Main SVG не содержит изображений")
                
            # Проверяем данные
            if test_data['data']['propertyaddress'] in main_svg_content:
                print("✅ Main SVG содержит адрес")
            if test_data['data']['price'] in main_svg_content:
                print("✅ Main SVG содержит цену")
        else:
            print(f"❌ Main SVG недоступен: {svg_response.status_code}")
            return False
        
        # Тест 2: Photo SVG
        print("\n📄 Тестирую Photo SVG...")
        svg_response = requests.get(photo_svg_url, timeout=10)
        if svg_response.status_code == 200:
            photo_svg_content = svg_response.text
            print(f"✅ Photo SVG доступен: {len(photo_svg_content)} символов")
            
            # Проверяем содержимое
            if 'data:image/' in photo_svg_content:
                print("✅ Photo SVG содержит изображения")
            else:
                print("⚠️ Photo SVG не содержит изображений")
        else:
            print(f"❌ Photo SVG недоступен: {svg_response.status_code}")
            return False
        
        # Тест 3: PNG файлы
        print("\n🖼️ Тестирую PNG файлы...")
        png_success = 0
        for i, png_url in enumerate(png_urls):
            try:
                png_response = requests.get(png_url, timeout=10)
                if png_response.status_code == 200:
                    png_size = len(png_response.content)
                    print(f"✅ PNG {i+1} доступен: {png_size} байт")
                    
                    if png_size > 50000:  # Больше 50KB = вероятно с изображениями
                        print(f"🎉 PNG {i+1} большой - содержит изображения!")
                    else:
                        print(f"⚠️ PNG {i+1} маленький - возможно без изображений")
                    
                    png_success += 1
                else:
                    print(f"❌ PNG {i+1} недоступен: {png_response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка PNG {i+1}: {e}")
        
        # Итоговая оценка
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
        
        total_score = 0
        max_score = 6
        
        if result.get('success'):
            total_score += 1
            print("✅ API работает")
        
        if len(result.get('urls', [])) >= 2:
            total_score += 1
            print("✅ SVG файлы созданы")
        
        if 'data:image/' in main_svg_content:
            total_score += 1
            print("✅ Main SVG с изображениями")
        
        if 'data:image/' in photo_svg_content:
            total_score += 1
            print("✅ Photo SVG с изображениями")
        
        if png_success >= 1:
            total_score += 1
            print("✅ PNG файлы созданы")
        
        if png_success == len(png_urls) and png_success >= 2:
            total_score += 1
            print("✅ Все PNG файлы работают")
        
        print(f"\n🎯 ОБЩИЙ СЧЕТ: {total_score}/{max_score}")
        
        if total_score == max_score:
            print("🎉 СИСТЕМА РАБОТАЕТ ИДЕАЛЬНО!")
            return True
        elif total_score >= 4:
            print("✅ Система работает хорошо")
            return True
        else:
            print("❌ Система требует доработки")
            return False
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def test_png_conversion_api():
    """Тестируем PNG конвертацию API"""
    
    print("\n🖼️ ТЕСТ PNG КОНВЕРТАЦИИ")
    print("=" * 30)
    
    api_url = "https://new-api-generator.onrender.com/api/convert-to-png"
    
    # Простой SVG для теста
    test_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="white"/>
        <text x="200" y="150" text-anchor="middle" font-size="24" fill="black">PNG Test</text>
        <circle cx="200" cy="200" r="50" fill="blue"/>
    </svg>'''
    
    # Используем один из созданных SVG URL
    test_data = {
        "svg_url": "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-assets/carousel/carousel_ac98294f-2e10-4d94-816b-4ac84a39b411_main.svg",
        "width": 400,
        "height": 300
    }
    
    try:
        response = requests.post(api_url, json=test_data, timeout=30)
        
        print(f"📊 PNG API статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'png_url' in result:
                png_url = result['png_url']
                print(f"✅ PNG создан: {png_url}")
                
                # Проверяем доступность
                png_response = requests.get(png_url, timeout=10)
                if png_response.status_code == 200:
                    png_size = len(png_response.content)
                    print(f"✅ PNG доступен: {png_size} байт")
                    return True
                else:
                    print(f"❌ PNG недоступен: {png_response.status_code}")
            else:
                print(f"❌ Нет png_url в ответе: {result}")
        else:
            print(f"❌ PNG API ошибка: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Ошибка PNG теста: {e}")
    
    return False

def main():
    """Основная функция тестирования"""
    
    print("🚀 ЗАПУСК ФИНАЛЬНОГО ТЕСТА СИСТЕМЫ")
    print("🕐 Время начала:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Тест 1: Основная генерация карусели
    carousel_success = test_real_carousel_generation()
    
    # Тест 2: PNG конвертация
    png_success = test_png_conversion_api()
    
    # Финальный отчет
    print("\n" + "=" * 60)
    print("🏁 ФИНАЛЬНЫЙ ОТЧЕТ")
    print("=" * 60)
    
    print(f"🎠 Генерация карусели: {'✅ РАБОТАЕТ' if carousel_success else '❌ НЕ РАБОТАЕТ'}")
    print(f"🖼️ PNG конвертация: {'✅ РАБОТАЕТ' if png_success else '❌ НЕ РАБОТАЕТ'}")
    
    if carousel_success and png_success:
        print("\n🎉 ВСЯ СИСТЕМА РАБОТАЕТ ИДЕАЛЬНО!")
        print("🚀 Готово к продакшену!")
    elif carousel_success:
        print("\n✅ Основная функциональность работает")
        print("⚠️ PNG конвертация требует внимания")
    else:
        print("\n❌ Система требует исправлений")
    
    print(f"🕐 Время завершения: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()