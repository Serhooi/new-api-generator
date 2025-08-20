#!/usr/bin/env python3
"""
Тест PNG генерации
"""

import requests
import json

def test_png_endpoints():
    """Тестируем все PNG endpoints"""
    
    print("🖼️ ТЕСТ PNG ГЕНЕРАЦИИ")
    print("=" * 50)
    
    # Проверяем сервер
    try:
        health = requests.get("http://localhost:5000/api/health", timeout=5)
        if health.status_code != 200:
            print("❌ Сервер не работает")
            return
    except:
        print("❌ Сервер недоступен")
        return
    
    print("✅ Сервер работает")
    
    # Получаем шаблоны
    try:
        templates_response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
        if templates_response.status_code != 200:
            print("❌ Не удалось получить шаблоны")
            return
        
        templates = templates_response.json().get('templates', [])
        main_template = None
        photo_template = None
        
        for template in templates:
            if template.get('template_role') == 'main':
                main_template = template
            elif template.get('template_role') == 'photo':
                photo_template = template
        
        if not main_template or not photo_template:
            print("❌ Не найдены шаблоны")
            return
        
        print(f"✅ Main: {main_template['name']}")
        print(f"✅ Photo: {photo_template['name']}")
        
    except Exception as e:
        print(f"❌ Ошибка получения шаблонов: {e}")
        return
    
    # Тестовые данные
    test_data = {
        "main_template_id": main_template['id'],
        "photo_template_id": photo_template['id'],
        "data": {
            "dyno.propertyaddress": "123 PNG Test Street",
            "dyno.price": "$750,000",
            "dyno.name": "PNG Tester"
        }
    }
    
    # Тест 1: Обычный endpoint с format=png
    print("\\n🧪 ТЕСТ 1: /api/generate/carousel с format=png")
    test_data_with_format = test_data.copy()
    test_data_with_format['format'] = 'png'
    
    try:
        response1 = requests.post(
            "http://localhost:5000/api/generate/carousel",
            json=test_data_with_format,
            timeout=60
        )
        
        print(f"📊 Статус: {response1.status_code}")
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"✅ Успех: {result1.get('success')}")
            print(f"📄 Формат: {result1.get('format')}")
            
            images1 = result1.get('images', [])
            print(f"🖼️ Изображений: {len(images1)}")
            
            for i, url in enumerate(images1):
                print(f"  {i+1}. {url}")
                if '.png' in url:
                    print(f"     ✅ PNG файл")
                else:
                    print(f"     ❌ Не PNG файл")
        else:
            print(f"❌ Ошибка: {response1.text}")
            
    except Exception as e:
        print(f"❌ Ошибка теста 1: {e}")
    
    # Тест 2: PNG endpoint
    print("\\n🧪 ТЕСТ 2: /api/generate/carousel-png")
    
    try:
        response2 = requests.post(
            "http://localhost:5000/api/generate/carousel-png",
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Статус: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✅ Успех: {result2.get('success')}")
            print(f"📄 Формат: {result2.get('format')}")
            
            images2 = result2.get('images', [])
            print(f"🖼️ Изображений: {len(images2)}")
            
            for i, url in enumerate(images2):
                print(f"  {i+1}. {url}")
                if '.png' in url:
                    print(f"     ✅ PNG файл")
                else:
                    print(f"     ❌ Не PNG файл")
        else:
            print(f"❌ Ошибка: {response2.text}")
            
    except Exception as e:
        print(f"❌ Ошибка теста 2: {e}")
    
    # Тест 3: Simple PNG endpoint
    print("\\n🧪 ТЕСТ 3: /api/generate/carousel-png-simple")
    
    try:
        response3 = requests.post(
            "http://localhost:5000/api/generate/carousel-png-simple",
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Статус: {response3.status_code}")
        
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"✅ Успех: {result3.get('success')}")
            print(f"📄 Формат: {result3.get('format')}")
            
            images3 = result3.get('images', [])
            print(f"🖼️ Изображений: {len(images3)}")
            
            for i, url in enumerate(images3):
                print(f"  {i+1}. {url}")
                if '.png' in url:
                    print(f"     ✅ PNG файл")
                    
                    # Проверяем доступность
                    try:
                        check_response = requests.head(url, timeout=10)
                        print(f"     📊 Доступность: {check_response.status_code}")
                        
                        if check_response.status_code == 200:
                            content_type = check_response.headers.get('content-type', 'unknown')
                            print(f"     📄 Content-Type: {content_type}")
                            
                            if 'png' in content_type:
                                print(f"     ✅ Правильный Content-Type")
                            else:
                                print(f"     ⚠️ Content-Type не PNG")
                        else:
                            print(f"     ❌ Файл недоступен")
                    except Exception as e:
                        print(f"     ❌ Ошибка проверки: {e}")
                else:
                    print(f"     ❌ Не PNG файл")
        else:
            print(f"❌ Ошибка: {response3.text}")
            
    except Exception as e:
        print(f"❌ Ошибка теста 3: {e}")

if __name__ == "__main__":
    test_png_endpoints()