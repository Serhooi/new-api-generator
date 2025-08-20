#!/usr/bin/env python3
"""
Тест Playwright для генерации превью
"""

import os
import tempfile

def test_playwright_installation():
    """Проверяем установку Playwright"""
    
    print("🎭 ТЕСТ PLAYWRIGHT")
    print("=" * 50)
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright импортирован успешно")
        
        # Проверяем браузеры
        with sync_playwright() as p:
            print("🌐 Доступные браузеры:")
            
            try:
                browser = p.chromium.launch()
                print("  ✅ Chromium работает")
                browser.close()
            except Exception as e:
                print(f"  ❌ Chromium: {e}")
            
            try:
                browser = p.firefox.launch()
                print("  ✅ Firefox работает")
                browser.close()
            except Exception as e:
                print(f"  ❌ Firefox: {e}")
                
        return True
        
    except ImportError as e:
        print(f"❌ Playwright не установлен: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка Playwright: {e}")
        return False

def test_svg_to_png_conversion():
    """Тестируем конвертацию SVG в PNG"""
    
    print("\n🖼️ ТЕСТ КОНВЕРТАЦИИ SVG → PNG")
    print("=" * 50)
    
    # Тестовый SVG
    test_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="600" fill="#f0f8ff"/>
  <rect x="20" y="20" width="360" height="560" fill="white" stroke="#ddd" stroke-width="2"/>
  <text x="200" y="100" text-anchor="middle" font-family="Arial" font-size="24" fill="#333">
    Test Template
  </text>
  <rect x="50" y="150" width="300" height="200" fill="#e6f3ff" stroke="#4a90e2" stroke-width="2"/>
  <text x="200" y="260" text-anchor="middle" font-family="Arial" font-size="16" fill="#4a90e2">
    Preview Content
  </text>
  <circle cx="200" cy="450" r="50" fill="#ff6b6b"/>
  <text x="200" y="455" text-anchor="middle" font-family="Arial" font-size="14" fill="white">
    Logo
  </text>
</svg>'''
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        output_path = tmp_file.name
    
    try:
        from png_preview_with_playwright import svg_to_png_with_playwright
        
        print("🔄 Конвертирую тестовый SVG...")
        success = svg_to_png_with_playwright(test_svg, output_path, 400, 600)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PNG создан: {output_path}")
            print(f"📏 Размер файла: {file_size} bytes")
            
            # Проверяем что это валидный PNG
            try:
                from PIL import Image
                img = Image.open(output_path)
                print(f"📐 Размеры PNG: {img.size}")
                print(f"🎨 Режим: {img.mode}")
                img.close()
                print("✅ PNG файл валидный")
            except Exception as e:
                print(f"❌ PNG файл поврежден: {e}")
            
            return True
        else:
            print("❌ PNG не создан")
            return False
            
    except ImportError:
        print("❌ Модуль png_preview_with_playwright не найден")
        return False
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return False
    finally:
        # Удаляем временный файл
        try:
            os.unlink(output_path)
        except:
            pass

def test_pil_fallback():
    """Тестируем PIL fallback"""
    
    print("\n🎨 ТЕСТ PIL FALLBACK")
    print("=" * 40)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем тестовое изображение
        img = Image.new('RGB', (400, 600), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        # Градиент
        for y in range(600):
            color_val = int(248 - (y * 20 / 600))
            draw.line([(0, y), (400, y)], fill=(color_val, color_val + 2, color_val + 5))
        
        # Контент
        draw.rectangle([20, 20, 380, 580], outline='#dee2e6', width=3)
        draw.text((200, 300), "PIL Fallback Test", fill='#2d3748', anchor='mm')
        
        # Сохраняем
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        img.save(output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ PIL превью создано: {output_path}")
            print(f"📏 Размер файла: {file_size} bytes")
            
            # Удаляем файл
            os.unlink(output_path)
            return True
        else:
            print("❌ PIL превью не создано")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка PIL: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🧪 ТЕСТ СИСТЕМЫ ГЕНЕРАЦИИ ПРЕВЬЮ")
    print("=" * 60)
    
    playwright_ok = test_playwright_installation()
    conversion_ok = test_svg_to_png_conversion() if playwright_ok else False
    pil_ok = test_pil_fallback()
    
    print(f"\n📊 ИТОГИ:")
    print(f"🎭 Playwright: {'✅' if playwright_ok else '❌'}")
    print(f"🖼️ SVG → PNG: {'✅' if conversion_ok else '❌'}")
    print(f"🎨 PIL Fallback: {'✅' if pil_ok else '❌'}")
    
    if conversion_ok:
        print("\n🎉 Система превью работает полностью!")
    elif pil_ok:
        print("\n⚠️ Только PIL fallback работает - превью будут простыми")
    else:
        print("\n❌ Система превью не работает")

if __name__ == "__main__":
    main()