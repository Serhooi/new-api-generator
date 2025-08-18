#!/usr/bin/env python3
"""
Тест превью шаблонов
"""

import requests
import os

def test_template_previews():
    """Тестируем превью шаблонов"""
    
    print("🖼️ ТЕСТ ПРЕВЬЮ ШАБЛОНОВ")
    print("=" * 50)
    
    # Проверяем сервер
    try:
        health = requests.get("http://localhost:5000/api/health", timeout=5)
        if health.status_code != 200:
            print("❌ Сервер не работает")
            return
    except:
        print("❌ Сервер недоступен")
        return
    
    print("✅ Сервер работает")
    
    # Получаем список шаблонов
    try:
        response = requests.get("http://localhost:5000/api/templates/all-previews", timeout=15)
        print(f"📊 Статус получения шаблонов: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"📋 Найдено шаблонов: {len(templates)}")
            
            if templates:
                print("\\n🎯 ТЕСТ ПРЕВЬЮ:")
                
                for i, template in enumerate(templates[:3], 1):  # Тестируем первые 3
                    template_id = template.get('id')
                    template_name = template.get('name')
                    preview_url = template.get('preview_url')
                    
                    print(f"\\n{i}. {template_name}")
                    print(f"   ID: {template_id}")
                    print(f"   Preview URL: {preview_url}")
                    
                    # Проверяем доступность превью
                    if preview_url:
                        try:
                            preview_response = requests.get(f"http://localhost:5000{preview_url}", timeout=10)
                            print(f"   📊 Preview статус: {preview_response.status_code}")
                            
                            if preview_response.status_code == 200:
                                content_type = preview_response.headers.get('content-type', 'unknown')
                                content_length = len(preview_response.content)
                                print(f"   📄 Content-Type: {content_type}")
                                print(f"   📏 Размер: {content_length} bytes")
                                print("   ✅ Превью доступно")
                            else:
                                print("   ❌ Превью недоступно")
                                
                        except Exception as e:
                            print(f"   ❌ Ошибка превью: {e}")
                    
                    # Тестируем прямой API превью
                    try:
                        direct_preview = requests.get(f"http://localhost:5000/api/templates/{template_id}/preview", timeout=10)
                        print(f"   📊 Direct API статус: {direct_preview.status_code}")
                        
                        if direct_preview.status_code == 200:
                            content_type = direct_preview.headers.get('content-type', 'unknown')
                            print(f"   📄 Direct Content-Type: {content_type}")
                            
                            if 'svg' in content_type:
                                print("   ✅ Возвращается SVG")
                            elif 'png' in content_type:
                                print("   ✅ Возвращается PNG")
                            else:
                                print(f"   ⚠️ Неожиданный тип: {content_type}")
                        else:
                            print("   ❌ Direct API не работает")
                            
                    except Exception as e:
                        print(f"   ❌ Ошибка direct API: {e}")
            else:
                print("ℹ️ Шаблонов не найдено")
        else:
            print(f"❌ Ошибка получения шаблонов: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")

def check_preview_directory():
    """Проверяем директорию превью"""
    
    print("\\n📁 ПРОВЕРКА ДИРЕКТОРИИ ПРЕВЬЮ")
    print("=" * 40)
    
    preview_dir = "output/previews"
    
    if os.path.exists(preview_dir):
        files = os.listdir(preview_dir)
        png_files = [f for f in files if f.endswith('.png')]
        
        print(f"📊 Всего файлов: {len(files)}")
        print(f"🖼️ PNG файлов: {len(png_files)}")
        
        if png_files:
            print("\\n📋 PNG превью:")
            for f in png_files[:5]:  # Показываем первые 5
                file_path = os.path.join(preview_dir, f)
                size = os.path.getsize(file_path)
                print(f"  - {f} ({size} bytes)")
        else:
            print("ℹ️ PNG превью не найдены")
    else:
        print("❌ Директория превью не существует")

if __name__ == "__main__":
    check_preview_directory()
    test_template_previews()