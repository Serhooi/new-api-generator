#!/usr/bin/env python3
"""
Исправление проблем с base64 данными в SVG
"""

import re

def clean_base64_in_svg(svg_content):
    """
    Очищаем base64 данные в SVG от невалидных символов
    """
    print("🧹 Очищаю base64 данные в SVG...")
    
    cleaned = svg_content
    
    # 1. Убираем невалидные символы
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    # 2. Исправляем амперсанды
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    
    # 3. АГРЕССИВНАЯ очистка base64 данных
    def clean_base64_data(match):
        base64_data = match.group(1)
        
        # Убираем все невалидные символы из base64
        # Валидные символы base64: A-Z, a-z, 0-9, +, /, =
        cleaned_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', base64_data)
        
        # Убираем лишние символы = в конце (должно быть максимум 2)
        cleaned_base64 = re.sub(r'=+$', '', cleaned_base64)
        
        # Добавляем правильное количество = для выравнивания
        remainder = len(cleaned_base64) % 4
        if remainder == 2:
            cleaned_base64 += '=='
        elif remainder == 3:
            cleaned_base64 += '='
        
        return f'data:image/jpeg;base64,{cleaned_base64}'
    
    # Ищем и очищаем все base64 данные
    pattern = r'data:image/[^;]+;base64,([^"\'>\s]+)'
    matches = re.findall(pattern, cleaned)
    print(f"🔍 Найдено {len(matches)} base64 изображений")
    
    cleaned = re.sub(pattern, clean_base64_data, cleaned)
    
    # 4. Исправляем image теги (на всякий случай)
    def fix_image_tag(match):
        tag_content = match.group(1)
        if tag_content.endswith('/'):
            return match.group(0)
        return f'<image{tag_content}/>'
    
    cleaned = re.sub(r'<image([^>]*?)>', fix_image_tag, cleaned)
    
    # 5. Исправляем use теги
    def fix_use_tag(match):
        tag_content = match.group(1)
        if tag_content.endswith('/'):
            return match.group(0)
        return f'<use{tag_content}/>'
    
    cleaned = re.sub(r'<use([^>]*?)>', fix_use_tag, cleaned)
    
    # 6. Убираем лишние пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    print(f"🧹 Base64 очистка завершена: {len(svg_content)} → {len(cleaned)} символов")
    
    return cleaned

def update_app_with_base64_cleaning():
    """Обновляем app.py с очисткой base64"""
    
    print("📝 Читаю app.py...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Находим и заменяем умную очистку на очистку с base64
    old_cleaning = '''            # УМНАЯ ОЧИСТКА SVG - ИСПРАВЛЯЕМ ТЕГИ, НО СОХРАНЯЕМ ИЗОБРАЖЕНИЯ
            print("🧠 УМНАЯ очистка SVG - исправляю теги, но сохраняю изображения...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. УМНО исправляем image теги - НЕ удаляем, а закрываем
            def fix_image_tag(match):
                tag_content = match.group(1)
                if tag_content.endswith('/'):
                    return match.group(0)
                return f'<image{tag_content}/>'
            
            cleaned_svg = re.sub(r'<image([^>]*?)>', fix_image_tag, cleaned_svg)
            
            # 4. УМНО исправляем use теги
            def fix_use_tag(match):
                tag_content = match.group(1)
                if tag_content.endswith('/'):
                    return match.group(0)
                return f'<use{tag_content}/>'
            
            cleaned_svg = re.sub(r'<use([^>]*?)>', fix_use_tag, cleaned_svg)
            
            # 5. Исправляем другие самозакрывающиеся теги
            self_closing_tags = ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop']
            
            for tag in self_closing_tags:
                def fix_tag_func(match):
                    tag_content = match.group(1)
                    if tag_content.endswith('/'):
                        return match.group(0)
                    return f'<{tag}{tag_content}/>'
                
                cleaned_svg = re.sub(f'<{tag}([^>]*?)>', fix_tag_func, cleaned_svg)
            
            # 6. Убираем лишние пробелы
            cleaned_svg = re.sub(r'\\s+', ' ', cleaned_svg)
            
            print(f"🧠 Умная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    new_cleaning = '''            # УЛЬТИМАТИВНАЯ ОЧИСТКА SVG + BASE64
            print("🧹 УЛЬТИМАТИВНАЯ очистка SVG + base64 данных...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. АГРЕССИВНАЯ очистка base64 данных
            def clean_base64_data(match):
                base64_data = match.group(1)
                # Убираем все невалидные символы из base64
                cleaned_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', base64_data)
                # Убираем лишние = в конце
                cleaned_base64 = re.sub(r'=+$', '', cleaned_base64)
                # Добавляем правильное количество = для выравнивания
                remainder = len(cleaned_base64) % 4
                if remainder == 2:
                    cleaned_base64 += '=='
                elif remainder == 3:
                    cleaned_base64 += '='
                return f'data:image/jpeg;base64,{cleaned_base64}'
            
            # Очищаем все base64 данные
            pattern = r'data:image/[^;]+;base64,([^"\\'>\\s]+)'
            cleaned_svg = re.sub(pattern, clean_base64_data, cleaned_svg)
            
            # 4. Исправляем image теги
            def fix_image_tag(match):
                tag_content = match.group(1)
                if tag_content.endswith('/'):
                    return match.group(0)
                return f'<image{tag_content}/>'
            
            cleaned_svg = re.sub(r'<image([^>]*?)>', fix_image_tag, cleaned_svg)
            
            # 5. Исправляем use теги
            def fix_use_tag(match):
                tag_content = match.group(1)
                if tag_content.endswith('/'):
                    return match.group(0)
                return f'<use{tag_content}/>'
            
            cleaned_svg = re.sub(r'<use([^>]*?)>', fix_use_tag, cleaned_svg)
            
            # 6. Убираем лишние пробелы
            cleaned_svg = re.sub(r'\\s+', ' ', cleaned_svg)
            
            print(f"🧹 Ультимативная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    # Заменяем код
    if old_cleaning in content:
        content = content.replace(old_cleaning, new_cleaning)
        print("✅ Умная очистка заменена на ультимативную с base64!")
    else:
        print("⚠️ Не найден код умной очистки")
        return False
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с ультимативной очисткой base64")
    return True

def test_base64_cleaning():
    """Тестируем очистку base64 на реальном файле"""
    
    print("🧪 Тестирую очистку base64 на debug_improved_cleaned.svg...")
    
    with open('debug_improved_cleaned.svg', 'r') as f:
        svg_content = f.read()
    
    print(f"📊 Размер до очистки: {len(svg_content)} символов")
    
    # Применяем очистку base64
    cleaned = clean_base64_in_svg(svg_content)
    
    print(f"📊 Размер после очистки: {len(cleaned)} символов")
    
    # Сохраняем результат
    with open('debug_base64_cleaned.svg', 'w') as f:
        f.write(cleaned)
    
    print("💾 Сохранен файл: debug_base64_cleaned.svg")
    
    return True

if __name__ == "__main__":
    print("🧹 ИСПРАВЛЕНИЕ BASE64 ДАННЫХ В SVG")
    print("=" * 50)
    
    # Тест очистки base64
    success = test_base64_cleaning()
    
    if success:
        print("\n✅ Base64 очистка работает!")
        print("📝 Обновляю app.py...")
        update_app_with_base64_cleaning()
    else:
        print("\n❌ Base64 очистка не работает")