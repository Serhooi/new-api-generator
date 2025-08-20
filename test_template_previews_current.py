#!/usr/bin/env python3
"""
Тестируем превью шаблонов в системе
"""
import requests
import json

BASE_URL = "https://new-api-generator.onrender.com"

def test_template_previews():
    """Тестируем превью шаблонов"""
    
    print("🖼️ Тестируем превью шаблонов")
    print("=" * 50)
    
    # 1. Получаем список шаблонов
    print("\n1️⃣ Получаем список шаблонов")
    try:
        response = requests.get(f"{BASE_URL}/api/templates", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Найдено шаблонов: {len(templates)}")
            
            # Анализируем первые несколько шаблонов
            for i, template in enumerate(templates[:3]):
                print(f"\n📋 Шаблон {i+1}:")
                print(f"   ID: {template.get('id', 'НЕТ ID')}")
                print(f"   Name: {template.get('name', 'НЕТ ИМЕНИ')}")
                print(f"   Role: {template.get('role', 'НЕТ РОЛИ')}")
                
                # Проверяем наличие превью
                if 'preview_url' in template:
                    print(f"   ✅ Preview URL: {template['preview_url']}")
                    
                    # Проверяем доступность превью
                    try:
                        preview_response = requests.head(template['preview_url'], timeout=10)
                        print(f"   📄 Preview доступен: {preview_response.status_code}")
                        print(f"   📄 Content-Type: {preview_response.headers.get('content-type', 'НЕ УКАЗАН')}")
                    except Exception as e:
                        print(f"   ❌ Preview недоступен: {e}")
                        
                else:
                    print(f"   ❌ Preview URL отсутствует")
                
                # Проверяем другие поля превью
                preview_fields = ['preview_path', 'preview_filename', 'has_preview']
                for field in preview_fields:
                    if field in template:
                        print(f"   {field}: {template[field]}")
        else:
            print(f"❌ Ошибка получения шаблонов: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return
    
    # 2. Тестируем генерацию превью для конкретного шаблона
    print(f"\n2️⃣ Тестируем генерацию превью")
    
    # Берем первый шаблон для теста
    if templates:
        test_template = templates[0]
        template_id = test_template.get('id')
        
        print(f"🎯 Тестируем превью для шаблона: {template_id}")
        
        # Проверяем endpoint для генерации превью
        preview_endpoints = [
            f"/api/templates/{template_id}/preview",
            f"/api/preview/{template_id}",
            f"/preview/{template_id}"
        ]
        
        for endpoint in preview_endpoints:
            try:
                print(f"\n   🔍 Проверяю endpoint: {endpoint}")
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    print(f"   ✅ Превью доступно!")
                    print(f"   📄 Content-Type: {content_type}")
                    
                    if 'image' in content_type:
                        print(f"   🖼️ Это изображение!")
                    elif 'svg' in content_type:
                        print(f"   🎨 Это SVG!")
                    else:
                        print(f"   📄 Неизвестный тип контента")
                        
                elif response.status_code == 404:
                    print(f"   ❌ Endpoint не найден")
                else:
                    print(f"   ⚠️ Статус: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")

def test_preview_generation_api():
    """Тестируем API для генерации превью"""
    
    print(f"\n3️⃣ Тестируем API генерации превью")
    
    # Возможные endpoints для генерации превью
    endpoints_to_test = [
        "/api/generate/preview",
        "/api/templates/generate-preview", 
        "/api/preview/generate"
    ]
    
    test_data = {
        "template_id": "propertyimage2",
        "width": 400,
        "height": 600
    }
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n   🔍 Тестирую: {endpoint}")
            response = requests.post(f"{BASE_URL}{endpoint}", json=test_data, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   ✅ Превью сгенерировано!")
                    print(f"   📄 Ответ: {json.dumps(result, indent=2)[:200]}...")
                except:
                    print(f"   ✅ Превью сгенерировано (не JSON)")
                    
            elif response.status_code == 404:
                print(f"   ❌ Endpoint не найден")
            else:
                print(f"   ⚠️ Статус: {response.status_code}")
                print(f"   📄 Ответ: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_template_previews()
    test_preview_generation_api()
    
    print(f"\n" + "=" * 50)
    print("✅ Тест превью шаблонов завершен!")