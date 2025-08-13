#!/usr/bin/env python3
"""
PNG превью с Playwright
"""

import os
import tempfile
from playwright.sync_api import sync_playwright

def svg_to_png_with_playwright(svg_content, output_path, width=400, height=600):
    """Конвертирует SVG в PNG используя Playwright"""
    try:
        # Создаем HTML с SVG
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
            page = browser.new_page(viewport={'width': width, 'height': height})
            
            # Загружаем HTML
            page.set_content(html_content)
            
            # Ждем загрузки
            page.wait_for_load_state('networkidle')
            
            # Делаем скриншот
            page.screenshot(path=output_path, full_page=True)
            
            browser.close()
        
        print(f"✅ PNG создан через Playwright: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Playwright: {e}")
        return False

def test_playwright_conversion():
    """Тестируем конвертацию с Playwright"""
    
    print("🧪 ТЕСТ PLAYWRIGHT PNG КОНВЕРТАЦИИ")
    print("=" * 50)
    
    # Тестовый SVG
    test_svg = '''<svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="600" fill="#e3f2fd"/>
        <rect x="20" y="20" width="360" height="560" fill="white" stroke="#1976d2" stroke-width="2"/>
        <text x="200" y="100" text-anchor="middle" font-size="24" fill="#1976d2">Template Preview</text>
        <text x="200" y="150" text-anchor="middle" font-size="16" fill="#666">Generated with Playwright</text>
        <circle cx="200" cy="300" r="50" fill="#4caf50"/>
        <text x="200" y="310" text-anchor="middle" font-size="14" fill="white">✓</text>
    </svg>'''
    
    # Тестируем конвертацию
    test_output = 'test_playwright_preview.png'
    
    if svg_to_png_with_playwright(test_svg, test_output):
        print("✅ Playwright конвертация работает!")
        
        # Проверяем размер файла
        if os.path.exists(test_output):
            size = os.path.getsize(test_output)
            print(f"📊 Размер PNG: {size} bytes")
            
            # Удаляем тестовый файл
            os.remove(test_output)
            return True
    
    return False

def update_app_for_playwright():
    """Обновляем app.py для использования Playwright"""
    
    print("🔧 Обновляю app.py для Playwright...")
    
    # Добавляем функцию в app.py
    playwright_function = '''
def convert_svg_to_png_playwright(svg_content, output_path, width=400, height=600):
    """Конвертирует SVG в PNG используя Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        
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
            page.screenshot(path=output_path, full_page=True)
            browser.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Playwright: {{e}}")
        return False

def generate_svg_preview(svg_content, width=400, height=600):
    """Генерирует PNG превью из SVG используя Playwright"""
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_png_path = f.name
        
        if convert_svg_to_png_playwright(svg_content, temp_png_path, width, height):
            with open(temp_png_path, 'rb') as f:
                png_data = f.read()
            os.unlink(temp_png_path)
            return png_data
        else:
            print("❌ Не удалось создать PNG превью")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка генерации PNG превью: {{e}}")
        return None
'''
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем функцию generate_svg_preview
    import re
    content = re.sub(
        r'def generate_svg_preview\(svg_content, width=400, height=600\):.*?return svg_content',
        playwright_function.strip(),
        content,
        flags=re.DOTALL
    )
    
    # Исправляем остальные функции для PNG
    content = content.replace('.svg', '.png')
    content = content.replace('image/svg+xml', 'image/png')
    content = content.replace('svg_data', 'png_data')
    content = content.replace('svg_path', 'png_path')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py обновлен для Playwright PNG превью!")

if __name__ == "__main__":
    if test_playwright_conversion():
        print("\n🎉 Playwright работает! Обновляю app.py...")
        update_app_for_playwright()
        print("\n✅ PNG превью с Playwright настроены!")
        print("📋 Теперь превью будут красивые PNG файлы")
    else:
        print("\n❌ Playwright не работает")