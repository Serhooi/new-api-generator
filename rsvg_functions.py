
def convert_svg_to_png_rsvg(svg_content, output_path, width=1080, height=1350):
    """
    Конвертация SVG в PNG через rsvg-convert (самый быстрый нативный метод)
    """
    import subprocess
    import tempfile
    import os
    
    try:
        print(f"🎨 Конвертирую SVG в PNG через rsvg-convert...")
        
        # Создаем временный SVG файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as svg_file:
            svg_file.write(svg_content)
            svg_path = svg_file.name
        
        # Конвертируем через rsvg-convert
        cmd = [
            'rsvg-convert',
            '--format', 'png',
            '--width', str(width),
            '--height', str(height),
            '--output', output_path,
            svg_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Удаляем временный SVG
        os.unlink(svg_path)
        
        if result.returncode == 0:
            print(f"✅ PNG создан через rsvg-convert: {output_path}")
            return True
        else:
            print(f"❌ Ошибка rsvg-convert: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка rsvg-convert: {e}")
        return False

def convert_svg_to_png_ultimate_rsvg(svg_content, output_path, width=1080, height=1350):
    """
    Ультимативная конвертация с rsvg-convert в приоритете
    """
    
    # Метод 1: rsvg-convert (самый быстрый нативный)
    if convert_svg_to_png_rsvg(svg_content, output_path, width, height):
        return True
    
    # Метод 2: Playwright (если rsvg-convert не работает)
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
        
        # Парсим содержимое SVG
        colors = re.findall(r'fill="([^"]+)"', svg_content)
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
        
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
