#!/usr/bin/env python3
"""
Исправляем пути для CairoSVG на macOS
"""

import os
import sys

def fix_cairo_paths():
    """Настраиваем пути для Cairo"""
    
    print("🔧 НАСТРОЙКА CAIRO ПУТЕЙ")
    print("=" * 30)
    
    # Пути к Cairo библиотекам
    cairo_lib_path = "/opt/homebrew/Cellar/cairo/1.18.4/lib"
    cairo_lib_file = f"{cairo_lib_path}/libcairo.2.dylib"
    
    # Проверяем что библиотека существует
    if os.path.exists(cairo_lib_file):
        print(f"✅ Cairo библиотека найдена: {cairo_lib_file}")
    else:
        print(f"❌ Cairo библиотека не найдена: {cairo_lib_file}")
        return False
    
    # Настраиваем переменные окружения
    os.environ['DYLD_LIBRARY_PATH'] = f"{cairo_lib_path}:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
    os.environ['CAIRO_LIBRARY_PATH'] = cairo_lib_path
    
    # Пробуем импортировать cairocffi напрямую
    try:
        print("🧪 Тестирую cairocffi...")
        
        # Патчим cairocffi чтобы он искал в правильном месте
        import cairocffi
        
        # Принудительно указываем путь к библиотеке
        cairocffi.cairo = cairocffi.dlopen(cairo_lib_file)
        
        print("✅ cairocffi успешно загружен!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка cairocffi: {e}")
        return False

def test_cairosvg_with_fixed_paths():
    """Тестируем CairoSVG с исправленными путями"""
    
    print("\n🎨 ТЕСТ CAIROSVG С ИСПРАВЛЕННЫМИ ПУТЯМИ")
    print("=" * 45)
    
    try:
        # Сначала исправляем пути
        if not fix_cairo_paths():
            return False
        
        # Теперь импортируем cairosvg
        import cairosvg
        print("✅ CairoSVG импортирован!")
        
        # Тестовый SVG
        test_svg = '''<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#e3f2fd"/>
            <rect x="20" y="20" width="360" height="260" fill="white" stroke="#1976d2" stroke-width="3"/>
            <text x="200" y="80" text-anchor="middle" font-size="28" fill="#1976d2" font-weight="bold">CairoSVG Test</text>
            <text x="200" y="120" text-anchor="middle" font-size="18" fill="#666">Fast SVG to PNG</text>
            <rect x="50" y="140" width="300" height="80" fill="#4caf50"/>
            <text x="200" y="190" text-anchor="middle" font-size="24" fill="white" font-weight="bold">SUCCESS!</text>
        </svg>'''
        
        # Конвертируем в PNG
        output_file = 'test_cairo_fixed.png'
        
        print("🖼️ Конвертирую SVG в PNG через CairoSVG...")
        
        cairosvg.svg2png(
            bytestring=test_svg.encode('utf-8'),
            write_to=output_file,
            output_width=400,
            output_height=300
        )
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✅ PNG создан через CairoSVG: {size} bytes")
            
            if size > 5000:
                print("🎉 CAIROSVG РАБОТАЕТ!")
                os.remove(output_file)
                return True
            else:
                print("⚠️ PNG слишком маленький")
        else:
            print("❌ PNG файл не создан")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    return False

def create_cairo_wrapper():
    """Создаем обертку для CairoSVG"""
    
    wrapper_code = '''
import os
import sys

# Настраиваем пути для Cairo
cairo_lib_path = "/opt/homebrew/Cellar/cairo/1.18.4/lib"
os.environ['DYLD_LIBRARY_PATH'] = f"{cairo_lib_path}:{os.environ.get('DYLD_LIBRARY_PATH', '')}"

def convert_svg_to_png_cairo_fixed(svg_content, output_path, width=1080, height=1350):
    """
    Конвертация SVG в PNG через CairoSVG с исправленными путями
    """
    try:
        print(f"🎨 Конвертирую SVG в PNG через CairoSVG...")
        
        # Импортируем с исправленными путями
        import cairocffi
        cairo_lib_file = f"{cairo_lib_path}/libcairo.2.dylib"
        cairocffi.cairo = cairocffi.dlopen(cairo_lib_file)
        
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
'''
    
    with open('cairo_wrapper.py', 'w') as f:
        f.write(wrapper_code)
    
    print("📝 Создана обертка cairo_wrapper.py")

if __name__ == "__main__":
    print("🚀 ИСПРАВЛЕНИЕ CAIRO НА MACOS")
    print("=" * 40)
    
    # Тестируем исправленные пути
    success = test_cairosvg_with_fixed_paths()
    
    if success:
        print("\n🎉 CAIRO ИСПРАВЛЕН!")
        print("✅ CairoSVG работает с исправленными путями")
        print("✅ Быстрая конвертация SVG → PNG")
        
        # Создаем обертку
        create_cairo_wrapper()
        print("✅ Обертка создана для использования в app.py")
    else:
        print("\n❌ Не удалось исправить Cairo")
        print("Остается использовать Playwright")