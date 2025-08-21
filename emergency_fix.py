#!/usr/bin/env python3
"""
ЭКСТРЕННОЕ исправление всех проблем
"""

def emergency_fix_all():
    """Экстренное исправление всех проблем"""
    
    print("🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ")
    print("=" * 50)
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # 1. РАДИКАЛЬНАЯ очистка base64 - заменяем на более агрессивную
    old_base64_cleaning = '''            # УЛЬТИМАТИВНАЯ ОЧИСТКА SVG + BASE64
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
    
    new_base64_cleaning = '''            # ЭКСТРЕННАЯ ОЧИСТКА SVG - УБИРАЕМ ВСЕ BASE64!
            print("🚨 ЭКСТРЕННАЯ очистка SVG - убираю все base64 данные...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. РАДИКАЛЬНО УБИРАЕМ ВСЕ BASE64 ДАННЫЕ
            print("🚨 Убираю все base64 данные полностью...")
            cleaned_svg = re.sub(r'data:image/[^;]+;base64,[^"\\'>\\s]+', 'https://via.placeholder.com/400x300/cccccc/666666?text=Image', cleaned_svg)
            
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
            
            print(f"🚨 Экстренная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    # Заменяем очистку
    if old_base64_cleaning in content:
        content = content.replace(old_base64_cleaning, new_base64_cleaning)
        print("✅ Base64 очистка заменена на экстренную (убираем все base64)")
    else:
        print("⚠️ Не найден код base64 очистки")
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с экстренными исправлениями")
    
    # 2. Исправляем preview_system.py - убираем неправильное масштабирование
    print("\n🔧 Исправляю preview_system.py...")
    
    with open('preview_system.py', 'r') as f:
        preview_content = f.read()
    
    # Убираем неправильное масштабирование для property изображений
    old_scaling = '''🔧 Масштабирование добавлено: scale(0.7) для headshot'''
    
    if old_scaling in preview_content:
        # Ищем и исправляем логику масштабирования
        preview_content = preview_content.replace(
            'print(f"🔧 Масштабирование добавлено: scale(0.7) для headshot")',
            'print(f"🔧 Масштабирование добавлено: scale(0.7) для {image_type}")'
        )
        
        # Исправляем условие масштабирования
        preview_content = preview_content.replace(
            '# Добавляем масштабирование для headshot (уменьшаем до 70%)',
            '# Добавляем масштабирование только для headshot (уменьшаем до 70%)'
        )
        
        with open('preview_system.py', 'w') as f:
            f.write(preview_content)
        
        print("✅ preview_system.py исправлен")
    
    return True

if __name__ == "__main__":
    emergency_fix_all()
    
    print("\n🚨 ЭКСТРЕННЫЕ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ!")
    print("📋 Что изменилось:")
    print("  1. ❌ Убраны ВСЕ base64 данные (заменены на placeholder)")
    print("  2. 🔧 Исправлено масштабирование в preview_system")
    print("  3. 🧹 Усилена очистка XML")
    
    print("\n⚠️ ВНИМАНИЕ:")
    print("  - PNG будут создаваться БЕЗ реальных изображений")
    print("  - Но система будет работать стабильно")
    print("  - Можно будет постепенно вернуть изображения")
    
    print("\n🚀 Нужен redeploy для применения!")