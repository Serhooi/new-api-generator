#!/usr/bin/env python3
"""
Тестируем правильные endpoints для превью шаблонов
"""
import requests
import json

BASE_URL = "https://new-api-generator.onrender.com"

def test_template_previews_correct():
    """Тестируем правильные endpoints для превью"""
    
    print("🖼️ Тестируем превью шаблонов (правильные endpoints)")
    print("=" * 50)
    
    # 1. Получаем все шаблоны с превью
    print("\n1️⃣ Получаем все шаблоны с превью")
    try:
        response = requests.get(f"{BASE_URL}/api/templates/all-previews", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Найдено шаблонов: {len(templates)}")
            
            # Анализируем шаблоны
            templates_list = templates if isinstance(templates, list) else [templates]
            for i, template in enumerate(templates_list[:5]):  # Первые 5 шаблонов
                print(f"\n📋 Шаблон {i+1}:")
                print(f"   ID: {template.get('id', 'НЕТ ID')}")
                print(f"   Name: {template.get('name', 'НЕТ ИМЕНИ')}")
                print(f"   Role: {template.get('role', 'НЕТ РОЛИ')}")
                
                # Проверяем превью поля
                preview_fields = ['preview_url', 'preview_path', 'preview_filename', 'has_preview']
                for field in preview_fields:
                    if field in template:
                        value = template[field]
                        print(f"   {field}: {value}")
                        
                        # Если это URL превью, проверяем доступность
                        if field == 'preview_url' and value:
                            try:
                                preview_response = requests.head(value, timeout=10)
                                print(f"   📄 Preview доступен: {preview_response.status_code}")
                                content_type = preview_response.headers.get('content-type', 'НЕ УКАЗАН')
                                print(f"   📄 Content-Type: {content_type}")
                                
                                if '.png' in value:
                                    print(f"   🖼️ PNG превью")
                                elif '.svg' in value:
                                    print(f"   🎨 SVG превью")
                                    
                            except Exception as e:
                                print(f"   ❌ Preview недоступен: {e}")
                
                print(f"   " + "-" * 40)
                
        else:
            print(f"❌ Ошибка получения шаблонов: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None
    
    return templates

def test_individual_template_preview(templates):
    """Тестируем превью отдельных шаблонов"""
    
    if not templates:
        print("\n❌ Нет шаблонов для тестирования")
        return
    
    print(f"\n2️⃣ Тестируем превью отдельных шаблонов")
    
    # Берем первые 3 шаблона
    templates_list = templates if isinstance(templates, list) else [templates]
    for template in templates_list[:3]:
        template_id = template.get('id')
        if not template_id:
            continue
            
        print(f"\n🎯 Тестируем превью для: {template_id}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/templates/{template_id}/preview", timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"   ✅ Превью получено!")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📏 Размер: {len(response.content)} байт")
                
                if 'image' in content_type:
                    print(f"   🖼️ Это изображение!")
                elif 'svg' in content_type:
                    print(f"   🎨 Это SVG!")
                elif 'json' in content_type:
                    try:
                        result = response.json()
                        print(f"   📄 JSON ответ: {json.dumps(result, indent=2)[:200]}...")
                    except:
                        print(f"   📄 JSON ответ (не удалось распарсить)")
                        
            elif response.status_code == 404:
                print(f"   ❌ Превью не найдено")
            else:
                print(f"   ⚠️ Статус: {response.status_code}")
                print(f"   📄 Ответ: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def test_preview_generation():
    """Тестируем генерацию превью"""
    
    print(f"\n3️⃣ Тестируем генерацию превью")
    
    # Проверяем endpoint для генерации превью
    test_template_id = "propertyimage2"
    
    print(f"🎯 Генерируем превью для: {test_template_id}")
    
    try:
        # Пробуем получить превью
        response = requests.get(f"{BASE_URL}/api/templates/{test_template_id}/preview", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"✅ Превью сгенерировано!")
            print(f"📄 Content-Type: {content_type}")
            print(f"📏 Размер: {len(response.content)} байт")
            
            # Сохраняем превью для проверки
            if 'image' in content_type:
                extension = 'png' if 'png' in content_type else 'jpg'
                filename = f"preview_{test_template_id}.{extension}"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 Превью сохранено: {filename}")
                
        else:
            print(f"❌ Ошибка генерации: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    templates = test_template_previews_correct()
    test_individual_template_preview(templates)
    test_preview_generation()
    
    print(f"\n" + "=" * 50)
    print("✅ Тест превью шаблонов завершен!")