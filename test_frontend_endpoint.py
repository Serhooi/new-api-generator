#!/usr/bin/env python3
"""
Тестируем эндпоинт который использует фронтенд
"""

import requests
import json

def test_frontend_carousel_endpoint():
    """Тестируем эндпоинт /generate-carousel как использует фронтенд"""
    
    url = "https://new-api-generator-1.onrender.com/generate-carousel"
    
    # Данные в формате, который ожидает фронтенд
    test_data = {
        "main_template_name": "propertyimage2",
        "photo_template_name": "propertyimage2", 
        "slides_count": 1,
        "replacements": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем эндпоинт /generate-carousel (как фронтенд)...")
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем запрос с таймаутом
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ!")
            print(f"📁 Количество файлов: {len(result.get('files', []))}")
            print(f"🆔 ID карусели: {result.get('carousel_id', 'N/A')}")
            
            # Показываем файлы
            files = result.get('files', [])
            for i, file_info in enumerate(files):
                print(f"📄 Файл {i+1}: {file_info.get('filename', 'N/A')}")
                print(f"   URL: {file_info.get('url', 'N/A')}")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут запроса (60 секунд)")
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    test_frontend_carousel_endpoint()