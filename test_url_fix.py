#!/usr/bin/env python3
"""
Тест исправления URL с лишним знаком вопроса
"""

import requests
import json

def test_carousel_generation():
    """Тестируем генерацию карусели и проверяем URL"""
    
    print("🧪 ТЕСТ ИСПРАВЛЕНИЯ URL")
    print("=" * 50)
    
    # Проверяем что сервер работает
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Сервер не работает")
            return
    except:
        print("❌ Сервер недоступен")
        return
    
    print("✅ Сервер работает")
    
    # Тестовые данные для генерации
    test_data = {
        "main_template_id": "09cd9071-8c36-4ea6-9922-ce367c78980f",
        "photo_template_id": "69ef8dc1-a58c-41e0-97cc-88f8e5ddba45", 
        "data": {
            "dyno.propertyaddress": "123 Test Street",
            "dyno.price": "$500,000",
            "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300"
        }
    }
    
    print("🔄 Отправляю запрос на генерацию...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/generate/carousel",
            json=test_data,
            timeout=60
        )
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Генерация успешна!")
            
            # Проверяем URL в ответе
            images = result.get('images', [])
            print(f"\n🖼️ Получено изображений: {len(images)}")
            
            for i, url in enumerate(images, 1):
                print(f"\n🔍 Изображение {i}:")
                print(f"URL: {url}")
                
                # Проверяем на лишний знак вопроса
                if url.endswith('?'):
                    print("❌ URL содержит лишний знак вопроса в конце!")
                else:
                    print("✅ URL корректный")
                
                # Проверяем доступность URL
                try:
                    url_response = requests.head(url, timeout=10)
                    print(f"📊 URL статус: {url_response.status_code}")
                    
                    if url_response.status_code == 200:
                        print("✅ Изображение доступно")
                        
                        # Проверяем заголовки
                        content_type = url_response.headers.get('content-type', 'unknown')
                        print(f"📄 Content-Type: {content_type}")
                        
                        cors_origin = url_response.headers.get('access-control-allow-origin')
                        if cors_origin:
                            print(f"🌐 CORS: {cors_origin}")
                        else:
                            print("⚠️ CORS заголовки отсутствуют")
                    else:
                        print(f"❌ Изображение недоступно: {url_response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Ошибка проверки URL: {e}")
            
        else:
            print(f"❌ Ошибка генерации: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_template_preview():
    """Тестируем превью шаблонов"""
    
    print(f"\n🖼️ ТЕСТ ПРЕВЬЮ ШАБЛОНОВ")
    print("=" * 40)
    
    # Получаем список шаблонов
    try:
        templates_response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=10)
        
        if templates_response.status_code == 200:
            data = templates_response.json()
            templates = data.get('templates', [])
            print(f"📋 Найдено шаблонов: {len(templates)}")
            
            if templates:
                # Тестируем превью первого шаблона
                template = templates[0]
                template_id = template.get('id')
                template_name = template.get('name')
                
                print(f"\n🎯 Тестирую превью: {template_name} (ID: {template_id})")
                
                preview_response = requests.get(
                    f"http://localhost:5000/api/templates/{template_id}/preview",
                    timeout=10
                )
                
                print(f"📊 Превью статус: {preview_response.status_code}")
                
                if preview_response.status_code == 200:
                    content_type = preview_response.headers.get('content-type', 'unknown')
                    print(f"📄 Content-Type: {content_type}")
                    
                    if 'svg' in content_type:
                        print("✅ Превью возвращается как SVG")
                    elif 'png' in content_type:
                        print("✅ Превью возвращается как PNG")
                    else:
                        print(f"⚠️ Неожиданный тип: {content_type}")
                else:
                    print(f"❌ Ошибка превью: {preview_response.text}")
            else:
                print("ℹ️ Шаблонов не найдено")
        else:
            print(f"❌ Ошибка получения шаблонов: {templates_response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка теста превью: {e}")

if __name__ == "__main__":
    test_carousel_generation()
    test_template_preview()