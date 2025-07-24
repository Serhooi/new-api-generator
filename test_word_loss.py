#!/usr/bin/env python3
"""
ТЕСТ НА ПОТЕРЮ СЛОВ ПРИ ОБРАБОТКЕ SVG
=====================================

Проверяем конкретные случаи где могут теряться слова
"""

import re

def test_problematic_cases():
    """Тестируем проблемные случаи"""
    print("🔍 ТЕСТ ПРОБЛЕМНЫХ СЛУЧАЕВ")
    print("=" * 50)
    
    # Случай 1: Слова с амперсандами
    test_cases = [
        {
            "name": "Амперсанд в названии",
            "input": "Smith & Associates Real Estate",
            "expected_issues": ["Амперсанд может экранироваться"]
        },
        {
            "name": "Кавычки в тексте", 
            "input": 'Beautiful "Dream Home" for Sale',
            "expected_issues": ["Кавычки могут экранироваться"]
        },
        {
            "name": "Специальные символы",
            "input": "Price: $450,000 <SOLD>",
            "expected_issues": ["< и > экранируются"]
        },
        {
            "name": "Длинный адрес",
            "input": "123 Very Long Street Name That Might Get Cut Off, Beverly Hills, CA 90210",
            "expected_issues": ["Может обрезаться при переносе"]
        },
        {
            "name": "Множественные пробелы",
            "input": "John    Smith     Real   Estate",
            "expected_issues": ["Множественные пробелы могут схлопываться"]
        }
    ]
    
    for case in test_cases:
        print(f"\n📝 Тест: {case['name']}")
        print(f"   Входные данные: '{case['input']}'")
        
        # Применяем экранирование
        escaped = safe_escape_for_svg(case['input'])
        print(f"   После экранирования: '{escaped}'")
        
        # Проверяем потерю данных
        if len(escaped) != len(case['input'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')):
            print("   ⚠️ ВОЗМОЖНАЯ ПРОБЛЕМА: Неожиданное изменение длины")
        
        print(f"   Ожидаемые проблемы: {case['expected_issues']}")

def safe_escape_for_svg(text):
    """Безопасное экранирование для SVG"""
    if not text:
        return text
    
    original_length = len(text)
    text = str(text)
    
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    
    print(f"      🔢 Длина: {original_length} → {len(text)}")
    return text

def test_tspan_content_extraction():
    """Тестируем извлечение содержимого tspan"""
    print("\n🎯 ТЕСТ ИЗВЛЕЧЕНИЯ СОДЕРЖИМОГО TSPAN")
    print("=" * 50)
    
    test_svgs = [
        {
            "name": "Простой tspan",
            "svg": '<text id="dyno.name"><tspan x="100" y="50">dyno.name</tspan></text>',
            "field": "dyno.name"
        },
        {
            "name": "Множественные tspan",
            "svg": '<text id="dyno.address"><tspan x="100" y="50">dyno.address</tspan><tspan x="100" y="70">Line 2</tspan></text>',
            "field": "dyno.address"
        },
        {
            "name": "Вложенные элементы",
            "svg": '<text id="dyno.price"><tspan x="100" y="50"><tspan>$</tspan>dyno.price</tspan></text>',
            "field": "dyno.price"
        },
        {
            "name": "С атрибутами",
            "svg": '<text id="dyno.agent" font-family="Inter"><tspan x="100" y="50" fill="black">dyno.agent</tspan></text>',
            "field": "dyno.agent"
        }
    ]
    
    for test in test_svgs:
        print(f"\n📋 Тест: {test['name']}")
        print(f"   SVG: {test['svg']}")
        print(f"   Поле: {test['field']}")
        
        # Ищем элемент
        element_pattern = f'<text[^>]*id="{re.escape(test["field"])}"[^>]*>(.*?)</text>'
        match = re.search(element_pattern, test['svg'], re.DOTALL)
        
        if match:
            element_content = match.group(1)
            print(f"   ✅ Найден элемент: '{element_content.strip()}'")
            
            # Ищем все tspan
            tspan_pattern = r'<tspan[^>]*>([^<]*)</tspan>'
            tspan_matches = re.findall(tspan_pattern, element_content)
            
            print(f"   📝 Найдено tspan элементов: {len(tspan_matches)}")
            for i, content in enumerate(tspan_matches):
                print(f"      {i+1}: '{content}'")
                
                # Проверяем, содержит ли dyno поле
                if test['field'] in content:
                    print(f"         🎯 Содержит dyno поле!")
        else:
            print("   ❌ Элемент не найден")

def test_replacement_logic():
    """Тестируем логику замены"""
    print("\n🔄 ТЕСТ ЛОГИКИ ЗАМЕНЫ")
    print("=" * 50)
    
    test_svg = '''<text id="dyno.agentName" x="100" y="50">
        <tspan x="100" y="50">dyno.agentName</tspan>
    </text>'''
    
    replacements = [
        "John Smith",
        "John Smith & Associates", 
        "John \"The Best\" Smith",
        "Smith & Associates <Premium>",
        "John    Smith    (Multiple Spaces)"
    ]
    
    for replacement in replacements:
        print(f"\n🔄 Замена на: '{replacement}'")
        
        # Применяем полную логику замены
        result_svg = test_svg
        safe_replacement = safe_escape_for_svg(replacement)
        
        # Ищем элемент
        element_pattern = r'<text[^>]*id="dyno\.agentName"[^>]*>(.*?)</text>'
        match = re.search(element_pattern, result_svg, re.DOTALL)
        
        if match:
            element_content = match.group(1)
            
            # Заменяем первый tspan
            tspan_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
            
            def replace_tspan_content(tspan_match):
                opening_tag = tspan_match.group(1)
                old_content = tspan_match.group(2)
                closing_tag = tspan_match.group(3)
                
                print(f"      🎯 Заменяю: '{old_content}' → '{safe_replacement}'")
                return opening_tag + safe_replacement + closing_tag
            
            new_content = re.sub(tspan_pattern, replace_tspan_content, element_content, count=1)
            result_svg = result_svg.replace(element_content, new_content)
            
            print(f"   ✅ Результат:")
            print(f"      {result_svg.strip()}")
        else:
            print("   ❌ Элемент не найден")

def test_address_splitting_edge_cases():
    """Тестируем крайние случаи разбиения адресов"""
    print("\n🏠 ТЕСТ КРАЙНИХ СЛУЧАЕВ АДРЕСОВ")
    print("=" * 50)
    
    edge_cases = [
        "123 Main St",  # Короткий адрес
        "A",  # Один символ
        "",  # Пустая строка
        "123 Main Street, Beverly Hills, CA 90210, USA, North America",  # Очень много частей
        "123-Main-Street-Without-Spaces",  # Без пробелов
        "123 Main Street,,,, Beverly Hills",  # Множественные запятые
        "123 Main Street Beverly Hills CA 90210",  # Без запятых
    ]
    
    def wrap_address_text(address_text, max_length=35):
        """Функция переноса адреса с диагностикой"""
        print(f"   📍 Обрабатываю: '{address_text}' (длина: {len(address_text)})")
        
        if not address_text:
            print("   ⚠️ Пустая строка")
            return "", ""
            
        if len(address_text) <= max_length:
            print("   ✅ Короткий адрес, перенос не нужен")
            return address_text, ""
        
        words = address_text.split()
        print(f"   🔤 Слов: {len(words)}")
        
        if len(words) <= 1:
            print("   ⚠️ Одно слово или меньше")
            return address_text, ""
        
        # Простая логика разбиения пополам
        mid = len(words) // 2
        first_line = ' '.join(words[:mid])
        second_line = ' '.join(words[mid:])
        
        print(f"   📝 Разбито: '{first_line}' | '{second_line}'")
        
        if len(second_line) > max_length:
            print("   ❌ Вторая строка слишком длинная")
            return address_text, ""
        
        return first_line, second_line
    
    for addr in edge_cases:
        print(f"\n🏠 Тест адреса: '{addr}'")
        first, second = wrap_address_text(addr)
        
        # Проверяем потерю данных
        combined = (first + " " + second).strip()
        original_words = set(addr.split())
        result_words = set(combined.split())
        
        if original_words != result_words:
            print("   ❌ ПОТЕРЯ ДАННЫХ!")
            print(f"      Потеряно: {original_words - result_words}")
            print(f"      Добавлено: {result_words - original_words}")
        else:
            print("   ✅ Данные сохранены")

def main():
    """Основная функция"""
    print("🔍 ТЕСТ НА ПОТЕРЮ СЛОВ ПРИ ОБРАБОТКЕ SVG")
    print("=" * 60)
    
    test_problematic_cases()
    test_tspan_content_extraction()
    test_replacement_logic()
    test_address_splitting_edge_cases()
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    main()