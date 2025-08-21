#!/usr/bin/env python3
"""
Проверка создания PNG файлов в основном API
"""

import requests
import time

def check_png_creation():
    """Проверяем создаются ли PNG автоматически"""
    
    print("🔍 ПРОВЕРКА СОЗДАНИЯ PNG")
    print("=" * 30)
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "Test Address",
            "price": "$1,000,000",
            "beds": "3",
            "baths": "2",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    try:
        response = requests.post(api_url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📋 Полный ответ API:")
            for key, value in result.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                elif isinstance(value, list):
                    print(f"  {key}: [{len(value)} элементов]")
                    for i, item in enumerate(value[:3]):
                        if isinstance(item, dict):
                            print(f"    [{i}]: {list(item.keys())}")
                        else:
                            print(f"    [{i}]: {item}")
                else:
                    print(f"  {key}: {value}")
            
            # Ищем PNG URLs в разных местах
            png_urls = []
            
            # Проверяем images_detailed
            if 'images_detailed' in result:
                for img in result['images_detailed']:
                    if isinstance(img, dict):
                        for key, value in img.items():
                            if 'png' in key.lower() and isinstance(value, str):
                                png_urls.append(value)
            
            # Проверяем другие поля
            for key, value in result.items():
                if 'png' in key.lower() and isinstance(value, str):
                    png_urls.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and '.png' in item:
                            png_urls.append(item)
            
            print(f"\n🖼️ Найдено PNG URLs: {len(png_urls)}")
            for png_url in png_urls:
                print(f"  - {png_url}")
            
            # Проверяем доступность PNG
            if png_urls:
                for i, png_url in enumerate(png_urls):
                    try:
                        png_response = requests.get(png_url, timeout=10)
                        if png_response.status_code == 200:
                            size = len(png_response.content)
                            print(f"✅ PNG {i+1} работает: {size} байт")
                        else:
                            print(f"❌ PNG {i+1} недоступен: {png_response.status_code}")
                    except Exception as e:
                        print(f"❌ Ошибка PNG {i+1}: {e}")
            else:
                print("⚠️ PNG URLs не найдены - возможно PNG не создаются автоматически")
                
                # Проверяем есть ли ошибки в логах
                print("\n🔍 Возможные причины:")
                print("  1. PNG создание отключено")
                print("  2. Ошибки в rsvg-convert")
                print("  3. PNG создаются но URLs не возвращаются")
        
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_png_creation()