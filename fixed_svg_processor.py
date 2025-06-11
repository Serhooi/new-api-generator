# Исправленная логика замены с переносом строк

import re

def process_svg_with_line_breaks(svg_content, replacements):
    """
    ИСПРАВЛЕННАЯ функция обработки SVG:
    1. Правильная замена без дублирования
    2. Автоматический перенос длинных адресов
    3. Сохранение оригинальных шрифтов
    """
    print("🎨 ЗАПУСК ИСПРАВЛЕННОЙ ОБРАБОТКИ SVG С ПЕРЕНОСОМ СТРОК")
    
    processed_svg = svg_content
    
    for dyno_field, replacement in replacements.items():
        print(f"\n🔄 Обрабатываю поле: {dyno_field} = {replacement}")
        
        # Безопасное экранирование
        safe_replacement = safe_escape_for_svg(str(replacement))
        
        # Специальная обработка для адреса - добавляем перенос строки
        if 'address' in dyno_field.lower():
            # Разбиваем длинный адрес на строки
            address_parts = str(replacement).split(', ')
            if len(address_parts) >= 3:
                # Первая строка: номер дома + улица
                line1 = address_parts[0]
                # Вторая строка: город + штат + индекс
                line2 = ', '.join(address_parts[1:])
                
                # Создаем многострочный текст для SVG
                safe_replacement = f'''<tspan x="0" dy="0">{safe_escape_for_svg(line1)}</tspan>
                                     <tspan x="0" dy="1.2em">{safe_escape_for_svg(line2)}</tspan>'''
                print(f"   📍 Адрес разбит на строки: {line1} | {line2}")
            else:
                safe_replacement = safe_escape_for_svg(str(replacement))
        
        if 'image' in dyno_field.lower() or 'headshot' in dyno_field.lower() or 'logo' in dyno_field.lower():
            # ОБРАБОТКА ИЗОБРАЖЕНИЙ (без изменений)
            print(f"🖼️ Обрабатываю изображение: {dyno_field}")
            
            safe_url = str(replacement).replace('&', '&amp;')
            
            if 'propertyimage' in dyno_field.lower():
                aspect_ratio = 'xMidYMid slice'
            elif 'logo' in dyno_field.lower():
                aspect_ratio = 'xMidYMid meet'
            elif 'headshot' in dyno_field.lower() or 'agent' in dyno_field.lower():
                aspect_ratio = 'xMidYMid meet'
            else:
                aspect_ratio = 'xMidYMid meet'
            
            element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
            match = re.search(element_pattern, processed_svg)
            
            if match:
                pattern_id = match.group(1)
                image_id = pattern_id.replace("pattern", "image")
                
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
            # ИСПРАВЛЕННАЯ ОБРАБОТКА ТЕКСТА
            print(f"📝 Обрабатываю текст: {dyno_field}")
            
            # Ищем ТОЧНОЕ совпадение dyno поля в тексте элементов
            # Паттерн для поиска текстового элемента с dyno полем
            text_element_pattern = f'<text[^>]*>([^<]*{re.escape(dyno_field)}[^<]*)</text>'
            matches = list(re.finditer(text_element_pattern, processed_svg))
            
            if matches:
                # Заменяем ТОЛЬКО ПЕРВОЕ совпадение
                match = matches[0]
                old_text = match.group(1)
                
                if 'address' in dyno_field.lower():
                    # Для адреса используем tspan элементы
                    new_text = safe_replacement
                else:
                    # Для обычного текста - простая замена
                    new_text = old_text.replace(dyno_field, safe_replacement)
                
                # Заменяем только этот конкретный элемент
                old_element = match.group(0)
                new_element = old_element.replace(old_text, new_text)
                
                processed_svg = processed_svg.replace(old_element, new_element, 1)
                print(f"   ✅ Заменен текст: {old_text} → {new_text[:50]}...")
            
            else:
                # Fallback - ищем по старым паттернам
                patterns = [
                    f'>{re.escape(dyno_field)}<',
                    f'{{{{\\s*{re.escape(dyno_field)}\\s*}}}}',
                    f'{{\\s*{re.escape(dyno_field)}\\s*}}',
                ]
                
                replaced = False
                for pattern in patterns:
                    if re.search(pattern, processed_svg):
                        if pattern.startswith('>'):
                            processed_svg = re.sub(pattern, f'>{safe_replacement}<', processed_svg, count=1)
                        else:
                            processed_svg = re.sub(pattern, safe_replacement, processed_svg, count=1)
                        
                        print(f"   ✅ Заменен текст по fallback паттерну: {pattern}")
                        replaced = True
                        break
                
                if not replaced:
                    print(f"   ⚠️ Текстовое поле {dyno_field} не найдено")
    
    print("✅ Сохраняем оригинальные шрифты шаблона")
    print("🎉 ИСПРАВЛЕННАЯ обработка SVG завершена!")
    return processed_svg

def safe_escape_for_svg(text):
    """Безопасное экранирование для SVG"""
    if not text:
        return text
    
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    return text

