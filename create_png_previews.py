#!/usr/bin/env python3
"""
Создание PNG превью без Cairo - используем альтернативные методы
"""

import os
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def svg_to_png_with_wkhtmltopdf(svg_content, output_path, width=400, height=600):
    """Конвертирует SVG в PNG используя wkhtmltopdf"""
    try:
        # Создаем временный HTML файл с SVG
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; }}
                svg {{ width: {width}px; height: {height}px; }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            # Конвертируем HTML в PNG
            subprocess.run([
                'wkhtmltoimage',
                '--width', str(width),
                '--height', str(height),
                '--format', 'png',
                html_path,
                output_path
            ], check=True, capture_output=True)
            
            print(f"✅ PNG создан через wkhtmltoimage: {output_path}")
            return True
            
        finally:
            os.unlink(html_path)
            
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️ wkhtmltoimage недоступен: {e}")
        return False

def svg_to_png_with_chrome(svg_content, output_path, width=400, height=600):
    """Конвертирует SVG в PNG используя headless Chrome"""
    try:
        # Создаем временный HTML файл
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background: white; }}
                svg {{ width: {width}px; height: {height}px; }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            # Используем Chrome для скриншота
            subprocess.run([
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '--headless',
                '--disable-gpu',
                '--screenshot=' + output_path,
                '--window-size=' + f"{width},{height}",
                '--default-background-color=0',
                'file://' + html_path
            ], check=True, capture_output=True)
            
            print(f"✅ PNG создан через Chrome: {output_path}")
            return True
            
        finally:
            os.unlink(html_path)
            
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️ Chrome недоступен: {e}")
        return False

def create_fallback_png(svg_content, output_path, width=400, height=600):
    """Создает PNG заглушку с информацией о шаблоне"""
    try:
        # Создаем изображение заглушку
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Пытаемся извлечь название из SVG
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', svg_content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Template Preview"
        
        # Рисуем рамку
        draw.rectangle([10, 10, width-10, height-10], outline='#cccccc', width=2)
        
        # Добавляем текст
        try:
            # Пытаемся использовать системный шрифт
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Центрируем текст
        text_bbox = draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), title, fill='#333333', font=font)
        
        # Добавляем иконку SVG
        draw.text((x, y - 30), "📄 SVG Template", fill='#666666', font=font)
        
        # Сохраняем
        img.save(output_path, 'PNG')
        print(f"✅ Fallback PNG создан: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания fallback PNG: {e}")
        return False

def convert_svg_to_png_advanced(svg_content, output_path, width=400, height=600):
    """Продвинутая конвертация SVG в PNG с несколькими методами"""
    
    print(f"🎨 Конвертирую SVG в PNG: {output_path}")
    
    # Метод 1: wkhtmltoimage
    if svg_to_png_with_wkhtmltopdf(svg_content, output_path, width, height):
        return True
    
    # Метод 2: Chrome headless
    if svg_to_png_with_chrome(svg_content, output_path, width, height):
        return True
    
    # Метод 3: Fallback заглушка
    print("⚠️ Использую fallback метод для PNG")
    return create_fallback_png(svg_content, output_path, width, height)

def update_app_with_png_previews():
    """Обновляет app.py для использования PNG превью"""
    
    print("🔧 Обновляю app.py для PNG превью...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем функцию generate_svg_preview
    new_preview_function = '''
def generate_svg_preview(svg_content, width=400, height=600):
    """Генерирует PNG превью из SVG"""
    try:
        # Создаем временный PNG файл
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_png_path = f.name
        
        # Конвертируем SVG в PNG
        from create_png_previews import convert_svg_to_png_advanced
        if convert_svg_to_png_advanced(svg_content, temp_png_path, width, height):
            # Читаем PNG файл
            with open(temp_png_path, 'rb') as f:
                png_data = f.read()
            
            # Удаляем временный файл
            os.unlink(temp_png_path)
            return png_data
        else:
            print("❌ Не удалось создать PNG превью")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка генерации PNG превью: {e}")
        return None
'''
    
    # Заменяем функцию в коде
    import re
    content = re.sub(
        r'def generate_svg_preview\(svg_content, width=400, height=600\):.*?return svg_content',
        new_preview_function.strip(),
        content,
        flags=re.DOTALL
    )
    
    # Исправляем API endpoints для PNG
    content = content.replace('preview_url = f\'/output/previews/{template_id}_preview.svg\'', 
                             'preview_url = f\'/output/previews/{template_id}_preview.png\'')
    
    content = content.replace('svg_path = preview_path.replace(\'.png\', \'.svg\')',
                             'png_path = preview_path')
    
    content = content.replace('with open(svg_path, \'w\', encoding=\'utf-8\') as f:\\n                        f.write(svg_data)',
                             'with open(png_path, \'wb\') as f:\\n                        f.write(png_data)')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py обновлен для PNG превью!")

if __name__ == "__main__":
    print("🎨 НАСТРОЙКА PNG ПРЕВЬЮ БЕЗ CAIRO")
    print("=" * 50)
    
    # Тестируем доступные методы
    test_svg = '''<svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="600" fill="#f0f0f0"/>
        <text x="200" y="300" text-anchor="middle" font-size="24">Test Preview</text>
    </svg>'''
    
    print("🧪 Тестирую методы конвертации...")
    
    # Тест wkhtmltoimage
    if svg_to_png_with_wkhtmltopdf(test_svg, 'test_wkhtml.png'):
        print("✅ wkhtmltoimage работает")
        os.remove('test_wkhtml.png')
    
    # Тест Chrome
    if svg_to_png_with_chrome(test_svg, 'test_chrome.png'):
        print("✅ Chrome headless работает")
        os.remove('test_chrome.png')
    
    # Тест fallback
    if create_fallback_png(test_svg, 'test_fallback.png'):
        print("✅ Fallback метод работает")
        os.remove('test_fallback.png')
    
    # Обновляем app.py
    update_app_with_png_previews()
    
    print("\n🎉 PNG превью настроены!")
    print("📋 Доступные методы:")
    print("  1. wkhtmltoimage (если установлен)")
    print("  2. Chrome headless (если установлен)")
    print("  3. Fallback заглушки (всегда работает)")