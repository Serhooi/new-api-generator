#!/usr/bin/env python3
"""
Тест локальных SVG файлов main.svg и photo.svg
"""

import os
import subprocess
import tempfile
import re

def test_svg_cleaning_and_conversion(svg_file):
    """Тестируем очистку и конвертацию SVG файла"""
    
    print(f"\n🧪 Тестирую файл: {svg_file}")
    
    if not os.path.exists(svg_file):
        print(f"❌ Файл не найден: {svg_file}")
        return False
    
    # Читаем SVG
    with open(svg_file, 'r') as f:
        svg_content = f.read()
    
    print(f"📊 Размер оригинального SVG: {len(svg_content)} символов")
    
    # Анализируем проблемные теги
    image_tags = len(re.findall(r'<image[^>]*>', svg_content))
    use_tags = len(re.findall(r'<use[^>]*>', svg_content))
    unclosed_image = len(re.findall(r'<image[^>]*[^/]>', svg_content))
    unclosed_use = len(re.findall(r'<use[^>]*[^/]>', svg_content))
    
    print(f"🔍 Анализ тегов:")
    print(f"  - image тегов: {image_tags} (незакрытых: {unclosed_image})")
    print(f"  - use тегов: {use_tags} (незакрытых: {unclosed_use})")
    
    # Применяем нашу радикальную очистку
    print("🔥 Применяю радикальную очистку...")
    cleaned_svg = svg_content
    
    # 1. Убираем невалидные символы
    cleaned_svg = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned_svg)
    
    # 2. Исправляем амперсанды
    cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
    
    # 3. РАДИКАЛЬНО - УБИРАЕМ ВСЕ IMAGE ТЕГИ ПОЛНОСТЬЮ
    cleaned_svg = re.sub(r'<image[^>]*/?>', '', cleaned_svg)
    
    # 4. УБИРАЕМ ВСЕ USE ТЕГИ ПОЛНОСТЬЮ
    cleaned_svg = re.sub(r'<use[^>]*/?>', '', cleaned_svg)
    
    # 5. Исправляем оставшиеся самозакрывающиеся теги
    self_closing_tags = ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop']
    
    for tag in self_closing_tags:
        cleaned_svg = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\1/>', cleaned_svg)
    
    # 6. Убираем лишние пробелы
    cleaned_svg = re.sub(r'\s+', ' ', cleaned_svg)
    
    print(f"✅ Очистка завершена: {len(svg_content)} → {len(cleaned_svg)} символов")
    
    # Проверяем что проблемные теги удалены
    remaining_image = len(re.findall(r'<image[^>]*>', cleaned_svg))
    remaining_use = len(re.findall(r'<use[^>]*>', cleaned_svg))
    
    print(f"🔍 После очистки:")
    print(f"  - image тегов: {remaining_image}")
    print(f"  - use тегов: {remaining_use}")
    
    if remaining_image == 0 and remaining_use == 0:
        print("✅ Все проблемные теги удалены!")
    else:
        print("⚠️ Остались проблемные теги!")
    
    # Сохраняем очищенный SVG
    cleaned_file = f"cleaned_{os.path.basename(svg_file)}"
    with open(cleaned_file, 'w') as f:
        f.write(cleaned_svg)
    
    print(f"💾 Очищенный SVG сохранен: {cleaned_file}")
    
    # Тестируем конвертацию в PNG через rsvg-convert
    print("🖼️ Тестирую конвертацию в PNG...")
    
    png_file = f"test_{os.path.basename(svg_file).replace('.svg', '.png')}"
    
    try:
        # Проверяем что rsvg-convert доступен
        version_result = subprocess.run(['rsvg-convert', '--version'], 
                                      capture_output=True, text=True, timeout=5)
        if version_result.returncode != 0:
            print("❌ rsvg-convert не доступен")
            return False
        
        print(f"✅ rsvg-convert найден: {version_result.stdout.strip()}")
        
        # Конвертируем через stdin
        result = subprocess.run(
            ["rsvg-convert", "-w", "400"],
            input=cleaned_svg.encode("utf-8"),
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
                print("✅ PNG файл валидный!")
                return True
            else:
                print("❌ PNG файл пустой или не создался")
                return False
        else:
            print(f"❌ rsvg-convert ошибка: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return False

def test_cairosvg_fallback(svg_file):
    """Тестируем CairoSVG как fallback"""
    
    print(f"\n🎨 Тестирую CairoSVG для: {svg_file}")
    
    try:
        import cairosvg
        
        # Читаем очищенный SVG
        cleaned_file = f"cleaned_{os.path.basename(svg_file)}"
        if not os.path.exists(cleaned_file):
            print(f"❌ Очищенный файл не найден: {cleaned_file}")
            return False
        
        with open(cleaned_file, 'r') as f:
            cleaned_svg = f.read()
        
        # Конвертируем через CairoSVG
        png_bytes = cairosvg.svg2png(bytestring=cleaned_svg.encode('utf-8'), 
                                   output_width=400)
        
        cairo_png_file = f"cairo_{os.path.basename(svg_file).replace('.svg', '.png')}"
        with open(cairo_png_file, 'wb') as f:
            f.write(png_bytes)
        
        print(f"✅ CairoSVG PNG создан: {cairo_png_file} ({len(png_bytes)} байт)")
        return True
        
    except ImportError:
        print("⚠️ CairoSVG не установлен")
        return False
    except Exception as e:
        print(f"❌ CairoSVG ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🔥 ТЕСТИРОВАНИЕ ЛОКАЛЬНЫХ SVG ФАЙЛОВ")
    print("=" * 50)
    
    svg_files = ['main.svg', 'photo.svg']
    results = {}
    
    for svg_file in svg_files:
        print(f"\n{'='*20} {svg_file.upper()} {'='*20}")
        
        # Тест 1: Очистка и rsvg-convert
        rsvg_success = test_svg_cleaning_and_conversion(svg_file)
        
        # Тест 2: CairoSVG fallback
        cairo_success = test_cairosvg_fallback(svg_file)
        
        results[svg_file] = {
            'rsvg': rsvg_success,
            'cairo': cairo_success
        }
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    
    for svg_file, result in results.items():
        print(f"\n📄 {svg_file}:")
        print(f"  ✅ rsvg-convert: {'РАБОТАЕТ' if result['rsvg'] else 'НЕ РАБОТАЕТ'}")
        print(f"  ✅ CairoSVG: {'РАБОТАЕТ' if result['cairo'] else 'НЕ РАБОТАЕТ'}")
    
    # Общий статус
    all_rsvg = all(r['rsvg'] for r in results.values())
    all_cairo = all(r['cairo'] for r in results.values())
    
    print(f"\n🎯 ОБЩИЙ СТАТУС:")
    print(f"  rsvg-convert: {'✅ ВСЕ РАБОТАЕТ' if all_rsvg else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    print(f"  CairoSVG: {'✅ ВСЕ РАБОТАЕТ' if all_cairo else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    
    if all_rsvg or all_cairo:
        print("\n🎉 СИСТЕМА PNG КОНВЕРТАЦИИ РАБОТАЕТ!")
    else:
        print("\n❌ СИСТЕМА PNG КОНВЕРТАЦИИ НЕ РАБОТАЕТ!")

if __name__ == "__main__":
    main()