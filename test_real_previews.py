#!/usr/bin/env python3
"""
Тестируем исправленную систему превью - должны показываться реальные шаблоны
"""

import sys
sys.path.append('.')

from app import generate_svg_preview, create_preview_svg, convert_svg_to_png_improved
import os

def test_preview_generation():
    """Тестируем генерацию превью из реального SVG"""
    
    print("🧪 ТЕСТ РЕАЛЬНЫХ ПРЕВЬЮ")
    print("=" * 40)
    
    # Тестовый SVG шаблон (упрощенный)
    test_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
        <rect width="1080" height="1350" fill="#ffffff"/>
        
        <!-- Заголовок -->
        <rect x="40" y="40" width="1000" height="200" fill="#1976d2"/>
        <text x="540" y="140" text-anchor="middle" font-size="48" fill="white" font-weight="bold">{{dyno.agentName}}</text>
        
        <!-- Адрес -->
        <text x="540" y="300" text-anchor="middle" font-size="32" fill="#333">{{dyno.propertyAddress}}</text>
        
        <!-- Цена -->
        <rect x="200" y="350" width="680" height="100" fill="#4caf50"/>
        <text x="540" y="410" text-anchor="middle" font-size="42" fill="white" font-weight="bold">{{dyno.price}}</text>
        
        <!-- Детали -->
        <text x="270" y="500" text-anchor="middle" font-size="24" fill="#666">{{dyno.bedrooms}} bed</text>
        <text x="540" y="500" text-anchor="middle" font-size="24" fill="#666">{{dyno.bathrooms}} bath</text>
        <text x="810" y="500" text-anchor="middle" font-size="24" fill="#666">{{dyno.sqft}} sq ft</text>
        
        <!-- Изображение недвижимости -->
        <rect x="100" y="600" width="880" height="500" fill="#e0e0e0" stroke="#999" stroke-width="2"/>
        <text x="540" y="860" text-anchor="middle" font-size="20" fill="#666">Property Image</text>
        
        <!-- Контакты -->
        <text x="540" y="1200" text-anchor="middle" font-size="20" fill="#333">{{dyno.agentPhone}}</text>
        <text x="540" y="1250" text-anchor="middle" font-size="18" fill="#666">{{dyno.agentEmail}}</text>
    </svg>'''
    
    print("1️⃣ Тестирую create_preview_svg...")
    preview_svg = create_preview_svg(test_svg)
    
    # Проверяем что dyno поля заменились
    if '{{dyno.' in preview_svg:
        print("❌ Dyno поля не заменились")
        return False
    else:
        print("✅ Dyno поля заменены на примеры")
    
    print("\n2️⃣ Тестирую generate_svg_preview...")
    result = generate_svg_preview(test_svg, "test_template", 400, 600)
    
    if result['success']:
        print("✅ generate_svg_preview работает")
        
        # Проверяем файл
        preview_file = f"output/previews/test_template_preview.png"
        if os.path.exists(preview_file):
            size = os.path.getsize(preview_file)
            print(f"📊 Размер превью: {size} bytes")
            
            if size > 5000:  # Больше 5KB
                print("✅ Превью содержит реальные данные!")
                
                # Удаляем тестовый файл
                try:
                    os.remove(preview_file)
                    print("🗑️ Тестовый файл удален")
                except:
                    pass
                
                return True
            else:
                print("❌ Превью слишком маленькое")
        else:
            print("❌ Файл превью не создан")
    else:
        print("❌ generate_svg_preview не работает")
    
    return False

def test_direct_conversion():
    """Тестируем прямую конвертацию с dyno полями"""
    
    print("\n3️⃣ ТЕСТ ПРЯМОЙ КОНВЕРТАЦИИ")
    print("=" * 30)
    
    # SVG с dyno полями
    svg_with_dyno = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#f0f8ff"/>
        <rect x="20" y="20" width="360" height="260" fill="white" stroke="#1976d2" stroke-width="2"/>
        <text x="200" y="80" text-anchor="middle" font-size="24" fill="#1976d2">{{dyno.agentName}}</text>
        <text x="200" y="120" text-anchor="middle" font-size="16" fill="#666">{{dyno.propertyAddress}}</text>
        <text x="200" y="180" text-anchor="middle" font-size="32" fill="#4caf50">{{dyno.price}}</text>
        <text x="200" y="220" text-anchor="middle" font-size="14" fill="#999">{{dyno.bedrooms}} bed • {{dyno.bathrooms}} bath</text>
    </svg>'''
    
    # Заменяем dyno поля
    preview_svg = create_preview_svg(svg_with_dyno)
    
    # Конвертируем в PNG
    success = convert_svg_to_png_improved(preview_svg, 'test_direct_preview.png', 400, 300)
    
    if success:
        if os.path.exists('test_direct_preview.png'):
            size = os.path.getsize('test_direct_preview.png')
            print(f"✅ Прямая конвертация работает: {size} bytes")
            os.remove('test_direct_preview.png')
            return True
    
    print("❌ Прямая конвертация не работает")
    return False

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ РЕАЛЬНЫХ ПРЕВЬЮ")
    print("=" * 50)
    
    # Создаем директории
    os.makedirs('output/previews', exist_ok=True)
    
    # Тестируем
    preview_ok = test_preview_generation()
    direct_ok = test_direct_conversion()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"🖼️ Система превью: {'✅ Работает' if preview_ok else '❌ Не работает'}")
    print(f"🔄 Прямая конвертация: {'✅ Работает' if direct_ok else '❌ Не работает'}")
    
    if preview_ok and direct_ok:
        print("\n🎉 ВСЕ ИСПРАВЛЕНО!")
        print("✅ Теперь превью показывают реальные шаблоны")
        print("✅ Dyno поля заменяются на примеры данных")
        print("✅ PNG создаются с качественным содержимым")
        print("\n📋 Что изменилось:")
        print("• generate_svg_preview использует convert_svg_to_png_improved")
        print("• Убраны заглушки 'Template Preview'")
        print("• Превью создаются из реального SVG контента")
    else:
        print("\n⚠️ Есть проблемы с системой превью")