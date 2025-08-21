#!/usr/bin/env python3
"""
Тестируем простой эндпоинт для одиночного изображения
"""

import requests
import json

def test_single_generation():
    """Тестируем /api/generate/single"""
    
    url = "https://new-api-generator-1.onrender.com/api/generate/single"
    
    # Минимальные данные
    test_data = {
        "template_id": "propertyimage2",
        "replacements": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем /api/generate/single...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ!")
            print(f"📄 Файл: {result.get('filename', 'N/A')}")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    test_single_generation()