#!/usr/bin/env python3
"""
Тест интеграции исправлений в app.py без запуска сервера
"""

import sys
import os
sys.path.append('.')

def test_import():
    """Тестируем что импорт работает"""
    
    print("🧪 ТЕСТ ИМПОРТА ИСПРАВЛЕНИЙ")
    print("=" * 50)
    
    try:
        # Тестируем импорт функции
        from preview_system import replace_image_in_svg
        print("✅ Импорт replace_image_in_svg успешен")
        
        # Тестируем что функция работает
        test_svg = '<image id="test" href="old.jpg"/>'
        result = replace_image_in_svg(test_svg, 'test', 'new.jpg')
        
        if 'new.jpg' in result:
            print("✅ Функция replace_image_in_svg работает")
        else:
            print("❌ Функция replace_image_in_svg не работает")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

def test_app_functions():
    """Тестируем что функции из app.py доступны"""
    
    print("\n🧪 ТЕСТ ФУНКЦИЙ APP.PY")
    print("=" * 50)
    
    try:
        # Импортируем функции из app.py
        from app import is_image_field
        
        # Тестируем определение полей изображений
        test_cases = [
            ('dyno.agentheadshot', True),
            ('dyno.propertyimage2', True),
            ('dyno.logo', True),
            ('dyno.agentName', False),
            ('dyno.price', False),
        ]
        
        for field, expected in test_cases:
            result = is_image_field(field)
            status = "✅" if result == expected else "❌"
            print(f"{status} {field}: {result} (ожидалось: {expected})")
            
    except ImportError as e:
        print(f"❌ Ошибка импорта app.py: {e}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_headshot_logic():
    """Тестируем логику headshot на реальных файлах"""
    
    print("\n🧪 ТЕСТ HEADSHOT ЛОГИКИ")
    print("=" * 50)
    
    try:
        from preview_system import replace_image_in_svg
        
        # Читаем main.svg
        with open('main.svg', 'r', encoding='utf-8') as f:
            main_svg = f.read()
        
        print(f"📄 Размер main.svg: {len(main_svg)} символов")
        
        # Проверяем текущий aspect ratio
        import re
        current_aspect = re.search(r'preserveAspectRatio="([^"]*)"', main_svg)
        if current_aspect:
            print(f"📋 Текущий aspect ratio: {current_aspect.group(1)}")
        
        # Применяем исправление
        test_image = "data:image/jpeg;base64,TEST_HEADSHOT"
        fixed_svg = replace_image_in_svg(main_svg, 'dyno.agentheadshot', test_image)
        
        if fixed_svg != main_svg:
            # Проверяем новый aspect ratio
            new_aspect = re.search(r'preserveAspectRatio="([^"]*)"', fixed_svg)
            if new_aspect:
                new_ratio = new_aspect.group(1)
                print(f"✅ Новый aspect ratio: {new_ratio}")
                
                if new_ratio == 'xMidYMid slice':
                    print("🎉 HEADSHOT ASPECT RATIO ИСПРАВЛЕН!")
                else:
                    print(f"⚠️ Aspect ratio не 'slice': {new_ratio}")
            
            if test_image in fixed_svg:
                print("✅ Изображение заменено!")
            else:
                print("❌ Изображение не заменено")
        else:
            print("❌ SVG не изменился")
            
    except FileNotFoundError:
        print("❌ main.svg не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_photo_logic():
    """Тестируем логику photo на реальных файлах"""
    
    print("\n🧪 ТЕСТ PHOTO ЛОГИКИ")
    print("=" * 50)
    
    try:
        from preview_system import replace_image_in_svg
        
        # Читаем photo.svg
        with open('photo.svg', 'r', encoding='utf-8') as f:
            photo_svg = f.read()
        
        print(f"📄 Размер photo.svg: {len(photo_svg)} символов")
        
        # Применяем исправление
        test_image = "data:image/jpeg;base64,TEST_PHOTO"
        fixed_svg = replace_image_in_svg(photo_svg, 'dyno.propertyimage2', test_image)
        
        if fixed_svg != photo_svg:
            if test_image in fixed_svg:
                print("✅ Photo изображение заменено!")
                print("🎉 PHOTO ГРУППА РАБОТАЕТ!")
            else:
                print("❌ Photo изображение не заменено")
            
            print(f"📊 Изменение размера: {len(fixed_svg) - len(photo_svg):+d} символов")
        else:
            print("❌ Photo SVG не изменился")
            
    except FileNotFoundError:
        print("❌ photo.svg не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Запускаем все тесты"""
    
    print("🚀 ТЕСТ ИНТЕГРАЦИИ ИСПРАВЛЕНИЙ В APP.PY")
    print("=" * 60)
    
    test_import()
    test_app_functions()
    test_headshot_logic()
    test_photo_logic()
    
    print("\n🎯 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("\n📋 ИТОГ:")
    print("- Если все тесты ✅ - исправления работают")
    print("- Теперь можно запускать сервер и тестировать API")

if __name__ == "__main__":
    main()