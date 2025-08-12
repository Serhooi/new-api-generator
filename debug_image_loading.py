#!/usr/bin/env python3
"""
Отладка загрузки изображений
"""

import requests
import time

def test_image_urls():
    """Тестируем доступность URL изображений"""
    
    print("🧪 ТЕСТ ДОСТУПНОСТИ ИЗОБРАЖЕНИЙ")
    print("=" * 50)
    
    test_urls = [
        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300", 
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face",
        "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=142&h=56"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📥 Тест {i}: {url[:50]}...")
        
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                size = len(response.content)
                print(f"✅ Доступно: {size} байт")
                
                # Проверяем что это изображение
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"✅ Тип: {content_type}")
                else:
                    print(f"⚠️ Неожиданный тип: {content_type}")
            else:
                print(f"❌ Ошибка: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ Таймаут")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def test_download_and_convert():
    """Тестируем функцию download_and_convert_image"""
    
    print("\n🧪 ТЕСТ КОНВЕРТАЦИИ ИЗОБРАЖЕНИЙ")
    print("=" * 50)
    
    try:
        from preview_system import download_and_convert_image
        
        test_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&h=120&fit=crop&crop=face"
        
        print(f"🔄 Конвертирую: {test_url[:50]}...")
        
        result = download_and_convert_image(test_url)
        
        if result and result.startswith('data:image/'):
            print(f"✅ Конвертировано в base64: {len(result)} символов")
            print(f"📋 Начало: {result[:50]}...")
        else:
            print(f"❌ Конвертация не удалась: {result}")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Запускаем все тесты"""
    
    print("🚀 ОТЛАДКА ЗАГРУЗКИ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    
    test_image_urls()
    test_download_and_convert()
    
    print("\n🎯 ОТЛАДКА ЗАВЕРШЕНА!")

if __name__ == "__main__":
    main()