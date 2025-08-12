#!/usr/bin/env python3
"""
Отладка загрузки файлов из Supabase
"""

import requests
import json

def test_supabase_url():
    """Тестируем доступность URL из Supabase"""
    
    print("🔍 ТЕСТ ЗАГРУЗКИ ФАЙЛОВ ИЗ SUPABASE")
    print("=" * 50)
    
    # URL из ошибки (обрезанный)
    test_url = "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-templates/carousel_1f1cdfc1-f788-4c5c-898d-351c20d6ae09_main.svg"
    
    print(f"🌐 Тестирую URL: {test_url}")
    
    try:
        # Делаем HEAD запрос чтобы проверить доступность
        response = requests.head(test_url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        if response.status_code == 200:
            print("✅ URL доступен!")
            
            # Проверяем Content-Type
            content_type = response.headers.get('content-type', 'unknown')
            print(f"📄 Content-Type: {content_type}")
            
            if 'svg' not in content_type.lower():
                print("⚠️ Content-Type может быть проблемой для SVG")
            
            # Проверяем CORS заголовки
            cors_origin = response.headers.get('access-control-allow-origin')
            if cors_origin:
                print(f"🌐 CORS Origin: {cors_origin}")
            else:
                print("❌ CORS заголовки отсутствуют!")
                
        else:
            print(f"❌ URL недоступен: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")

def test_local_server_files():
    """Проверяем файлы на локальном сервере"""
    
    print("\n🏠 ТЕСТ ЛОКАЛЬНЫХ ФАЙЛОВ")
    print("=" * 30)
    
    # Проверяем что сервер запущен
    try:
        response = requests.get("http://localhost:5000/api/templates", timeout=5)
        print(f"📊 Сервер статус: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"📋 Найдено шаблонов: {len(templates.get('templates', []))}")
            
            # Проверяем первый шаблон
            if templates.get('templates'):
                template = templates['templates'][0]
                print(f"🎯 Тестовый шаблон: {template.get('name')}")
                
                # Тестируем генерацию
                test_data = {
                    "template_id": template.get('id'),
                    "data": {
                        "dyno.propertyaddress": "123 Test Street",
                        "dyno.price": "$500,000",
                        "dyno.propertyimage": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300"
                    }
                }
                
                print("🔄 Тестирую генерацию...")
                gen_response = requests.post("http://localhost:5000/api/generate", 
                                           json=test_data, timeout=30)
                
                print(f"📊 Генерация статус: {gen_response.status_code}")
                
                if gen_response.status_code == 200:
                    result = gen_response.json()
                    print(f"✅ Генерация успешна!")
                    
                    if 'slides' in result:
                        for i, slide in enumerate(result['slides']):
                            slide_url = slide.get('url', '')
                            print(f"🖼️ Слайд {i+1}: {slide_url}")
                            
                            # Проверяем доступность слайда
                            if slide_url:
                                try:
                                    slide_response = requests.head(slide_url, timeout=5)
                                    print(f"  📊 Статус: {slide_response.status_code}")
                                    
                                    if slide_response.status_code != 200:
                                        print(f"  ❌ Слайд недоступен!")
                                except:
                                    print(f"  ❌ Ошибка доступа к слайду")
                else:
                    print(f"❌ Ошибка генерации: {gen_response.text}")
        else:
            print("❌ Сервер недоступен")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Сервер не запущен: {e}")

def check_output_directory():
    """Проверяем директорию output"""
    
    print("\n📁 ПРОВЕРКА ДИРЕКТОРИИ OUTPUT")
    print("=" * 35)
    
    import os
    
    output_dir = "output"
    if os.path.exists(output_dir):
        print(f"✅ Директория {output_dir} существует")
        
        # Проверяем содержимое
        files = os.listdir(output_dir)
        print(f"📋 Файлов в output: {len(files)}")
        
        # Показываем последние файлы
        svg_files = [f for f in files if f.endswith('.svg')]
        print(f"🖼️ SVG файлов: {len(svg_files)}")
        
        if svg_files:
            print("📋 Последние SVG файлы:")
            for f in sorted(svg_files)[-5:]:  # Последние 5
                file_path = os.path.join(output_dir, f)
                size = os.path.getsize(file_path)
                print(f"  {f} ({size} bytes)")
        
        # Проверяем права доступа
        import stat
        dir_stat = os.stat(output_dir)
        permissions = stat.filemode(dir_stat.st_mode)
        print(f"🔐 Права доступа: {permissions}")
        
    else:
        print(f"❌ Директория {output_dir} не существует")

if __name__ == "__main__":
    test_supabase_url()
    test_local_server_files()
    check_output_directory()