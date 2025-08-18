#!/usr/bin/env python3
"""
Тест всех исправлений: photo слайд, превью, PNG конвертация
"""

import requests
import json
import time

def test_server_health():
    """Проверяем что сервер работает"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_template_previews():
    """Тестируем превью шаблонов"""
    print("🖼️ ТЕСТ ПРЕВЬЮ ШАБЛОНОВ")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=15)
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"📋 Шаблонов: {len(templates)}")
            
            if templates:
                template = templates[0]
                preview_url = template.get('preview_url')
                print(f"🎯 Тестовый шаблон: {template.get('name')}")
                print(f"🔗 Preview URL: {preview_url}")
                
                # Проверяем доступность превью
                if preview_url:
                    preview_response = requests.get(f"http://localhost:5000{preview_url}", timeout=10)
                    print(f"📊 Preview статус: {preview_response.status_code}")
                    
                    if preview_response.status_code == 200:
                        print("✅ Превью доступно")
                        return True
                    else:
                        print("❌ Превью недоступно")
                        return False
            else:
                print("ℹ️ Шаблонов не найдено")
                return False
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_carousel_generation():
    """Тестируем генерацию карусели с отладкой photo слайда"""
    print("\n🎠 ТЕСТ ГЕНЕРАЦИИ КАРУСЕЛИ")
    print("=" * 40)
    
    # Получаем шаблоны
    try:
        templates_response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
        if templates_response.status_code != 200:
            print("❌ Не удалось получить шаблоны")
            return False, None
        
        templates = templates_response.json().get('templates', [])
        main_template = None
        photo_template = None
        
        for template in templates:
            if template.get('template_role') == 'main':
                main_template = template
            elif template.get('template_role') == 'photo':
                photo_template = template
        
        if not main_template or not photo_template:
            print("❌ Не найдены main или photo шаблоны")
            return False, None
        
        print(f"✅ Main: {main_template['name']}")
        print(f"✅ Photo: {photo_template['name']}")
        
        # Тестовые данные
        test_data = {
            "main_template_id": main_template['id'],
            "photo_template_id": photo_template['id'],
            "data": {
                "dyno.propertyaddress": "123 Test Street",
                "dyno.price": "$500,000",
                "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
                "dyno.propertyimage2": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300",
                "dyno.name": "John Smith",
                "dyno.phone": "(555) 123-4567"
            }
        }
        
        print("🔄 Генерирую карусель...")
        response = requests.post(
            "http://localhost:5000/api/generate/carousel",
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация успешна!")
            
            images = result.get('images', [])
            print(f"🖼️ Изображений: {len(images)}")
            
            if len(images) >= 2:
                main_url = images[0]
                photo_url = images[1]
                
                print(f"🎯 Main URL: {main_url}")
                print(f"📸 Photo URL: {photo_url}")
                
                # Проверяем доступность
                main_check = requests.head(main_url, timeout=10)
                photo_check = requests.head(photo_url, timeout=10)
                
                print(f"📊 Main доступность: {main_check.status_code}")
                print(f"📊 Photo доступность: {photo_check.status_code}")
                
                if main_check.status_code == 200 and photo_check.status_code == 200:
                    print("✅ Оба изображения доступны")
                    return True, images[0]  # Возвращаем первый URL для PNG теста
                else:
                    print("❌ Некоторые изображения недоступны")
                    return False, None
            else:
                print("❌ Недостаточно изображений")
                return False, None
        else:
            print(f"❌ Ошибка генерации: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False, None

def test_png_conversion(svg_url):
    """Тестируем конвертацию SVG в PNG"""
    print("\n🖼️ ТЕСТ PNG КОНВЕРТАЦИИ")
    print("=" * 40)
    
    if not svg_url:
        print("❌ Нет SVG URL для конвертации")
        return False
    
    try:
        conversion_data = {"svg_url": svg_url}
        
        print(f"🔄 Конвертирую: {svg_url}")
        response = requests.post(
            "http://localhost:5000/api/convert-to-png",
            json=conversion_data,
            timeout=60
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                png_url = result.get('png_url')
                filename = result.get('filename')
                
                print(f"✅ PNG создан: {filename}")
                print(f"🔗 PNG URL: {png_url}")
                
                # Проверяем доступность PNG
                png_check = requests.head(png_url, timeout=10)
                print(f"📊 PNG доступность: {png_check.status_code}")
                
                if png_check.status_code == 200:
                    print("✅ PNG доступен")
                    return True
                else:
                    print("❌ PNG недоступен")
                    return False
            else:
                print("❌ Конвертация не удалась")
                return False
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 ПОЛНЫЙ ТЕСТ ВСЕХ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    # Проверяем сервер
    if not test_server_health():
        print("❌ Сервер не работает")
        return
    
    print("✅ Сервер работает")
    
    # Тест 1: Превью шаблонов
    previews_ok = test_template_previews()
    
    # Тест 2: Генерация карусели (включая photo слайд)
    carousel_ok, svg_url = test_carousel_generation()
    
    # Тест 3: PNG конвертация
    png_ok = test_png_conversion(svg_url) if svg_url else False
    
    # Итоги
    print("\n📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    print(f"🖼️ Превью шаблонов: {'✅' if previews_ok else '❌'}")
    print(f"🎠 Генерация карусели: {'✅' if carousel_ok else '❌'}")
    print(f"🖼️ PNG конвертация: {'✅' if png_ok else '❌'}")
    
    if previews_ok and carousel_ok and png_ok:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Превью шаблонов работают")
        print("✅ Photo слайд обновляется")
        print("✅ PNG конвертация работает")
    else:
        print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ:")
        if not previews_ok:
            print("❌ Превью шаблонов не работают")
        if not carousel_ok:
            print("❌ Проблемы с генерацией карусели")
        if not png_ok:
            print("❌ PNG конвертация не работает")

if __name__ == "__main__":
    main()