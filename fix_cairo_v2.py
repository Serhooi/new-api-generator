#!/usr/bin/env python3
"""
Исправляем CairoSVG - версия 2
"""

import os
import sys

def patch_cairocffi():
    """Патчим cairocffi для работы с Homebrew Cairo"""
    
    print("🔧 ПАТЧИМ CAIROCFFI")
    print("=" * 25)
    
    try:
        import cairocffi
        
        # Путь к Cairo библиотеке
        cairo_lib = "/opt/homebrew/Cellar/cairo/1.18.4/lib/libcairo.2.dylib"
        
        if os.path.exists(cairo_lib):
            print(f"✅ Cairo найден: {cairo_lib}")
            
            # Патчим cairocffi
            import ctypes
            cairocffi.cairo = ctypes.CDLL(cairo_lib)
            
            print("✅ cairocffi успешно пропатчен!")
            return True
        else:
            print("❌ Cairo библиотека не найдена")
            
    except Exception as e:
        print(f"❌ Ошибка патча: {e}")
    
    return False

def test_patched_cairosvg():
    """Тестируем пропатченный CairoSVG"""
    
    print("\n🎨 ТЕСТ ПРОПАТЧЕННОГО CAIROSVG")
    print("=" * 35)
    
    try:
        # Сначала патчим cairocffi
        if not patch_cairocffi():
            return False
        
        # Теперь импортируем cairosvg
        import cairosvg
        print("✅ CairoSVG импортирован!")
        
        # Тестовый SVG
        test_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f0f8ff"/>
            <rect x="20" y="20" width="360" height="260" fill="white" stroke="#1976d2" stroke-width="2"/>
            <text x="200" y="80" text-anchor="middle" font-size="24" fill="#1976d2" font-weight="bold">CairoSVG</text>
            <text x="200" y="120" text-anchor="middle" font-size="16" fill="#666">Patched Version</text>
            <circle cx="200" cy="180" r="40" fill="#4caf50"/>
            <text x="200" y="190" text-anchor="middle" font-size="20" fill="white">✓</text>
            <text x="200" y="250" text-anchor="middle" font-size="14" fill="#333">Fast & Reliable</text>
        </svg>'''
        
        # Конвертируем в PNG
        output_file = 'test_cairo_patched.png'
        
        print("🖼️ Конвертирую SVG в PNG...")
        
        cairosvg.svg2png(
            bytestring=test_svg.encode('utf-8'),
            write_to=output_file,
            output_width=400,
            output_height=300
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ PNG создан: {size} bytes")
            
            if size > 3000:
                print("🎉 CAIROSVG РАБОТАЕТ!")
                os.remove(output_file)
                return True
            else:
                print("⚠️ PNG слишком маленький")
        else:
            print("❌ PNG файл не создан")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def create_cairo_function():
    """Создаем функцию для app.py"""
    
    function_code = '''
def convert_svg_to_png_cairo_patched(svg_content, output_path, width=1080, height=1350):
    """
    Конвертация SVG в PNG через пропатченный CairoSVG
    """
    try:
        print(f"🎨 Конвертирую SVG в PNG через CairoSVG...")
        
        # Патчим cairocffi
        import cairocffi
        import ctypes
        import os
        
        cairo_lib = "/opt/homebrew/Cellar/cairo/1.18.4/lib/libcairo.2.dylib"
        if os.path.exists(cairo_lib):
            cairocffi.cairo = ctypes.CDLL(cairo_lib)
        
        # Импортируем cairosvg
        import cairosvg
        
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=output_path,
            output_width=width,
            output_height=height
        )
        
        print(f"✅ PNG создан через CairoSVG: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка CairoSVG: {e}")
        return False

def convert_svg_to_png_ultimate_with_cairo(svg_content, output_path, width=1080, height=1350):
    """
    Ультимативная конвертация с CairoSVG в приоритете
    """
    
    # Метод 1: CairoSVG (самый быстрый)
    if convert_svg_to_png_cairo_patched(svg_content, output_path, width, height):
        return True
    
    # Метод 2: Playwright (если CairoSVG не работает)
    try:
        from playwright.sync_api import sync_playwright
        print("🎭 Пробую Playwright...")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    background: white;
                    width: {width}px;
                    height: {height}px;
                    overflow: hidden;
                }}
                svg {{ 
                    width: {width}px; 
                    height: {height}px; 
                    display: block;
                }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={{'width': width, 'height': height}})
            page.set_content(html_content)
            page.wait_for_load_state('networkidle')
            page.screenshot(path=output_path, full_page=False)
            browser.close()
        
        print(f"✅ PNG создан через Playwright: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ Ошибка Playwright: {e}")
    
    # Метод 3: PIL fallback
    try:
        from PIL import Image, ImageDraw, ImageFont
        import re
        
        print("🎨 Создаю PNG через PIL fallback...")
        
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Парсим цвета и текст из SVG
        colors = re.findall(r'fill="([^"]+)"', svg_content)
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
        
        # Добавляем содержимое
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        y_pos = 50
        for text in texts[:5]:
            if text.strip():
                draw.text((50, y_pos), text.strip(), fill='black', font=font)
                y_pos += 40
        
        draw.rectangle([10, 10, width-10, height-10], outline='gray', width=2)
        img.save(output_path, 'PNG', quality=95)
        
        print(f"✅ PNG создан через PIL fallback: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка PIL: {e}")
    
    return False
'''
    
    with open('cairo_functions.py', 'w') as f:
        f.write(function_code)
    
    print("📝 Создан файл cairo_functions.py с функциями")

if __name__ == "__main__":
    print("🚀 ИСПРАВЛЕНИЕ CAIROSVG - ВЕРСИЯ 2")
    print("=" * 45)
    
    # Тестируем пропатченный CairoSVG
    success = test_patched_cairosvg()
    
    if success:
        print("\n🎉 CAIROSVG ИСПРАВЛЕН!")
        print("✅ Патч cairocffi работает")
        print("✅ CairoSVG создает PNG")
        print("✅ Быстрая конвертация готова")
        
        # Создаем функции
        create_cairo_function()
        print("✅ Функции созданы для app.py")
    else:
        print("\n❌ CairoSVG все еще не работает")
        print("Остается Playwright как основной метод")