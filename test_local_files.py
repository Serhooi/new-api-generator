#!/usr/bin/env python3
"""
Тест локального сохранения файлов
"""

import requests
import json
import os

def test_local_carousel():
    """Тестируем создание карусели с локальным сохранением"""
    
    print("🧪 ТЕСТ ЛОКАЛЬНОГО СОХРАНЕНИЯ КАРУСЕЛИ")
    print("=" * 60)
    
    # Проверяем что output директория существует
    output_dir = "output/carousel"
    if not os.path.exists(output_dir):
        print(f"📁 Создаю директорию: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    else:
        print(f"📁 Директория существует: {output_dir}")
    
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
                
                # Если это локальный файл, проверяем его существование
                if slide_url.startswith('http://localhost:5000/output/'):
                    local_path = slide_url.replace('http://localhost:5000/', '')
                    if os.path.exists(local_path):
                        file_size = os.path.getsize(local_path)
                        print(f"   ✅ Локальный файл существует: {file_size} байт")
                        
                        # Проверяем содержимое
                        with open(local_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip().startswith('<?xml') or content.strip().startswith('<svg'):
                                print("   ✅ Это SVG файл")
                                
                                # Проверяем наличие изображений
                                base64_count = content.count('data:image/')
                                print(f"   📊 Base64 изображений: {base64_count}")
                            else:
                                print("   ❌ Не SVG файл")
                    else:
                        print(f"   ❌ Локальный файл не найден: {local_path}")
                
                # Проверяем доступность через HTTP
                check_slide_accessibility(slide_url, i+1)
            
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

def check_slide_accessibility(url, slide_num):
    """Проверяем доступность слайда через HTTP"""
    
    try:
        print(f"   🌐 Проверяю HTTP доступность...")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            content = response.text
            size = len(content)
            print(f"   ✅ HTTP доступен: {size} символов")
            
            if 'data:image/' in content:
                base64_count = content.count('data:image/')
                print(f"   ✅ Содержит {base64_count} base64 изображений")
            else:
                print("   ⚠️ Не содержит base64 изображений")
                
        else:
            print(f"   ❌ HTTP ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ HTTP ошибка: {e}")

def main():
    """Запускаем тест"""
    
    print("🚀 ТЕСТ ЛОКАЛЬНОГО СОХРАНЕНИЯ")
    print("=" * 70)
    print("⚠️  Убедитесь что сервер запущен: python3 app.py")
    print()
    
    result = test_local_carousel()
    
    print("\n🎯 ТЕСТ ЗАВЕРШЕН!")
    
    if result:
        print("\n✅ УСПЕХ!")
        print("📋 ПРОВЕРЬТЕ:")
        print("1. Все слайды должны быть доступны по HTTP")
        print("2. SVG файлы должны содержать base64 изображения")
        print("3. Фронтенд должен загружать слайды без ошибок")
    else:
        print("\n❌ ПРОБЛЕМЫ:")
        print("1. Проверьте что сервер запущен")
        print("2. Проверьте логи сервера на ошибки")
        print("3. Убедитесь что директории созданы")

if __name__ == "__main__":
    main()