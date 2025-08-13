#!/usr/bin/env python3
"""
Тест API генерации карусели
"""

import requests
import json

def test_carousel_generation():
    """Тестируем генерацию карусели через API"""
    
    print("🧪 ТЕСТ ГЕНЕРАЦИИ КАРУСЕЛИ")
    print("=" * 50)
    
    # Проверяем что сервер запущен
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"🏥 Сервер статус: {health_response.status_code}")
        
        if health_response.status_code != 200:
            print("❌ Сервер не запущен")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Сервер недоступен: {e}")
        return
    
    # Получаем список шаблонов
    try:
        templates_response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
        print(f"📋 Шаблоны статус: {templates_response.status_code}")
        
        if templates_response.status_code == 200:
            templates_data = templates_response.json()
            templates = templates_data.get('templates', [])
            print(f"📊 Найдено шаблонов: {len(templates)}")
            
            # Ищем main и photo шаблоны
            main_template = None
            photo_template = None
            
            for template in templates:
                if template.get('template_role') == 'main':
                    main_template = template
                elif template.get('template_role') == 'photo':
                    photo_template = template
            
            if not main_template or not photo_template:
                print("❌ Не найдены main или photo шаблоны")
                return
                
            print(f"✅ Main шаблон: {main_template['name']} (ID: {main_template['id']})")
            print(f"✅ Photo шаблон: {photo_template['name']} (ID: {photo_template['id']})")
            
        else:
            print(f"❌ Ошибка получения шаблонов: {templates_response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса шаблонов: {e}")
        return
    
    # Тестовые данные для генерации
    test_data = {
        "main_template_id": main_template['id'],
        "photo_template_id": photo_template['id'],
        "data": {
            "dyno.propertyaddress": "123 Test Street, Test City",
            "dyno.price": "$500,000",
            "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300",
            "dyno.propertyimage2": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300",
            "dyno.agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200",
            "dyno.name": "John Smith",
            "dyno.phone": "(555) 123-4567",
            "dyno.email": "john@example.com",
            "dyno.date": "MAY 20 2025",
            "dyno.time": "2:00 PM - 4:00 PM",
            "dyno.bedrooms": "4",
            "dyno.bathrooms": "3",
            "dyno.logo": "REALTY CO"
        }
    }
    
    print("\\n🔄 Отправляю запрос на генерацию...")
    print(f"📋 Данные: {json.dumps(test_data, indent=2)}")
    
    try:
        # Отправляем запрос на генерацию
        generation_response = requests.post(
            "http://localhost:5000/api/generate/carousel",
            json=test_data,
            timeout=60  # Увеличиваем таймаут для обработки изображений
        )
        
        print(f"📊 Генерация статус: {generation_response.status_code}")
        
        if generation_response.status_code == 200:
            result = generation_response.json()
            print("✅ Генерация успешна!")
            
            # Анализируем ответ
            print("\\n📋 АНАЛИЗ ОТВЕТА:")
            print(f"🆔 Carousel ID: {result.get('carousel_id')}")
            print(f"✅ Success: {result.get('success')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"🔢 Slides count: {result.get('slides_count')}")
            
            # Проверяем URL
            if 'images' in result:
                print(f"\\n🖼️ ИЗОБРАЖЕНИЯ ({len(result['images'])}):")
                for i, url in enumerate(result['images']):
                    print(f"  {i+1}. {url}")
                    
                    # Проверяем доступность каждого URL
                    try:
                        url_response = requests.head(url, timeout=10)
                        print(f"     📊 Статус: {url_response.status_code}")
                        
                        if url_response.status_code == 200:
                            content_type = url_response.headers.get('content-type', 'unknown')
                            print(f"     📄 Content-Type: {content_type}")
                        else:
                            print(f"     ❌ URL недоступен!")
                            
                    except requests.exceptions.RequestException as e:
                        print(f"     ❌ Ошибка проверки URL: {e}")
            
            # Проверяем другие поля
            if 'slides' in result:
                print(f"\\n🎠 SLIDES: {result['slides']}")
            
            if 'main_url' in result:
                print(f"\\n🎯 Main URL: {result['main_url']}")
            
            if 'photo_url' in result:
                print(f"📸 Photo URL: {result['photo_url']}")
            
            # Показываем весь ответ для отладки
            print(f"\\n🔍 ПОЛНЫЙ ОТВЕТ:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Ошибка генерации: {generation_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса генерации: {e}")

if __name__ == "__main__":
    test_carousel_generation()