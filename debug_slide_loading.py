#!/usr/bin/env python3
"""
Отладка загрузки слайдов
"""

import requests
import json
import re

def test_carousel_creation():
    """Тестируем создание карусели и проверяем URL слайдов"""
    
    print("🧪 ТЕСТ СОЗДАНИЯ КАРУСЕЛИ И ПРОВЕРКИ URL")
    print("=" * 60)
    
    # Данные для тестирования
    test_data = {
        "dyno.agentName": "Тест Агент",
        "dyno.agentPhone": "+1234567890", 
        "dyno.agentEmail": "test@example.com",
        "dyno.price": "$500,000",
        "dyno.propertyAddress": "123 Test Street",
        "dyno.bedrooms": "3",
        "dyno.bathrooms": "2",
        "dyno.date": "Aug 12, 2025",
        "dyno.time": "2:00 PM",
        "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
        "dyno.propertyimage2": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300", 
        "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face",
        "dyno.logo": "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=142&h=56",
        "dyno.propertyfeatures": "Бассейн, гараж, сад"
    }
    
    try:
        print("📤 Отправляю запрос на создание карусели...")
        
        response = requests.post(
            'http://localhost:5000/api/carousel/create-and-generate',
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Карусель создана успешно!")
            print(f"🆔 ID карусели: {result.get('carousel_id', 'N/A')}")
            
            # Проверяем созданные слайды
            slides = result.get('slides', [])
            print(f"📊 Создано слайдов: {len(slides)}")
            
            for i, slide in enumerate(slides):
                slide_type = slide.get('type', 'unknown')
                slide_url = slide.get('url', 'N/A')
                
                print(f"\n📋 Слайд {i+1} ({slide_type}):")
                print(f"   URL: {slide_url}")
                
                # Проверяем доступность URL
                if slide_url and slide_url != 'N/A':
                    check_slide_url(slide_url, i+1)
                else:
                    print("   ❌ URL отсутствует")
            
            return result
            
        else:
            print(f"❌ Ошибка сервера: {response.status_code}")
            print(f"📄 Ответ: {response.text[:500]}...")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python3 app.py")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def check_slide_url(url, slide_num):
    """Проверяем доступность URL слайда"""
    
    try:
        print(f"   🔍 Проверяю доступность слайда {slide_num}...")
        
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            content = response.text
            size = len(content)
            print(f"   ✅ Доступен: {size} символов")
            
            # Проверяем что это SVG
            if content.strip().startswith('<?xml') or content.strip().startswith('<svg'):
                print("   ✅ Это SVG файл")
                
                # Проверяем наличие изображений в SVG
                image_count = content.count('<image')
                base64_count = content.count('data:image/')
                print(f"   📊 Image элементов: {image_count}")
                print(f"   📊 Base64 изображений: {base64_count}")
                
                # Проверяем размеры SVG
                width_match = re.search(r'width="([^"]*)"', content)
                height_match = re.search(r'height="([^"]*)"', content)
                if width_match and height_match:
                    print(f"   📐 Размеры: {width_match.group(1)} x {height_match.group(1)}")
                
            else:
                print("   ❌ Не SVG файл")
                print(f"   📄 Начало: {content[:100]}...")
                
        elif response.status_code == 403:
            print("   ❌ Доступ запрещен (403) - проблема с CORS или авторизацией")
        elif response.status_code == 404:
            print("   ❌ Файл не найден (404)")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Таймаут при загрузке")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

def test_supabase_access():
    """Тестируем доступ к Supabase"""
    
    print("\n🧪 ТЕСТ ДОСТУПА К SUPABASE")
    print("=" * 50)
    
    # Тестовый URL Supabase (из предыдущих логов)
    test_url = "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/images/carousel/"
    
    try:
        print(f"🔍 Проверяю доступ к Supabase: {test_url}")
        
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase доступен")
        elif response.status_code == 404:
            print("⚠️ Путь не найден, но Supabase доступен")
        else:
            print(f"❌ Проблема с Supabase: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка доступа к Supabase: {e}")

def main():
    """Запускаем отладку"""
    
    print("🚀 ОТЛАДКА ЗАГРУЗКИ СЛАЙДОВ")
    print("=" * 70)
    print("⚠️  Убедитесь что сервер запущен: python3 app.py")
    print()
    
    # Тестируем Supabase
    test_supabase_access()
    
    # Создаем карусель и проверяем слайды
    result = test_carousel_creation()
    
    print("\n🎯 ОТЛАДКА ЗАВЕРШЕНА!")
    
    if result:
        print("\n📋 РЕКОМЕНДАЦИИ:")
        print("1. Проверьте что все URL слайдов доступны")
        print("2. Убедитесь что SVG файлы содержат изображения")
        print("3. Проверьте CORS настройки Supabase")
        print("4. Убедитесь что фронтенд использует правильные URL")
    else:
        print("\n❌ ПРОБЛЕМЫ:")
        print("1. Сервер не отвечает или есть ошибки")
        print("2. Проверьте логи сервера")
        print("3. Убедитесь что все зависимости установлены")

if __name__ == "__main__":
    main()