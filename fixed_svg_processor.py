# Исправленная версия API без дублирования и с сохранением шрифтов

import re

def process_svg_font_perfect_fixed(svg_content, replacements):
    """
    ИСПРАВЛЕННАЯ функция обработки SVG:
    1. БЕЗ изменения шрифтов
    2. БЕЗ дублирования полей
    3. Правильная обработка изображений
    """
    print("🎨 ЗАПУСК ИСПРАВЛЕННОЙ ОБРАБОТКИ SVG")
    
    processed_svg = svg_content
    replaced_fields = set()  # Отслеживаем замененные поля
    
    for dyno_field, replacement in replacements.items():
        if dyno_field in replaced_fields:
            print(f"⚠️ Поле {dyno_field} уже заменено, пропускаем")
            continue
            
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Безопасное экранирование
        safe_replacement = safe_escape_for_svg(str(replacement))
        
        if 'image' in dyno_field.lower() or 'headshot' in dyno_field.lower() or 'logo' in dyno_field.lower():
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ
            print(f"🖼️ Обрабатываю изображение: {dyno_field}")
            
            # Экранируем & символы в URL для XML
            safe_url = str(replacement).replace('&', '&amp;')
            
            # Определяем правильный preserveAspectRatio для типа изображения
            if 'propertyimage' in dyno_field.lower():
                aspect_ratio = 'xMidYMid slice'  # Cover эффект для недвижимости
            elif 'logo' in dyno_field.lower():
                aspect_ratio = 'xMidYMid meet'   # Contain эффект для логотипа
            elif 'headshot' in dyno_field.lower() or 'agent' in dyno_field.lower():
                aspect_ratio = 'xMidYMid meet'   # НЕ обрезаем лица
            else:
                aspect_ratio = 'xMidYMid meet'   # По умолчанию contain
            
            # Ищем и заменяем изображение ТОЛЬКО ОДИН РАЗ
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            if match:
                pattern_id = match.group(1)
                image_id = pattern_id.replace("pattern", "image")
                
                # Заменяем ТОЛЬКО соответствующий image элемент
                image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                def replace_specific_image(img_match):
                    result = img_match.group(0)
                    result = re.sub(r'href="[^"]*"', f'href="{safe_url}"', result)
                    result = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', result)
                    result = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', result)
                    
                    if 'preserveAspectRatio=' not in result:
                        result = result.replace('/>', f' preserveAspectRatio="{aspect_ratio}"/>')
                    
                    return result
                
                processed_svg = re.sub(image_pattern, replace_specific_image, processed_svg, count=1)
                print(f"   ✅ Заменено изображение {image_id}")
            else:
                print(f"   ⚠️ Элемент изображения {dyno_field} не найден")
        
        else:
            # ОБРАБОТКА ТЕКСТА - заменяем ТОЛЬКО ОДИН РАЗ
            print(f"📝 Обрабатываю текст: {dyno_field}")
            
            # Паттерны для замены текста
            patterns = [
                f'>{re.escape(dyno_field)}<',           # >dyno.field<
                f'{{{{\\s*{re.escape(dyno_field)}\\s*}}}}',  # {{dyno.field}}
                f'{{\\s*{re.escape(dyno_field)}\\s*}}',      # {dyno.field}
            ]
            
            replaced = False
            for pattern in patterns:
                if re.search(pattern, processed_svg):
                    if pattern.startswith('>'):
                        # Замена между тегами
                        processed_svg = re.sub(pattern, f'>{safe_replacement}<', processed_svg, count=1)
                    else:
                        # Замена шаблонных переменных
                        processed_svg = re.sub(pattern, safe_replacement, processed_svg, count=1)
                    
                    print(f"   ✅ Заменен текст по паттерну: {pattern}")
                    replaced = True
                    break
            
            if not replaced:
                print(f"   ⚠️ Текстовое поле {dyno_field} не найдено")
        
        # Отмечаем поле как замененное
        replaced_fields.add(dyno_field)
    
    # НЕ МЕНЯЕМ ШРИФТЫ ВООБЩЕ!
    print("✅ Сохраняем оригинальные шрифты шаблона")
    
    print("🎉 ИСПРАВЛЕННАЯ обработка SVG завершена!")
    return processed_svg

def safe_escape_for_svg(text):
    """
    Безопасное экранирование для SVG
    """
    if not text:
        return text
    
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

