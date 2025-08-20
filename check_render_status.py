#!/usr/bin/env python3
"""
Проверяем разные варианты URL и статус Render
"""
import requests
import time

# Возможные URL
urls_to_try = [
    "https://new-api-generator-1.onrender.com",
    "https://new-api-generator.onrender.com", 
    "http://new-api-generator-1.onrender.com",
]

def check_url(url):
    """Проверяем конкретный URL"""
    print(f"\n🔍 Проверяю: {url}")
    
    try:
        # Пробуем основной endpoint
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Сервер доступен!")
            return True
        elif response.status_code == 404:
            print(f"   ❌ 404 - Сервер не найден")
        else:
            print(f"   ⚠️ Неожиданный статус: {response.status_code}")
            
    except requests.exceptions.ConnectTimeout:
        print(f"   ❌ Timeout - сервер не отвечает")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error - сервер недоступен")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    return False

def check_render_deployment():
    """Проверяем статус развертывания на Render"""
    
    print("🚀 Проверка статуса Render развертывания")
    print("=" * 50)
    print(f"⏰ Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    working_url = None
    
    for url in urls_to_try:
        if check_url(url):
            working_url = url
            break
    
    if working_url:
        print(f"\n✅ Рабочий URL найден: {working_url}")
        
        # Тестируем API endpoints
        print(f"\n🧪 Тестируем API endpoints на {working_url}")
        
        endpoints = [
            "/api/templates",
            "/api/generate/carousel", 
            "/api/generate/carousel-png",
            "/api/generate/carousel-png-simple"
        ]
        
        for endpoint in endpoints:
            try:
                if endpoint == "/api/templates":
                    response = requests.get(f"{working_url}{endpoint}", timeout=10)
                else:
                    response = requests.options(f"{working_url}{endpoint}", timeout=10)
                
                print(f"   {endpoint}: {response.status_code}")
                
            except Exception as e:
                print(f"   {endpoint}: ❌ {e}")
        
        return working_url
    else:
        print(f"\n❌ Ни один URL не работает")
        print(f"\n💡 Возможные причины:")
        print(f"   1. Развертывание еще не завершилось")
        print(f"   2. Ошибка в коде приложения")
        print(f"   3. Проблемы с Render сервисом")
        print(f"   4. Неправильный URL")
        
        return None

if __name__ == "__main__":
    working_url = check_render_deployment()
    
    if not working_url:
        print(f"\n🔧 Рекомендации:")
        print(f"   1. Проверьте логи развертывания в Render Dashboard")
        print(f"   2. Убедитесь что requirements.txt содержит все зависимости")
        print(f"   3. Проверьте переменные окружения")
        print(f"   4. Попробуйте повторное развертывание")