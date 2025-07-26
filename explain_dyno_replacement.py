#!/usr/bin/env python3
"""
ОБЪЯСНЕНИЕ ЗАМЕНЫ DYNO ПОЛЕЙ
===========================

Показывает точно как происходит замена dyno полей в SVG
"""

def explain_replacement_process():
    """Объясняет процесс замены dyno полей"""
    print("🔧 КАК РАБОТАЕТ ЗАМЕНА DYNO ПОЛЕЙ")
    print("=" * 50)
    
    print("""
📋 АЛГОРИТМ ЗАМЕНЫ:

1. 🔍 СИСТЕМА ИЩЕТ В SVG:
   - Элементы с id="dyno.fieldName" (ТОЧНОЕ совпадение!)
   - Например: <rect id="dyno.agentPhoto" ...>
   - Или: <text id="dyno.agentName" ...>

2. 🖼️ ДЛЯ ИЗОБРАЖЕНИЙ:
   Ищет: <rect id="dyno.agentPhoto" fill="url(#agent_pattern)">
   Находит: <pattern id="agent_pattern">
   Внутри pattern: <use xlink:href="#agent_image">
   Заменяет в: <image id="agent_image" href="OLD_URL">
   На: <image id="agent_image" href="NEW_URL">

3. 📝 ДЛЯ ТЕКСТА:
   Ищет: <text id="dyno.agentName">
   Внутри: <tspan>OLD_TEXT</tspan>
   Заменяет на: <tspan>NEW_TEXT</tspan>

⚠️ КРИТИЧЕСКИ ВАЖНО:
- Названия полей должны ТОЧНО совпадать!
- dyno.companyLogo ≠ dyno.logo ≠ dyno.companylogo
- Регистр букв имеет значение!
""")

def show_common_problems():
    """Показывает частые проблемы"""
    print("\n❌ ЧАСТЫЕ ПРОБЛЕМЫ:")
    print("=" * 30)
    
    problems = [
        {
            "problem": "Лого не заменяется",
            "cause": "В SVG поле называется dyno.logo, а отправляете dyno.companyLogo",
            "solution": "Проверить точное название в SVG или отправлять оба варианта"
        },
        {
            "problem": "Headshot съезжает",
            "cause": "Фиксированные transform в pattern элементе",
            "solution": "Исправления уже применены - убраны фиксированные смещения"
        },
        {
            "problem": "Property image не меняется", 
            "cause": "Поле может называться dyno.propertyimage (lowercase)",
            "solution": "Отправлять разные варианты названий"
        },
        {
            "problem": "Поле не определяется как изображение",
            "cause": "Отсутствует ключевое слово (image, photo, logo, headshot)",
            "solution": "Добавить ключевое слово в название или в код"
        }
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. ❌ {problem['problem']}")
        print(f"   🔍 Причина: {problem['cause']}")
        print(f"   ✅ Решение: {problem['solution']}")

def show_field_examples():
    """Показывает примеры полей"""
    print("\n📋 ПРИМЕРЫ DYNO ПОЛЕЙ:")
    print("=" * 30)
    
    examples = [
        {
            "category": "Текстовые поля",
            "fields": [
                "dyno.agentName",
                "dyno.propertyAddress", 
                "dyno.price",
                "dyno.bedrooms",
                "dyno.bathrooms",
                "dyno.sqft",
                "dyno.agentPhone",
                "dyno.agentEmail"
            ]
        },
        {
            "category": "Изображения",
            "fields": [
                "dyno.agentPhoto",      # Фото агента
                "dyno.propertyImage",   # Фото недвижимости
                "dyno.companyLogo",     # Логотип компании
                "dyno.headshot",        # Альтернативное название для фото агента
                "dyno.logo"             # Альтернативное название для логотипа
            ]
        }
    ]
    
    for category in examples:
        print(f"\n📝 {category['category']}:")
        for field in category['fields']:
            print(f"   ✅ {field}")

def show_svg_structure():
    """Показывает структуру SVG"""
    print("\n🏗️ СТРУКТУРА SVG ШАБЛОНА:")
    print("=" * 30)
    
    svg_example = '''
<!-- Текстовое поле -->
<text id="dyno.agentName" x="100" y="50">
    <tspan x="100" y="50">dyno.agentName</tspan>
</text>

<!-- Изображение -->
<defs>
    <pattern id="agent_pattern">
        <use xlink:href="#agent_image"/>
    </pattern>
    <image id="agent_image" href="placeholder.jpg"/>
</defs>
<rect id="dyno.agentPhoto" fill="url(#agent_pattern)"/>
'''
    
    print("📄 Пример структуры:")
    print(svg_example)
    
    print("🔧 Что происходит при замене:")
    print("1. Система находит <rect id='dyno.agentPhoto'>")
    print("2. Видит fill='url(#agent_pattern)'")
    print("3. Находит <pattern id='agent_pattern'>")
    print("4. Внутри pattern находит <use xlink:href='#agent_image'>")
    print("5. Заменяет href в <image id='agent_image'>")

def show_debugging_tips():
    """Показывает советы по отладке"""
    print("\n🔍 СОВЕТЫ ПО ОТЛАДКЕ:")
    print("=" * 30)
    
    tips = [
        "Запустите сервер с python app.py и смотрите логи",
        "В логах ищите: '🔄 Обрабатываю поле: dyno.fieldName'",
        "Проверьте: '✅ Найден индикатор - это изображение'",
        "Для изображений ищите: '🎯 Найден pattern: pattern_id'",
        "Откройте исходный SVG и найдите все id='dyno.*'",
        "Сравните названия полей в SVG с отправляемыми данными",
        "Используйте quick_preview_test.html для быстрого тестирования"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")

def main():
    """Основная функция"""
    print("🔧 ОБЪЯСНЕНИЕ ЗАМЕНЫ DYNO ПОЛЕЙ")
    print("=" * 60)
    
    explain_replacement_process()
    show_common_problems()
    show_field_examples()
    show_svg_structure()
    show_debugging_tips()
    
    print("\n🎯 ИТОГ:")
    print("Система заменяет dyno поля по ТОЧНОМУ совпадению id в SVG.")
    print("Если поле не заменяется - проверьте название в исходном SVG файле!")

if __name__ == "__main__":
    main()