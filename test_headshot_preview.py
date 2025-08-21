#!/usr/bin/env python3
"""
Тест превью хедшота - проверяем что происходит
"""

import requests
import json

def test_headshot_preview():
    """Тестируем превью с хедшотом"""
    print("🧪 ТЕСТ ПРЕВЬЮ ХЕДШОТА")
    print("=" * 50)
    
    # Тестовые данные с хедшотом
    test_data = {
        "template": "main",
        "data": {
            "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            "dyno.name": "John Smith",
            "dyno.title": "Real Estate Agent"
        }
    }
    
    try:
        # Запрос превью
        print("📤 Отправляю запрос на превью...")
        response = requests.post(
            'http://localhost:8000/api/preview',
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Превью создано успешно!")
            print(f"🔗 URL: {result.get('preview_url', 'N/A')}")
            print(f"📏 Размер: {result.get('width', 'N/A')}x{result.get('height', 'N/A')}")
            
            if 'preview_url' in result:
                print(f"\n🌐 Открой в браузере: http://localhost:8000{result['preview_url']}")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запусти: python app.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_headshot_preview()