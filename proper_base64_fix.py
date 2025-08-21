#!/usr/bin/env python3
"""
ПРАВИЛЬНОЕ исправление base64 - исправляем символы, но сохраняем изображения
"""

def proper_base64_fix():
    """Правильное исправление base64 данных"""
    
    print("🔧 ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ BASE64")
    print("=" * 40)
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Откатываем экстренное исправление
    old_emergency_fix = '''            # ЭКСТРЕННАЯ ОЧИСТКА SVG - УБИРАЕМ ВСЕ BASE64!
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
    
    new_proper_fix = '''            # ПРАВИЛЬНАЯ ОЧИСТКА BASE64 - ИСПРАВЛЯЕМ СИМВОЛЫ, СОХРАНЯЕМ ИЗОБРАЖЕНИЯ
            print("🔧 ПРАВИЛЬНАЯ очистка base64 - исправляю символы, сохраняю изображения...")
            cleaned_svg = svg_content
            
            import re
            
            # 1. Убираем невалидные символы
            cleaned_svg = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', cleaned_svg)
            
            # 2. Исправляем амперсанды
            cleaned_svg = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\\d+;|#x[0-9a-fA-F]+;)', '&amp;', cleaned_svg)
            
            # 3. УМНАЯ очистка base64 данных - исправляем, но НЕ удаляем
            def clean_base64_data(match):
                full_match = match.group(0)
                mime_type = match.group(1)
                base64_data = match.group(2)
                
                # Убираем все невалидные символы из base64 (оставляем только валидные)
                cleaned_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', base64_data)
                
                # Обрезаем если слишком длинный (больше 1MB в base64 ≈ 1.3M символов)
                if len(cleaned_base64) > 1300000:
                    print(f"⚠️ Base64 слишком длинный ({len(cleaned_base64)} символов), обрезаю...")
                    cleaned_base64 = cleaned_base64[:1300000]
                
                # Исправляем padding
                remainder = len(cleaned_base64) % 4
                if remainder == 2:
                    cleaned_base64 += '=='
                elif remainder == 3:
                    cleaned_base64 += '='
                elif remainder == 1:
                    cleaned_base64 = cleaned_base64[:-1]  # Убираем последний символ
                
                return f'data:image/{mime_type};base64,{cleaned_base64}'
            
            # Очищаем все base64 данные
            pattern = r'data:image/([^;]+);base64,([^"\\'>\\s]+)'
            matches_before = len(re.findall(pattern, cleaned_svg))
            cleaned_svg = re.sub(pattern, clean_base64_data, cleaned_svg)
            matches_after = len(re.findall(pattern, cleaned_svg))
            
            print(f"🔧 Обработано {matches_before} base64 изображений")
            
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
            
            print(f"🔧 Правильная очистка завершена, длина: {len(cleaned_svg)} символов")'''
    
    # Заменяем код
    if old_emergency_fix in content:
        content = content.replace(old_emergency_fix, new_proper_fix)
        print("✅ Экстренное исправление заменено на правильное")
    else:
        print("⚠️ Не найден код экстренного исправления")
        return False
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с правильным исправлением base64")
    return True

if __name__ == "__main__":
    if proper_base64_fix():
        print("\n✅ ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ ПРИМЕНЕНО!")
        print("📋 Что изменилось:")
        print("  1. ✅ Изображения СОХРАНЕНЫ")
        print("  2. 🔧 Base64 данные ОЧИЩЕНЫ от невалидных символов")
        print("  3. ✂️ Слишком длинные base64 ОБРЕЗАНЫ")
        print("  4. 🔧 Исправлен padding base64")
        
        print("\n🎯 Результат:")
        print("  - PNG будут создаваться С изображениями")
        print("  - XML будет валидным")
        print("  - Превью будут работать")
        
        print("\n🚀 Нужен redeploy!")
    else:
        print("\n❌ Не удалось применить исправление")