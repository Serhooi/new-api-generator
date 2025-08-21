#!/usr/bin/env python3
"""
Тестируем с правильным ID шаблона
"""

import requests
import json

def test_with_correct_template_id():
    """Тестируем с правильным ID шаблона"""
    
    url = "https://new-api-generator-1.onrender.com/api/generate/single"
    
    # Используем правильный ID из базы данных
    test_data = {
        "template_id": "9cb08943-8d1e-440c-a712-92111ec23048",  # Main Template
        "replacements": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем с правильным ID шаблона...")
    print(f"URL: {url}")
    print(f"Template ID: {test_data['template_id']}")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ!")
            print(f"📋 Полный ответ: {json.dumps(result, indent=2)}")
            print(f"📄 Файл: {result.get('filename', 'N/A')}")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    test_with_correct_template_id()