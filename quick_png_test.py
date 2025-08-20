#!/usr/bin/env python3
"""
Быстрый тест PNG без сервера - напрямую тестируем функцию
"""

import os
import sys

# Добавляем путь к app.py
sys.path.append('.')

def test_png_function_directly():
    """Тестируем PNG функцию напрямую без сервера"""
    
    print("🧪 ПРЯМОЙ ТЕСТ PNG ФУНКЦИИ")
    print("=" * 40)
    
    # Импортируем функцию из app.py
    try:
        from app import convert_svg_to_png_improved
        print("✅ Функция импортирована")
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # Тестовый SVG с реальным содержимым
    test_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
        <rect width="1080" height="1350" fill="#f0f8ff"/>
        <rect x="40" y="40" width="1000" height="1270" fill="white" stroke="#1976d2" stroke-width="4"/>
        <text x="540" y="150" text-anchor="middle" font-size="48" fill="#1976d2" font-weight="bold">Real Estate</text>
        <text x="540" y="220" text-anchor="middle" font-size="32" fill="#666">Premium Property</text>
        <rect x="100" y="300" width="880" height="500" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
        <text x="540" y="580" text-anchor="middle" font-size="24" fill="#333">Beautiful Home</text>
        <text x="540" y="620" text-anchor="middle" font-size="20" fill="#666">3 bed • 2 bath • 2,500 sq ft</text>
        <text x="540" y="900" text-anchor="middle" font-size="36" fill="#1976d2" font-weight="bold">$750,000</text>
        <text x="540" y="1000" text-anchor="middle" font-size="18" fill="#666">Contact us today!</text>
    </svg>'''
    
    # Тестируем конвертацию
    output_file = 'test_direct_png.png'
    
    print("🖼️ Тестирую конвертацию...")
    success = convert_svg_to_png_improved(test_svg, output_file)
    
    if success:
        print("✅ Функция вернула True")
        
        # Проверяем файл
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"📊 Размер файла: {size} bytes")
            
            if size > 1000:
                print("✅ PNG файл создан и содержит данные!")
                print(f"📁 Файл: {os.path.abspath(output_file)}")
                
                # Удаляем тестовый файл
                try:
                    os.remove(output_file)
                    print("🗑️ Тестовый файл удален")
                except:
                    pass
                
                return True
            else:
                print("❌ PNG файл слишком маленький")
        else:
            print("❌ PNG файл не создан")
    else:
        print("❌ Функция вернула False")
    
    return False

def test_playwright_availability():
    """Проверяем доступность Playwright"""
    
    print("\n🎭 ПРОВЕРКА PLAYWRIGHT")
    print("=" * 25)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright импортирован")
        
        # Пробуем запустить браузер
        with sync_playwright() as p:
            browser = p.chromium.launch()
            print("✅ Chromium запущен")
            browser.close()
            print("✅ Chromium закрыт")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Playwright: {e}")
        return False

def test_pil_fallback():
    """Тестируем PIL fallback отдельно"""
    
    print("\n🎨 ТЕСТ PIL FALLBACK")
    print("=" * 20)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ PIL импортирован")
        
        # Создаем тестовое изображение
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Рисуем что-то
        draw.rectangle([20, 20, 380, 280], outline='navy', width=3)
        draw.text((200, 150), "PIL Test", fill='navy', anchor='mm')
        
        # Сохраняем
        test_file = 'test_pil.png'
        img.save(test_file, 'PNG')
        
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            print(f"✅ PIL создал PNG: {size} bytes")
            os.remove(test_file)
            return True
        
    except Exception as e:
        print(f"❌ Ошибка PIL: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 БЫСТРОЕ ТЕСТИРОВАНИЕ PNG СИСТЕМЫ")
    print("=" * 50)
    
    # Тестируем компоненты
    playwright_ok = test_playwright_availability()
    pil_ok = test_pil_fallback()
    png_ok = test_png_function_directly()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"🎭 Playwright: {'✅ Работает' if playwright_ok else '❌ Не работает'}")
    print(f"🎨 PIL: {'✅ Работает' if pil_ok else '❌ Не работает'}")
    print(f"🖼️ PNG функция: {'✅ Работает' if png_ok else '❌ Не работает'}")
    
    if png_ok:
        print("\n🎉 PNG СИСТЕМА РАБОТАЕТ!")
        print("Теперь можно тестировать через API")
    elif playwright_ok or pil_ok:
        print("\n⚠️ Есть проблемы с PNG функцией, но компоненты работают")
    else:
        print("\n❌ Критические проблемы с PNG системой")