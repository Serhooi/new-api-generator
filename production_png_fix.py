#!/usr/bin/env python3
"""
Исправление PNG для продакшена - альтернативные методы
"""

def convert_svg_to_png_production(svg_content, output_path, width=1080, height=1350):
    """
    Продакшен-версия конвертации SVG в PNG
    Приоритет: Playwright → wkhtmltoimage → улучшенный PIL
    """
    
    # Метод 1: Playwright (основной для Render)
    try:
        from playwright.sync_api import sync_playwright
        print("🎭 Конвертирую через Playwright...")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
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
            browser = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html_content)
            page.wait_for_load_state('networkidle')
            page.screenshot(path=output_path, full_page=False)
            browser.close()
        
        print(f"✅ PNG создан через Playwright: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ Playwright ошибка: {e}")
    
    # Метод 2: wkhtmltoimage (если доступен)
    try:
        import subprocess
        import tempfile
        
        print("🖼️ Пробую wkhtmltoimage...")
        
        # Создаем временный HTML файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as html_file:
            html_file.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; width: {width}px; height: {height}px; }}
                    svg {{ width: {width}px; height: {height}px; }}
                </style>
            </head>
            <body>{svg_content}</body>
            </html>
            """)
            html_path = html_file.name
        
        # Конвертируем через wkhtmltoimage
        cmd = [
            'wkhtmltoimage',
            '--width', str(width),
            '--height', str(height),
            '--format', 'png',
            html_path,
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Удаляем временный файл
        import os
        os.unlink(html_path)
        
        if result.returncode == 0:
            print(f"✅ PNG создан через wkhtmltoimage: {output_path}")
            return True
        else:
            print(f"⚠️ wkhtmltoimage ошибка: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ wkhtmltoimage не работает: {e}")
    
    # Метод 3: rsvg-convert (если доступен)
    try:
        import subprocess
        import tempfile
        
        print("🎨 Пробую rsvg-convert...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as svg_file:
            svg_file.write(svg_content)
            svg_path = svg_file.name
        
        cmd = [
            'rsvg-convert',
            '--format', 'png',
            '--width', str(width),
            '--height', str(height),
            '--output', output_path,
            svg_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        import os
        os.unlink(svg_path)
        
        if result.returncode == 0:
            print(f"✅ PNG создан через rsvg-convert: {output_path}")
            return True
        else:
            print(f"⚠️ rsvg-convert ошибка: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ rsvg-convert не работает: {e}")
    
    # Метод 4: Улучшенный PIL fallback (НЕ синие прямоугольники!)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import re
        
        print("🎨 Создаю качественный PNG через PIL...")
        
        # Создаем белое изображение
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Парсим SVG для извлечения информации
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
        rects = re.findall(r'<rect[^>]*fill="([^"]+)"[^>]*>', svg_content)
        
        # Загружаем шрифт
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            try:
                font_large = ImageFont.load_default()
                font_medium = font_large
                font_small = font_large
            except:
                font_large = font_medium = font_small = None
        
        # Рисуем фон (НЕ синий!)
        if rects:
            try:
                bg_color = rects[0]
                if bg_color.startswith('#') and bg_color != '#ffffff':
                    # Используем цвет из SVG, но делаем светлее
                    img = Image.new('RGB', (width, height), color=bg_color)
                    draw = ImageDraw.Draw(img)
            except:
                pass
        
        # Добавляем рамку
        draw.rectangle([20, 20, width-20, height-20], outline='#cccccc', width=4)
        
        # Добавляем заголовок
        if font_large:
            draw.text((width//2, 100), "REAL ESTATE FLYER", fill='#333333', font=font_large, anchor='mm')
        
        # Добавляем найденный текст из SVG
        y_pos = 200
        for i, text in enumerate(texts[:8]):  # Максимум 8 текстов
            if text.strip() and len(text.strip()) > 1:
                font = font_large if i == 0 else font_medium if i < 3 else font_small
                color = '#1976d2' if i == 0 else '#333333' if i < 3 else '#666666'
                
                if font:
                    draw.text((width//2, y_pos), text.strip(), fill=color, font=font, anchor='mm')
                else:
                    draw.text((width//2, y_pos), text.strip(), fill=color, anchor='mm')
                
                y_pos += 60 if i < 3 else 40
        
        # Добавляем имитацию изображения недвижимости
        img_rect = [100, y_pos, width-100, y_pos+300]
        draw.rectangle(img_rect, fill='#f0f0f0', outline='#cccccc', width=2)
        draw.text((width//2, y_pos+150), "🏠 PROPERTY IMAGE", fill='#999999', 
                 font=font_medium if font_medium else None, anchor='mm')
        
        # Добавляем водяной знак
        draw.text((width-200, height-50), "Generated PNG", fill='#dddddd', 
                 font=font_small if font_small else None)
        
        # Сохраняем
        img.save(output_path, 'PNG', quality=95, optimize=True)
        print(f"✅ Качественный PNG создан через PIL: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка PIL: {e}")
        return False

if __name__ == "__main__":
    # Тестируем продакшен версию
    test_svg = '''<svg width="1080" height="1350" xmlns="http://www.w3.org/2000/svg">
        <rect width="1080" height="1350" fill="#f0f8ff"/>
        <text x="540" y="200" text-anchor="middle" font-size="48" fill="#1976d2">LUXURY HOME</text>
        <text x="540" y="300" text-anchor="middle" font-size="32" fill="#333">123 Main Street</text>
        <text x="540" y="400" text-anchor="middle" font-size="36" fill="#4caf50">$750,000</text>
        <text x="540" y="500" text-anchor="middle" font-size="24" fill="#666">3 bed • 2 bath • 2,500 sq ft</text>
    </svg>'''
    
    success = convert_svg_to_png_production(test_svg, 'test_production.png')
    
    if success:
        import os
        size = os.path.getsize('test_production.png')
        print(f"🎉 Продакшен PNG создан: {size:,} bytes")
        os.remove('test_production.png')
    else:
        print("❌ Не удалось создать PNG")