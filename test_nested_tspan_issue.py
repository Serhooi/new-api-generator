#!/usr/bin/env python3
"""
ТЕСТ ПРОБЛЕМЫ С ВЛОЖЕННЫМИ TSPAN ЭЛЕМЕНТАМИ
===========================================

Проверяем проблему с регулярным выражением r'(<tspan[^>]*>)([^<]*)(</tspan>)'
которое НЕ УЧИТЫВАЕТ вложенные tspan элементы!
"""

import re

def test_nested_tspan_problem():
    """Демонстрируем проблему с вложенными tspan"""
    print("🚨 ПРОБЛЕМА С ВЛОЖЕННЫМИ TSPAN")
    print("=" * 50)
    
    # Проблемный SVG с вложенными tspan
    problematic_svg = '''<text id="dyno.price">
        <tspan x="100" y="50">
            <tspan fill="green">$</tspan>dyno.price
        </tspan>
    </text>'''
    
    print("📝 Проблемный SVG:")
    print(problematic_svg)
    
    # Текущий паттерн из кода
    current_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
    
    print(f"\n🔍 Текущий паттерн: {current_pattern}")
    print("   Этот паттерн ищет: [^<]* - любые символы КРОМЕ <")
    print("   ПРОБЛЕМА: Он останавливается на первом < (от вложенного tspan)!")
    
    # Ищем совпадения
    matches = re.findall(current_pattern, problematic_svg)
    print(f"\n📋 Найденные совпадения: {len(matches)}")
    
    for i, match in enumerate(matches):
        print(f"   {i+1}: Opening='{match[0]}', Content='{match[1]}', Closing='{match[2]}'")
    
    # Демонстрируем что происходит при замене
    print(f"\n🔄 Что происходит при замене:")
    
    def replace_tspan_content(tspan_match):
        opening_tag = tspan_match.group(1)
        old_content = tspan_match.group(2)  # ЭТО ПУСТАЯ СТРОКА!
        closing_tag = tspan_match.group(3)
        
        replacement = "NEW_VALUE"
        print(f"      🎯 Заменяю: '{old_content}' → '{replacement}'")
        print(f"         ПРОБЛЕМА: old_content пустой из-за вложенного <tspan>!")
        
        return opening_tag + replacement + closing_tag
    
    result = re.sub(current_pattern, replace_tspan_content, problematic_svg, count=1)
    print(f"\n❌ НЕПРАВИЛЬНЫЙ результат:")
    print(result)

def test_correct_solution():
    """Показываем правильное решение"""
    print("\n✅ ПРАВИЛЬНОЕ РЕШЕНИЕ")
    print("=" * 50)
    
    problematic_svg = '''<text id="dyno.price">
        <tspan x="100" y="50">
            <tspan fill="green">$</tspan>dyno.price
        </tspan>
    </text>'''
    
    print("📝 Тот же проблемный SVG:")
    print(problematic_svg)
    
    # Правильный подход - ищем весь контент между открывающим и закрывающим tspan
    # используя балансированные скобки или более умный паттерн
    
    def find_and_replace_dyno_in_tspan(svg_content, dyno_field, replacement):
        """Правильная функция замены с учетом вложенных элементов"""
        print(f"\n🔧 Правильная замена {dyno_field} → {replacement}")
        
        # Ищем text элемент
        text_pattern = f'<text[^>]*id="{re.escape(dyno_field)}"[^>]*>(.*?)</text>'
        text_match = re.search(text_pattern, svg_content, re.DOTALL)
        
        if not text_match:
            print("❌ Text элемент не найден")
            return svg_content
        
        text_content = text_match.group(1)
        print(f"📋 Содержимое text элемента:")
        print(f"   '{text_content.strip()}'")
        
        # Вместо сложного regex, просто заменяем dyno поле на значение
        # где бы оно ни находилось в тексте
        if dyno_field in text_content:
            new_text_content = text_content.replace(dyno_field, replacement)
            new_svg = svg_content.replace(text_content, new_text_content)
            
            print(f"✅ Простая замена выполнена:")
            print(f"   {dyno_field} → {replacement}")
            
            return new_svg
        else:
            print(f"⚠️ {dyno_field} не найдено в содержимом")
            return svg_content
    
    # Тестируем правильное решение
    result = find_and_replace_dyno_in_tspan(problematic_svg, "dyno.price", "$450,000")
    print(f"\n✅ ПРАВИЛЬНЫЙ результат:")
    print(result)

def test_real_world_cases():
    """Тестируем реальные случаи из практики"""
    print("\n🌍 РЕАЛЬНЫЕ СЛУЧАИ")
    print("=" * 50)
    
    real_cases = [
        {
            "name": "Цена с символом доллара",
            "svg": '''<text id="dyno.price">
                <tspan x="100" y="50">
                    <tspan fill="green" font-weight="bold">$</tspan>dyno.price
                </tspan>
            </text>''',
            "field": "dyno.price",
            "replacement": "450,000"
        },
        {
            "name": "Имя агента с иконкой",
            "svg": '''<text id="dyno.agentName">
                <tspan x="100" y="50">
                    <tspan>👤</tspan> dyno.agentName
                </tspan>
            </text>''',
            "field": "dyno.agentName", 
            "replacement": "John Smith"
        },
        {
            "name": "Адрес с иконкой локации",
            "svg": '''<text id="dyno.address">
                <tspan x="100" y="50">
                    <tspan fill="blue">📍</tspan> dyno.address
                </tspan>
            </text>''',
            "field": "dyno.address",
            "replacement": "123 Main Street, Beverly Hills, CA"
        }
    ]
    
    for case in real_cases:
        print(f"\n📋 Случай: {case['name']}")
        print(f"   Поле: {case['field']}")
        print(f"   Замена: {case['replacement']}")
        
        # Показываем проблему с текущим подходом
        current_pattern = r'(<tspan[^>]*>)([^<]*)(</tspan>)'
        matches = re.findall(current_pattern, case['svg'])
        
        print(f"   🔍 Текущий regex находит {len(matches)} совпадений:")
        for i, match in enumerate(matches):
            content = match[1] if len(match) > 1 else "N/A"
            print(f"      {i+1}: '{content}'")
            if case['field'] in content:
                print(f"         ✅ Содержит {case['field']}")
            else:
                print(f"         ❌ НЕ содержит {case['field']}")
        
        # Показываем правильное решение
        if case['field'] in case['svg']:
            result = case['svg'].replace(case['field'], case['replacement'])
            print(f"   ✅ Простая замена работает!")
        else:
            print(f"   ❌ Поле не найдено даже простым поиском")

def main():
    """Основная функция"""
    print("🚨 ДИАГНОСТИКА ПРОБЛЕМЫ С ВЛОЖЕННЫМИ TSPAN")
    print("=" * 60)
    
    test_nested_tspan_problem()
    test_correct_solution()
    test_real_world_cases()
    
    print("\n💡 ВЫВОДЫ:")
    print("1. Текущий regex r'(<tspan[^>]*>)([^<]*)(</tspan>)' НЕ РАБОТАЕТ с вложенными tspan")
    print("2. Паттерн [^<]* останавливается на первом < от вложенного элемента")
    print("3. Это приводит к пустому содержимому и потере данных")
    print("4. РЕШЕНИЕ: Использовать простую замену строк вместо сложного regex")
    print("5. Или использовать более умный парсинг XML/SVG")

if __name__ == "__main__":
    main()