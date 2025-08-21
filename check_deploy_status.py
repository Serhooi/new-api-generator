#!/usr/bin/env python3
"""
Проверка статуса деплоя по логам
"""

import requests
import time

def check_deploy_status():
    """Проверяем задеплоились ли наши изменения"""
    
    print("🔍 ПРОВЕРКА СТАТУСА ДЕПЛОЯ")
    print("=" * 30)
    
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "Deploy Test",
            "price": "$1,234,567",
            "beds": "4",
            "baths": "3",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    try:
        print("📡 Отправляю запрос для проверки логов...")
        response = requests.post(api_url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API отвечает")
            
            # Проверяем формат ответа
            format_type = result.get('format', 'unknown')
            print(f"📋 Формат: {format_type}")
            
            if format_type == 'png':
                print("🎉 ДЕПЛОЙ ЗАВЕРШЕН! PNG создание работает!")
                return True
            elif format_type == 'svg':
                print("⏳ Деплой еще не завершен - все еще SVG формат")
                print("💡 Нужно подождать еще немного")
                return False
            
            # Ищем PNG URLs
            png_found = False
            for key, value in result.items():
                if 'png' in key.lower() and isinstance(value, str):
                    print(f"🖼️ PNG найден: {key}")
                    png_found = True
            
            if png_found:
                print("🎉 PNG URLs найдены - деплой работает!")
                return True
            else:
                print("⏳ PNG URLs не найдены - деплой в процессе")
                return False
        
        else:
            print(f"❌ API ошибка: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def monitor_deploy():
    """Мониторим деплой каждые 30 секунд"""
    
    print("🔄 МОНИТОРИНГ ДЕПЛОЯ")
    print("=" * 25)
    
    max_attempts = 10  # 5 минут максимум
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔍 Попытка {attempt}/{max_attempts}")
        
        if check_deploy_status():
            print("\n🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
            return True
        
        if attempt < max_attempts:
            print("⏳ Жду 30 секунд до следующей проверки...")
            time.sleep(30)
    
    print("\n⏰ Время ожидания истекло")
    print("💡 Возможно деплой занимает больше времени")
    return False

if __name__ == "__main__":
    monitor_deploy()