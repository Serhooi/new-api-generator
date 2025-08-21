#!/usr/bin/env python3
"""
УМНАЯ очистка SVG - исправляем теги, но НЕ удаляем их
"""

import re

def smart_svg_cleaning(svg_content):
    """
    УМНАЯ очистка SVG - исправляем проблемы, но сохраняем изображения
    """
    print("🧠 УМНАЯ очистка SVG - исправляю теги, но сохраняю изображения...")
    
    cleaned = svg_content
    
    # 1. Убираем невалидные символы
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    # 2. Исправляем амперсанды
    cleaned = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned)
    
    # 3. УМНО исправляем image теги - НЕ удаляем, а закрываем
    # Ищем незакрытые image теги и закрываем их
    def fix_image_tag(match):
        tag_content = match.group(1)
        # Если тег уже самозакрывающийся, оставляем как есть
        if tag_content.endswith('/'):
            return match.group(0)
        # Иначе делаем самозакрывающимся
        return f'<image{tag_content}/>'
    
    cleaned = re.sub(r'<image([^>]*?)>', fix_image_tag, cleaned)
    
    # 4. УМНО исправляем use теги
    def fix_use_tag(match):
        tag_content = match.group(1)
        if tag_content.endswith('/'):
            return match.group(0)
        return f'<use{tag_content}/>'
    
    cleaned = re.sub(r'<use([^>]*?)>', fix_use_tag, cleaned)
    
    # 5. Исправляем другие самозакрывающиеся теги
    self_closing_tags = ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop']
    
    for tag in self_closing_tags:
        def fix_tag(match):
            tag_content = match.group(1)
            if tag_content.endswith('/'):
                return match.group(0)
            return f'<{tag}{tag_content}/>'
        
        cleaned = re.sub(f'<{tag}([^>]*?)>', fix_tag, cleaned)
    
    # 6. Убираем лишние пробелы
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    print(f"🧠 Умная очистка завершена: {len(svg_content)} → {len(cleaned)} символов")
    
    return cleaned

def update_app_with_smart_cleaning():
    """Обновляем app.py с умной очисткой"""
    
    print("📝 Читаю app.py...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Находим и заменяем радикальную очистку на умную
    old_cleaning = '''            # РАДИКАЛЬНАЯ ОЧИСТКА SVG - УБИРАЕМ ВСЕ ПРОБЛЕМНЫЕ ТЕГИ
            print("🔥 РАДИКАЛЬНАЯ очистка SVG - убираю все проблемные теги...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. РАДИКАЛЬНО - УБИРАЕМ ВСЕ IMAGE ТЕГИ ПОЛНОСТЬЮ
            print("🚨 Убираю все image теги полностью...")
            cleaned_svg = re.sub(r'<image[^>]*/?>', '', cleaned_svg)
            
            # 4. УБИРАЕМ ВСЕ USE ТЕГИ ПОЛНОСТЬЮ
            print("🚨 Убираю все use теги полностью...")
            cleaned_svg = re.sub(r'<use[^>]*/?>', '', cleaned_svg)
            
            # 5. Исправляем оставшиеся самозакрывающиеся теги
            self_closing_tags = ['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path', 'stop']
            
            for tag in self_closing_tags:
                cleaned_svg = re.sub(f'<{tag}([^>]*?)(?<!/)>', f'<{tag}\\\\1/>', cleaned_svg)
            
            # 6. Убираем лишние пробелы
            cleaned_svg = re.sub(r'\\s+', ' ', cleaned_svg)
            
            print(f"🔥 Радикальная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    new_cleaning = '''            # УМНАЯ ОЧИСТКА SVG - ИСПРАВЛЯЕМ ТЕГИ, НО СОХРАНЯЕМ ИЗОБРАЖЕНИЯ
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
    
    # Заменяем код
    if old_cleaning in content:
        content = content.replace(old_cleaning, new_cleaning)
        print("✅ Радикальная очистка заменена на умную!")
    else:
        print("⚠️ Не найден код радикальной очистки")
        return False
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с умной очисткой")
    return True

def test_smart_cleaning():
    """Тестируем умную очистку на локальных файлах"""
    
    print("🧪 Тестирую умную очистку на main.svg...")
    
    # Читаем оригинальный main.svg
    with open('main.svg', 'r') as f:
        svg_content = f.read()
    
    print(f"📊 Оригинальный размер: {len(svg_content)} символов")
    
    # Анализируем теги до очистки
    image_tags_before = len(re.findall(r'<image[^>]*>', svg_content))
    use_tags_before = len(re.findall(r'<use[^>]*>', svg_content))
    
    print(f"🔍 До очистки: {image_tags_before} image тегов, {use_tags_before} use тегов")
    
    # Применяем умную очистку
    cleaned = smart_svg_cleaning(svg_content)
    
    # Анализируем теги после очистки
    image_tags_after = len(re.findall(r'<image[^>]*>', cleaned))
    use_tags_after = len(re.findall(r'<use[^>]*>', cleaned))
    
    print(f"🔍 После очистки: {image_tags_after} image тегов, {use_tags_after} use тегов")
    
    # Сохраняем результат
    with open('smart_cleaned_main.svg', 'w') as f:
        f.write(cleaned)
    
    print("💾 Умно очищенный SVG сохранен: smart_cleaned_main.svg")
    
    # Проверяем что изображения остались
    if image_tags_after > 0:
        print("✅ Изображения сохранены!")
    else:
        print("❌ Изображения потеряны!")
    
    return image_tags_after > 0

if __name__ == "__main__":
    print("🧠 УМНАЯ ОЧИСТКА SVG")
    print("=" * 50)
    
    # Тест умной очистки
    success = test_smart_cleaning()
    
    if success:
        print("\n✅ Умная очистка работает - изображения сохранены!")
        print("📝 Обновляю app.py...")
        update_app_with_smart_cleaning()
    else:
        print("\n❌ Умная очистка не работает")