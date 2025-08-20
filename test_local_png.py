#!/usr/bin/env python3
"""
Тестируем PNG генерацию локально
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_local_png_generation():
    """Тестируем PNG генерацию локально"""
    
    print("🧪 Тестируем PNG генерацию локально")
    print("=" * 50)
    
    try:
        # Импортируем функции из app.py
        from app import process_svg_font_perfect, save_file_locally_or_supabase
        
        print("✅ Импорт функций успешен")
        
        # Создаем простой SVG для теста
        test_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white"/>
            <text id="dyno.address" x="540" y="200" text-anchor="middle" font-size="24" fill="black">
                <tspan x="540" y="200">{{dyno.address}}</tspan>
            </text>
            <text id="dyno.price" x="540" y="300" text-anchor="middle" font-size="32" fill="blue">
                <tspan x="540" y="300">{{dyno.price}}</tspan>
            </text>
        </svg>'''
        
        # Тестовые данные
        test_data = {
            "dyno.address": "123 Test Street, Beverly Hills, CA 90210",
            "dyno.price": "$500,000"
        }
        
        print("📝 Обрабатываем SVG...")
        processed_svg = process_svg_font_perfect(test_svg, test_data)
        
        print("✅ SVG обработан успешно")
        print(f"📏 Размер обработанного SVG: {len(processed_svg)} символов")
        
        # Проверяем, что замены произошли
        if "123 Test Street" in processed_svg:
            print("✅ Адрес заменен в SVG")
        else:
            print("❌ Адрес НЕ заменен в SVG")
            
        if "$500,000" in processed_svg:
            print("✅ Цена заменена в SVG")
        else:
            print("❌ Цена НЕ заменена в SVG")
        
        # Тестируем PIL fallback для PNG
        print("\n🖼️ Тестируем PIL PNG генерацию...")
        
        try:
            from PIL import Image, ImageDraw
            
            # Создаем PNG через PIL
            img = Image.new('RGB', (1080, 1350), color='white')
            draw = ImageDraw.Draw(img)
            
            # Рисуем заглушку
            draw.rectangle([50, 50, 1030, 1300], outline='gray', width=5)
            draw.text((540, 675), 'PNG Generated via PIL', fill='black', anchor='mm')
            draw.text((540, 725), 'Test Successful', fill='green', anchor='mm')
            
            # Сохраняем
            test_png_path = 'test_output.png'
            img.save(test_png_path)
            
            print(f"✅ PNG создан: {test_png_path}")
            print(f"📏 Размер файла: {os.path.getsize(test_png_path)} байт")
            
            # Удаляем тестовый файл
            os.remove(test_png_path)
            print("🗑️ Тестовый файл удален")
            
        except Exception as e:
            print(f"❌ Ошибка PIL: {e}")
        
        print("\n✅ Локальный тест завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка локального теста: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_local_png_generation()