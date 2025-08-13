#!/usr/bin/env python3
"""
Быстрый тест исправлений
"""

import os
import requests
import json

def test_environment_setup():
    """Проверяем настройку окружения"""
    
    print("🔍 ПРОВЕРКА НАСТРОЙКИ ОКРУЖЕНИЯ")
    print("=" * 50)
    
    # Проверяем переменные
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    print(f"📋 SUPABASE_URL: {'✅ установлена' if supabase_url else '❌ не установлена'}")
    print(f"📋 SUPABASE_ANON_KEY: {'✅ установлена' if supabase_key else '❌ не установлена'}")
    
    if supabase_url:
        print(f"🌐 URL: {supabase_url}")
    
    # Определяем логику is_render
    is_render = os.environ.get('RENDER', False) or bool(supabase_url)
    print(f"🎯 is_render: {is_render}")
    
    if is_render:
        print("✅ Файлы будут загружаться в Supabase")
    else:
        print("📁 Файлы будут сохраняться локально")
    
    return supabase_url, supabase_key, is_render

def test_server_health():
    """Проверяем работу сервера"""
    
    print("\\n🏥 ПРОВЕРКА СЕРВЕРА")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Сервер работает")
            return True
        else:
            print("❌ Сервер не отвечает правильно")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Сервер недоступен: {e}")
        return False

def test_simple_generation():
    """Простой тест генерации"""
    
    print("\\n🧪 ПРОСТОЙ ТЕСТ ГЕНЕРАЦИИ")
    print("=" * 40)
    
    # Минимальные данные для теста
    test_data = {
        "main_template_id": "test-main",
        "photo_template_id": "test-photo", 
        "data": {
            "dyno.propertyaddress": "Test Address",
            "dyno.price": "$100,000"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/generate/carousel",
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация успешна")
            
            # Проверяем основные поля
            if 'images' in result:
                print(f"🖼️ Изображений: {len(result['images'])}")
                for i, url in enumerate(result['images']):
                    print(f"  {i+1}. {url}")
            
            if 'carousel_id' in result:
                print(f"🆔 Carousel ID: {result['carousel_id']}")
            
            return True
            
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🚀 БЫСТРЫЙ ТЕСТ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    # Тест 1: Окружение
    supabase_url, supabase_key, is_render = test_environment_setup()
    
    # Тест 2: Сервер
    server_ok = test_server_health()
    
    if not server_ok:
        print("\\n❌ Сервер не работает, остальные тесты невозможны")
        return
    
    # Тест 3: Генерация
    generation_ok = test_simple_generation()
    
    # Итоги
    print("\\n📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    print(f"🌐 Supabase настроен: {'✅' if supabase_url and supabase_key else '❌'}")
    print(f"🏥 Сервер работает: {'✅' if server_ok else '❌'}")
    print(f"🧪 Генерация работает: {'✅' if generation_ok else '❌'}")
    
    if supabase_url and supabase_key and server_ok and generation_ok:
        print("\\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("\\n⚠️ Есть проблемы, требуется дополнительная отладка")

if __name__ == "__main__":
    main()