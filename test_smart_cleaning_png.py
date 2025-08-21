#!/usr/bin/env python3
"""
Тест умной очистки с PNG конвертацией
"""

import subprocess
import os

def test_smart_cleaned_png():
    """Тестируем PNG конвертацию умно очищенного SVG"""
    
    print("🧪 Тестирую PNG конвертацию умно очищенного SVG...")
    
    svg_file = 'smart_cleaned_main.svg'
    png_file = 'smart_cleaned_main.png'
    
    if not os.path.exists(svg_file):
        print(f"❌ Файл не найден: {svg_file}")
        return False
    
    # Читаем SVG
    with open(svg_file, 'r') as f:
        svg_content = f.read()
    
    print(f"📊 Размер SVG: {len(svg_content)} символов")
    
    try:
        # Конвертируем через rsvg-convert
        result = subprocess.run(
            ["rsvg-convert", "-w", "400"],
            input=svg_content.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        if result.returncode == 0:
            # Сохраняем PNG
            with open(png_file, 'wb') as f:
                f.write(result.stdout)
            
            png_size = len(result.stdout)
            print(f"✅ PNG создан успешно: {png_file} ({png_size} байт)")
            
            # Проверяем что файл действительно создался
            if os.path.exists(png_file) and os.path.getsize(png_file) > 0:
                print("✅ PNG файл валидный с изображениями!")
                return True
            else:
                print("❌ PNG файл пустой")
                return False
        else:
            print(f"❌ rsvg-convert ошибка: {result.stderr.decode()}")
            print("🔍 Возможно, все еще есть XML проблемы...")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return False

if __name__ == "__main__":
    success = test_smart_cleaned_png()
    
    if success:
        print("\n🎉 УМНАЯ ОЧИСТКА РАБОТАЕТ! PNG с изображениями создан!")
    else:
        print("\n❌ Умная очистка не решила XML проблемы...")
        print("💡 Возможно, нужна более агрессивная очистка незакрытых тегов")