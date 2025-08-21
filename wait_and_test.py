#!/usr/bin/env python3
"""
Ждем деплой и тестируем систему
"""

import requests
import time

def wait_for_deploy_and_test():
    """Ждем деплой и тестируем"""
    
    print("⏳ Ожидаю завершения деплоя на Render...")
    print("🕐 Подождем 2 минуты для деплоя...")
    
    # Ждем 2 минуты
    for i in range(120, 0, -10):
        print(f"⏳ Осталось {i} секунд...")
        time.sleep(10)
    
    print("\n🧪 Тестирую систему после деплоя...")
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "Test After Deploy",
            "price": "$999,999",
            "beds": "3",
            "baths": "2",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    try:
        print("📡 Отправляю тестовый запрос...")
        response = requests.post(api_url, json=test_data, timeout=60)
        
        print(f"📊 HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ API работает")
                
                # Ищем PNG URLs
                png_found = False
                for key, value in result.items():
                    if 'png' in key.lower():
                        print(f"🖼️ Найден PNG: {key} = {value}")
                        png_found = True
                
                if 'images_detailed' in result:
                    for img in result['images_detailed']:
                        if isinstance(img, dict):
                            for k, v in img.items():
                                if 'png' in k.lower():
                                    print(f"🖼️ Найден PNG в images_detailed: {k} = {v}")
                                    png_found = True
                
                if png_found:
                    print("🎉 PNG создание работает после деплоя!")
                else:
                    print("⚠️ PNG URLs все еще не найдены")
                    print("💡 Возможно нужно больше времени или есть ошибки в логах")
            else:
                print("❌ API вернул success: false")
        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(response.text[:500])
    
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

if __name__ == "__main__":
    wait_for_deploy_and_test()