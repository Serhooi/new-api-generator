#!/usr/bin/env python3
"""
Тестируем правильный эндпоинт для генерации карусели
"""

import requests
import json

def test_correct_carousel_endpoint():
    """Тестируем правильный эндпоинт /api/generate/carousel"""
    
    url = "https://new-api-generator-1.onrender.com/api/generate/carousel"
    
    # Минимальные данные для теста
    test_data = {
        "template_id": "propertyimage2",
        "data": {
            "headshot": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "propertyimage": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
            "text1": "Test Property",
            "text2": "123 Main St"
        }
    }
    
    print("🔍 Тестируем ПРАВИЛЬНЫЙ эндпоинт для генерации карусели...")
    print(f"URL: {url}")
    
    try:
        # Отправляем запрос с таймаутом
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ!")
            print(f"📁 Количество файлов: {len(result.get('files', []))}")
            print(f"🆔 ID карусели: {result.get('carousel_id', 'N/A')}")
            
            # Показываем первые несколько файлов
            files = result.get('files', [])
            for i, file_info in enumerate(files[:3]):
                print(f"📄 Файл {i+1}: {file_info.get('filename', 'N/A')}")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Таймаут запроса (60 секунд)")
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    test_correct_carousel_endpoint()