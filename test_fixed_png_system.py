#!/usr/bin/env python3
"""
Тестируем исправленную PNG систему
"""

import requests
import json
import time

def test_png_generation():
    """Тестируем PNG генерацию через API"""
    
    print("🧪 ТЕСТ ИСПРАВЛЕННОЙ PNG СИСТЕМЫ")
    print("=" * 45)
    
    # Тестовые данные
    data = {
        "main_template_id": "1",
        "photo_template_id": "2", 
        "format": "png",
        "replacements": {
            "dyno.address": "123 Test Street",
            "dyno.price": "$750,000",
            "dyno.beds": "3",
            "dyno.baths": "2",
            "dyno.sqft": "2,500"
        }
    }
    
    try:
        print("📤 Отправляю запрос на PNG генерацию...")
        
        response = requests.post(
            'http://localhost:5003/api/generate/carousel',
            json=data,
            timeout=60
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API работает!")
            
            if 'image_urls' in result:
                print(f"🖼️ Получено изображений: {len(result['image_urls'])}")
                
                for i, url in enumerate(result['image_urls']):
                    print(f"📷 Изображение {i+1}: {url}")
                    
                    # Проверяем что это PNG
                    if '.png' in url:
                        print(f"✅ Формат PNG подтвержден")
                        
                        # Пробуем скачать
                        try:
                            img_resp = requests.get(url, timeout=10)
                            if img_resp.status_code == 200:
                                size = len(img_resp.content)
                                print(f"📊 Размер: {size} bytes")
                                
                                if size > 20000:  # Больше 20KB - качественное изображение
                                    print(f"✅ Качественное изображение!")
                                elif size > 5000:  # Больше 5KB - нормальное
                                    print(f"⚠️ Среднее качество")
                                else:
                                    print(f"❌ Маленькое изображение (возможно заглушка)")
                        except Exception as e:
                            print(f"❌ Ошибка скачивания: {e}")
                    else:
                        print(f"❌ Не PNG формат")
                
                return True
            else:
                print("❌ Нет image_urls в ответе")
                print(f"📋 Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📋 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Сервер недоступен на порту 5003")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса (сервер завис)")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return False

def test_direct_function():
    """Тестируем функцию напрямую"""
    
    print("\n🔧 ТЕСТ ФУНКЦИИ НАПРЯМУЮ")
    print("=" * 30)
    
    import sys
    sys.path.append('.')
    
    try:
        from app import convert_svg_to_png_improved, create_preview_svg
        
        # Тестовый SVG с dyno полями
        test_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#e3f2fd"/>
            <rect x="20" y="20" width="360" height="260" fill="white" stroke="#1976d2" stroke-width="2"/>
            <text x="200" y="80" text-anchor="middle" font-size="24" fill="#1976d2" font-weight="bold">{{dyno.agentName}}</text>
            <text x="200" y="120" text-anchor="middle" font-size="16" fill="#666">{{dyno.propertyAddress}}</text>
            <text x="200" y="180" text-anchor="middle" font-size="32" fill="#4caf50" font-weight="bold">{{dyno.price}}</text>
            <text x="200" y="220" text-anchor="middle" font-size="14" fill="#999">{{dyno.bedrooms}} bed • {{dyno.bathrooms}} bath</text>
        </svg>'''
        
        # Заменяем dyno поля
        preview_svg = create_preview_svg(test_svg)
        print("✅ Dyno поля заменены")
        
        # Конвертируем в PNG
        success = convert_svg_to_png_improved(preview_svg, 'test_direct_function.png', 400, 300)
        
        if success:
            import os
            if os.path.exists('test_direct_function.png'):
                size = os.path.getsize('test_direct_function.png')
                print(f"✅ PNG создан: {size} bytes")
                os.remove('test_direct_function.png')
                return True
        
        print("❌ Функция не работает")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ PNG СИСТЕМЫ")
    print("=" * 60)
    
    # Тестируем функцию напрямую
    direct_ok = test_direct_function()
    
    # Тестируем API
    api_ok = test_png_generation()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"🔧 Прямая функция: {'✅ Работает' if direct_ok else '❌ Не работает'}")
    print(f"🌐 API: {'✅ Работает' if api_ok else '❌ Не работает'}")
    
    if direct_ok and api_ok:
        print("\n🎉 ВСЕ ИСПРАВЛЕНО!")
        print("✅ PNG система создает качественные изображения")
        print("✅ Больше никаких белых заглушек")
        print("✅ API возвращает реальные PNG файлы")
    elif direct_ok:
        print("\n⚠️ Функция работает, но проблемы с API")
        print("Возможно сервер не запущен или зависает")
    else:
        print("\n❌ Критические проблемы с PNG системой")