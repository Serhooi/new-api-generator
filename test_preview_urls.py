#!/usr/bin/env python3
"""
Тестируем доступность превью по URL
"""
import requests

BASE_URL = "https://new-api-generator.onrender.com"

def test_preview_urls():
    """Тестируем доступность превью по URL"""
    
    print("🔗 Тестируем доступность превью по URL")
    print("=" * 50)
    
    # Получаем шаблоны
    try:
        response = requests.get(f"{BASE_URL}/api/templates/all-previews", timeout=30)
        if response.status_code != 200:
            print("❌ Не удалось получить шаблоны")
            return
            
        data = response.json()
        templates = data.get('templates', [])
        
        print(f"✅ Найдено {len(templates)} шаблонов")
        
        # Тестируем первые 5 превью
        for i, template in enumerate(templates[:5]):
            template_id = template.get('id', 'НЕТ ID')
            preview_url = template.get('preview_url', '')
            
            print(f"\n📋 Шаблон {i+1}: {template_id}")
            print(f"   Относительный URL: {preview_url}")
            
            if preview_url:
                # Тестируем полный URL
                full_url = f"{BASE_URL}{preview_url}"
                print(f"   Полный URL: {full_url}")
                
                try:
                    preview_response = requests.head(full_url, timeout=10)
                    print(f"   Status: {preview_response.status_code}")
                    
                    if preview_response.status_code == 200:
                        content_type = preview_response.headers.get('content-type', 'НЕ УКАЗАН')
                        content_length = preview_response.headers.get('content-length', 'НЕ УКАЗАН')
                        print(f"   ✅ Превью доступно!")
                        print(f"   📄 Content-Type: {content_type}")
                        print(f"   📏 Размер: {content_length} байт")
                        
                        # Проверяем, что это действительно изображение
                        if 'image' in content_type:
                            print(f"   🖼️ Это изображение!")
                        else:
                            print(f"   ⚠️ Не изображение: {content_type}")
                            
                    elif preview_response.status_code == 404:
                        print(f"   ❌ Превью не найдено (404)")
                    else:
                        print(f"   ⚠️ Неожиданный статус: {preview_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка запроса: {e}")
            else:
                print(f"   ❌ Preview URL отсутствует")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_direct_preview_access():
    """Тестируем прямой доступ к превью"""
    
    print(f"\n🎯 Тестируем прямой доступ к превью")
    
    # Известные превью URL
    preview_urls = [
        "/output/previews/propertyimage2_preview.png",
        "/api/templates/propertyimage2/preview"
    ]
    
    for preview_url in preview_urls:
        print(f"\n🔗 Тестируем: {preview_url}")
        full_url = f"{BASE_URL}{preview_url}"
        
        try:
            response = requests.head(full_url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'НЕ УКАЗАН')
                print(f"   ✅ Доступно!")
                print(f"   📄 Content-Type: {content_type}")
            else:
                print(f"   ❌ Недоступно: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_preview_urls()
    test_direct_preview_access()
    
    print(f"\n" + "=" * 50)
    print("✅ Тест превью URL завершен!")