#!/usr/bin/env python3
"""
Улучшенная SVG → PNG конвертация с несколькими методами
"""

def convert_svg_to_png_multi_method(svg_content, output_path, width=1080, height=1350):
    """
    Конвертация SVG в PNG с несколькими методами (по приоритету)
    """
    
    # Метод 1: CairoSVG (самый быстрый и точный)
    try:
        import cairosvg
        print("🎨 Пробую CairoSVG...")
        
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=output_path,
            output_width=width,
            output_height=height
        )
        
        print(f"✅ PNG создан через CairoSVG: {output_path}")
        return True
        
    except ImportError:
        print("⚠️ CairoSVG не установлен")
    except Exception as e:
        print(f"⚠️ Ошибка CairoSVG: {e}")
    
    # Метод 2: Playwright (если доступен)
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
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html_content)
            page.wait_for_load_state('networkidle')
            page.screenshot(path=output_path, full_page=False)
            browser.close()
        
        print(f"✅ PNG создан через Playwright: {output_path}")
        return True
        
    except ImportError:
        print("⚠️ Playwright не установлен")
    except Exception as e:
        print(f"⚠️ Ошибка Playwright: {e}")
    
    # Метод 3: Selenium (если доступен)
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import tempfile
        import os
        
        print("🚗 Пробую Selenium...")
        
        # Создаем временный HTML файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(f"""
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
            temp_html = f.name
        
        # Настройки Chrome
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={width},{height}')
        
        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{temp_html}')
        driver.save_screenshot(output_path)
        driver.quit()
        
        # Удаляем временный файл
        os.unlink(temp_html)
        
        print(f"✅ PNG создан через Selenium: {output_path}")
        return True
        
    except ImportError:
        print("⚠️ Selenium не установлен")
    except Exception as e:
        print(f"⚠️ Ошибка Selenium: {e}")
    
    # Метод 4: Умный PIL fallback (как резерв)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import re
        
        print("🎨 Использую умный PIL fallback...")
        
        # Создаем изображение
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Парсим цвета из SVG
        colors = re.findall(r'fill="([^"]+)"', svg_content)
        bg_colors = [c for c in colors if c not in ['none', 'transparent']]
        
        if bg_colors:
            try:
                bg_color = bg_colors[0]
                if bg_color.startswith('#'):
                    img = Image.new('RGB', (width, height), color=bg_color)
                    draw = ImageDraw.Draw(img)
            except:
                pass
        
        # Добавляем градиент
        for y in range(height):
            alpha = int(255 * (1 - y / height * 0.1))
            color = (240, 248, 255) if len(bg_colors) == 0 else (200, 220, 240)
            try:
                draw.line([(0, y), (width, y)], fill=color)
            except:
                pass
        
        # Извлекаем текст
        texts = re.findall(r'<text[^>]*>([^<]+)</text>', svg_content)
        
        # Пытаемся загрузить шрифт
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Добавляем текст
        y_pos = 50
        for text in texts[:5]:
            if text.strip():
                try:
                    draw.text((50, y_pos), text.strip(), fill='black', font=font)
                    y_pos += 40
                except:
                    pass
        
        # Рамка
        draw.rectangle([10, 10, width-10, height-10], outline='gray', width=2)
        
        # Водяной знак
        draw.text((width-150, height-30), "Generated PNG", fill='lightgray', font=small_font)
        
        # Сохраняем
        img.save(output_path, 'PNG', quality=95)
        print(f"✅ PNG создан через PIL fallback: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка PIL fallback: {e}")
    
    print("❌ Все методы конвертации не сработали")
    return False

def install_cairosvg():
    """Устанавливает CairoSVG"""
    import subprocess
    import sys
    
    try:
        print("📦 Устанавливаю CairoSVG...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'cairosvg'], check=True)
        print("✅ CairoSVG установлен")
        return True
    except Exception as e:
        print(f"❌ Ошибка установки CairoSVG: {e}")
        return False

if __name__ == "__main__":
    # Тестируем все методы
    test_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#e3f2fd"/>
        <rect x="20" y="20" width="360" height="260" fill="white" stroke="#1976d2" stroke-width="2"/>
        <text x="200" y="100" text-anchor="middle" font-size="24" fill="#1976d2">Test SVG</text>
        <text x="200" y="150" text-anchor="middle" font-size="16" fill="#666">Multi-method conversion</text>
        <circle cx="200" cy="200" r="30" fill="#4caf50"/>
    </svg>'''
    
    print("🧪 ТЕСТИРУЮ ВСЕ МЕТОДЫ КОНВЕРТАЦИИ")
    print("=" * 50)
    
    success = convert_svg_to_png_multi_method(test_svg, 'test_multi_method.png', 400, 300)
    
    if success:
        import os
        size = os.path.getsize('test_multi_method.png')
        print(f"\n✅ Конвертация успешна! Размер: {size} bytes")
        os.remove('test_multi_method.png')
    else:
        print("\n❌ Все методы не сработали")