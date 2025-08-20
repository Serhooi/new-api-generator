#!/usr/bin/env python3
"""
Отладка ответа API шаблонов
"""
import requests
import json

BASE_URL = "https://new-api-generator.onrender.com"

def debug_templates_api():
    """Отладка API шаблонов"""
    
    print("🔍 Отладка API шаблонов")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/templates/all-previews", timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"\n📄 Сырой ответ:")
            raw_text = response.text
            print(f"Тип: {type(raw_text)}")
            print(f"Длина: {len(raw_text)}")
            print(f"Первые 500 символов:")
            print(raw_text[:500])
            
            print(f"\n📄 Попытка парсинга JSON:")
            try:
                data = response.json()
                print(f"Тип данных: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"Словарь с ключами: {list(data.keys())}")
                    print(f"Полный словарь:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                elif isinstance(data, list):
                    print(f"Список из {len(data)} элементов")
                    if data:
                        print(f"Первый элемент:")
                        print(json.dumps(data[0], indent=2, ensure_ascii=False))
                else:
                    print(f"Неожиданный тип: {type(data)}")
                    print(f"Данные: {data}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                
        else:
            print(f"❌ Ошибка HTTP: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_specific_template_preview():
    """Тестируем превью конкретного шаблона"""
    
    print(f"\n🎯 Тестируем превью конкретного шаблона")
    
    template_ids = ["propertyimage2", "test_template", "main_template"]
    
    for template_id in template_ids:
        print(f"\n📋 Тестируем: {template_id}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/templates/{template_id}/preview", timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"   ✅ Превью получено!")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📏 Размер: {len(response.content)} байт")
                
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"   📄 JSON данные:")
                        print(f"   {json.dumps(data, indent=4, ensure_ascii=False)}")
                    except:
                        print(f"   ❌ Не удалось распарсить JSON")
                        
            elif response.status_code == 404:
                print(f"   ❌ Шаблон не найден")
            else:
                print(f"   ⚠️ Статус: {response.status_code}")
                print(f"   📄 Ответ: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    debug_templates_api()
    test_specific_template_preview()
    
    print(f"\n" + "=" * 50)
    print("✅ Отладка завершена!")