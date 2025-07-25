#!/usr/bin/env python3
"""
Тест генерации превью из SVG
"""

import sys
import os
sys.path.append('.')

from app import generate_svg_preview, create_preview_svg

def test_preview_generation():
    """Тестируем генерацию превью"""
    print("🧪 ТЕСТ ГЕНЕРАЦИИ ПРЕВЬЮ")
    print("=" * 50)
    
    # Тестовый SVG с dyno полями
    test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#f8f9fa"/>
  
  <text x="400" y="100" text-anchor="middle" fill="#2c3e50" font-family="Inter" font-size="24">
    <tspan x="400" y="100">dyno.agentName</tspan>
  </text>
  
  <text x="400" y="200" text-anchor="middle" fill="#e74c3c" font-family="Inter" font-size="32">
    <tspan x="400" y="200">dyno.price</tspan>
  </text>
  
  <text x="400" y="300" text-anchor="middle" fill="#7f8c8d" font-family="Inter" font-size="16">
    <tspan x="400" y="300">dyno.propertyAddress</tspan>
  </text>
  
  <text x="400" y="400" text-anchor="middle" fill="#27ae60" font-family="Inter" font-size="18">
    <tspan x="400" y="400">dyno.bedrooms beds, dyno.bathrooms baths</tspan>
  </text>
</svg>'''
    
    print("📝 Тестовый SVG создан")
    
    # Тестируем создание превью SVG
    print("\n🎨 Тестирую создание превью SVG...")
    preview_svg = create_preview_svg(test_svg)
    
    print("✅ Превью SVG создан")
    print("🔍 Проверяю замены:")
    
    # Проверяем что dyno поля заменились
    if 'John Smith' in preview_svg:
        print("   ✅ dyno.agentName заменен на John Smith")
    else:
        print("   ❌ dyno.agentName НЕ заменен")
    
    if '$450,000' in preview_svg:
        print("   ✅ dyno.price заменен на $450,000")
    else:
        print("   ❌ dyno.price НЕ заменен")
    
    # Тестируем генерацию PNG
    print("\n🖼️ Тестирую генерацию PNG превью...")
    template_id = "test-template-123"
    
    try:
        result = generate_svg_preview(preview_svg, template_id)
        
        if result['success']:
            print(f"✅ PNG превью создан: {result['filename']}")
            print(f"📁 Путь: {result['path']}")
            print(f"🌐 URL: {result['url']}")
            
            # Проверяем что файл существует
            if os.path.exists(result['path']):
                file_size = os.path.getsize(result['path'])
                print(f"📊 Размер файла: {file_size} байт")
            else:
                print("❌ Файл не найден!")
        else:
            print(f"❌ Ошибка генерации PNG: {result['error']}")
    
    except Exception as e:
        print(f"❌ Исключение при генерации: {e}")
    
    print("\n🎉 ТЕСТ ЗАВЕРШЕН")

if __name__ == "__main__":
    test_preview_generation()