#!/usr/bin/env python3
"""
Тестируем карусель с правильными ID шаблонов
"""

import requests
import json

def test_carousel_with_correct_ids():
    """Тестируем карусель с правильными UUID"""
    
    url = "https://new-api-generator-1.onrender.com/api/generate/carousel"
    
    # Используем правильные UUID из базы данных
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",  # Main Template
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d",  # Photo Template
        "data": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем карусель с правильными UUID...")
    print(f"URL: {url}")
    print(f"Main Template ID: {test_data['main_template_id']}")
    print(f"Photo Template ID: {test_data['photo_template_id']}")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ!")
            print(f"📋 Полный ответ: {json.dumps(result, indent=2)}")
            
            files = result.get('files', [])
            print(f"📁 Количество файлов: {len(files)}")
            
            for i, file_info in enumerate(files):
                print(f"📄 Файл {i+1}: {file_info.get('filename', 'N/A')}")
                print(f"   URL: {file_info.get('url', 'N/A')}")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    test_carousel_with_correct_ids()