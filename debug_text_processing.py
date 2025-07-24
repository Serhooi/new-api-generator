#!/usr/bin/env python3
"""
ДИАГНОСТИКА ПРОБЛЕМ С ОБРАБОТКОЙ ТЕКСТА В SVG
==============================================

Этот скрипт поможет найти где "пропадают" слова при обработке SVG
"""

import re

def safe_escape_for_svg(text):
    """Безопасное экранирование для SVG"""
    if not text:
        return text
    
    text = str(text)
    print(f"🔍 Исходный текст: '{text}'")
    
    text = text.replace('&', '&amp;')  # ВАЖНО: & должен быть первым!
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    print(f"🔒 После экранирования: '{text}'")
    return text

def test_tspan_replacement():
    """Тестирование замены содержимого tspan"""
    print("🧪 ТЕСТ: Замена содержимого tspan")
    print("=" * 50)
    
    # Пример SVG с tspan
    test_svg = '''<text id="dyno.agentName" x="100" y="50">
        <tspan x="100" y="50">dyno.agentName</tspan>
    </text>'''
    
    replacement_text = "John Smith & Associates"
    dyno_field = "dyno.agentName"
    
    print(f"📝 Исходный SVG:\n{test_svg}")
    print(f"📝 Замена: {dyno_field} → {replacement_text}")
    
    # Применяем экранирование
    safe_replacement = safe_escape_for_svg(replacement_text)
    
    # Ищем элемент
    element_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
    match = re.search(element_pattern, test_svg, re.DOTALL)
    
    if match:
        element_content = match.group(1)
        print(f"🎯 Найден элемент с содержимым: '{element_content.strip()}'")
        
        # Ищем tspan
        tspan_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
        tspan_match = re.search(tspan_pattern, element_content)
        
        if tspan_match:
            opening_tag = tspan_match.group(1)
            old_content = tspan_match.group(2)
            closing_tag = tspan_match.group(3)
            
            print(f"📋 Найден tspan:")
            print(f"   Opening: {opening_tag}")
            print(f"   Content: '{old_content}'")
            print(f"   Closing: {closing_tag}")
            
            # Заменяем содержимое
            new_tspan = opening_tag + safe_replacement + closing_tag
            new_element_content = element_content.replace(tspan_match.group(0), new_tspan)
            new_svg = test_svg.replace(element_content, new_element_content)
            
            print(f"✅ Результат:\n{new_svg}")
        else:
            print("❌ tspan не найден")
    else:
        print("❌ Элемент не найден")

def test_address_wrapping():
    """Тестирование переноса адресов"""
    print("\n🏠 ТЕСТ: Перенос адресов")
    print("=" * 50)
    
    def wrap_address_text(address_text, max_length=35):
        """Автоматический перенос адреса на две строки"""
        print(f"📍 Обрабатываю адрес: '{address_text}' (длина: {len(address_text)})")
        
        if not address_text or len(address_text) <= max_length:
            print("✅ Адрес короткий, перенос не нужен")
            return address_text, ""
        
        # Пытаемся найти хорошее место для разрыва
        words = address_text.split()
        print(f"🔤 Слова: {words}")
        
        if len(words) <= 1:
            print("⚠️ Только одно слово, перенос невозможен")
            return address_text, ""
        
        # Ищем оптимальное место для разрыва
        best_break = len(words) // 2
        print(f"🎯 Начальная точка разрыва: {best_break}")
        
        # Пытаемся найти запятую для естественного разрыва
        for i, word in enumerate(words):
            if ',' in word and i > 0 and i < len(words) - 1:
                first_part = ' '.join(words[:i+1])
                print(f"🔍 Найдена запятая в слове '{word}' (позиция {i})")
                print(f"    Первая часть: '{first_part}' (длина: {len(first_part)})")
                
                if len(first_part) >= 15:  # Минимум 15 символов в первой строке
                    best_break = i + 1
                    print(f"✅ Используем разрыв по запятой: {best_break}")
                    break
        
        # Если не нашли запятую, ищем другие разделители
        if best_break == len(words) // 2:
            print("🔍 Запятая не найдена, ищем оптимальный разрыв...")
            for i, word in enumerate(words):
                if i > 0 and i < len(words) - 1:
                    first_part = ' '.join(words[:i+1])
                    if 20 <= len(first_part) <= max_length:
                        best_break = i + 1
                        print(f"✅ Найден оптимальный разрыв: {best_break}")
                        break
        
        first_line = ' '.join(words[:best_break])
        second_line = ' '.join(words[best_break:])
        
        print(f"📝 Первая строка: '{first_line}' (длина: {len(first_line)})")
        print(f"📝 Вторая строка: '{second_line}' (длина: {len(second_line)})")
        
        # Если вторая строка слишком длинная, возвращаем оригинал
        if len(second_line) > max_length:
            print("❌ Вторая строка слишком длинная, возвращаем оригинал")
            return address_text, ""
        
        return first_line, second_line
    
    # Тестовые адреса
    test_addresses = [
        "123 Main Street, Beverly Hills, CA 90210",
        "456 Very Long Property Address That Should Be Wrapped, Los Angeles, California 90028",
        "789 Short St, NYC 10001",
        "1000 Extremely Long Property Address With Many Words That Definitely Needs Wrapping, San Francisco, California 94102"
    ]
    
    for addr in test_addresses:
        print(f"\n🏠 Тестирую адрес: {addr}")
        first, second = wrap_address_text(addr)
        if second:
            print(f"✅ Разбито на:")
            print(f"   1: {first}")
            print(f"   2: {second}")
        else:
            print(f"✅ Оставлен как есть: {first}")

def test_regex_patterns():
    """Тестирование регулярных выражений"""
    print("\n🔍 ТЕСТ: Регулярные выражения")
    print("=" * 50)
    
    test_svg = '''<text id="dyno.agentName" x="100" y="50" font-family="Inter">
        <tspan x="100" y="50">dyno.agentName</tspan>
    </text>
    <text id="dyno.propertyAddress" x="100" y="100">
        <tspan x="100" y="100">dyno.propertyAddress</tspan>
    </text>'''
    
    # Тестируем разные паттерны
    patterns = [
        r'<text[^>]*id="dyno\.agentName"[^>]*>(.*?)</text>',
        r'<text[^>]*id="dyno\.propertyAddress"[^>]*>(.*?)</text>',
        r'(<tspan[^>]*>)([^<]*)(</tspan>)'
    ]
    
    for i, pattern in enumerate(patterns):
        print(f"\n🔍 Паттерн {i+1}: {pattern}")
        matches = re.findall(pattern, test_svg, re.DOTALL)
        print(f"   Найдено совпадений: {len(matches)}")
        for j, match in enumerate(matches):
            print(f"   Совпадение {j+1}: {match}")

def main():
    """Основная функция диагностики"""
    print("🔧 ДИАГНОСТИКА ОБРАБОТКИ ТЕКСТА В SVG")
    print("=" * 60)
    
    test_tspan_replacement()
    test_address_wrapping()
    test_regex_patterns()
    
    print("\n🎉 ДИАГНОСТИКА ЗАВЕРШЕНА")

if __name__ == "__main__":
    main()