#!/usr/bin/env python3
"""
АНАЛИЗ DYNO ПОЛЕЙ В SVG ШАБЛОНЕ
==============================

Показывает какие именно dyno поля есть в SVG и как происходит замена
"""

import re
import sqlite3

def analyze_svg_template(template_id=None):
    """Анализирует dyno поля в SVG шаблоне"""
    print("🔍 АНАЛИЗ DYNO ПОЛЕЙ В SVG ШАБЛОНЕ")
    print("=" * 50)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        if template_id:
            cursor.execute('SELECT name, svg_content FROM templates WHERE id = ?', [template_id])
            result = cursor.fetchone()
            if not result:
                print(f"❌ Шаблон с ID {template_id} не найден")
                return
            template_name, svg_content = result
            templates = [(template_id, template_name, svg_content)]
        else:
            # Анализируем все шаблоны
            cursor.execute('SELECT id, name, svg_content FROM templates ORDER BY created_at DESC LIMIT 5')
            templates = cursor.fetchall()
        
        conn.close()
        
        for template_id, template_name, svg_content in templates:
            print(f"\n📋 ШАБЛОН: {template_name} ({template_id})")
            print("=" * 60)
            
            analyze_single_template(svg_content)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def analyze_single_template(svg_content):
    """Анализирует один SVG шаблон"""
    
    # 1. Ищем все dyno поля с id
    print("\n1. 🎯 DYNO ПОЛЯ С ID:")
    id_pattern = r'id="(dyno\.[^"]*)"'
    id_matches = re.findall(id_pattern, svg_content)
    
    if id_matches:
        for field in sorted(set(id_matches)):
            print(f"   ✅ {field}")
            
            # Проверяем что это за элемент
            element_pattern = f'<([^>\\s]+)[^>]*id="{re.escape(field)}"[^>]*>'
            element_match = re.search(element_pattern, svg_content)
            if element_match:
                element_type = element_match.group(1)
                print(f"      📝 Тип элемента: <{element_type}>")
                
                # Если это элемент с fill="url(#pattern)", показываем pattern
                fill_pattern = f'id="{re.escape(field)}"[^>]*fill="url\\(#([^)]+)\\)"'
                fill_match = re.search(fill_pattern, svg_content)
                if fill_match:
                    pattern_id = fill_match.group(1)
                    print(f"      🎨 Использует pattern: #{pattern_id}")
    else:
        print("   ❌ Не найдено dyno полей с id")
    
    # 2. Ищем dyno поля в фигурных скобках
    print("\n2. 🔗 DYNO ПОЛЯ В ФИГУРНЫХ СКОБКАХ:")
    bracket_patterns = [
        r'\{\{(dyno\.[^}]+)\}\}',  # {{dyno.field}}
        r'\{(dyno\.[^}]+)\}',      # {dyno.field}
    ]
    
    bracket_fields = set()
    for pattern in bracket_patterns:
        matches = re.findall(pattern, svg_content)
        bracket_fields.update(matches)
    
    if bracket_fields:
        for field in sorted(bracket_fields):
            print(f"   ✅ {field}")
    else:
        print("   ❌ Не найдено dyno полей в фигурных скобках")
    
    # 3. Ищем все упоминания dyno
    print("\n3. 🔍 ВСЕ УПОМИНАНИЯ DYNO:")
    all_dyno_pattern = r'dyno\.[a-zA-Z][a-zA-Z0-9]*'
    all_matches = re.findall(all_dyno_pattern, svg_content)
    
    if all_matches:
        unique_fields = sorted(set(all_matches))
        for field in unique_fields:
            print(f"   📝 {field}")
    else:
        print("   ❌ Не найдено упоминаний dyno")
    
    # 4. Анализируем изображения
    print("\n4. 🖼️ АНАЛИЗ ИЗОБРАЖЕНИЙ:")
    analyze_image_elements(svg_content)

def analyze_image_elements(svg_content):
    """Анализирует элементы изображений в SVG"""
    
    # Ищем pattern элементы
    pattern_pattern = r'<pattern[^>]*id="([^"]*)"[^>]*>'
    patterns = re.findall(pattern_pattern, svg_content)
    
    if patterns:
        print("   📋 Найденные patterns:")
        for pattern_id in patterns:
            print(f"      🎨 #{pattern_id}")
            
            # Ищем что использует этот pattern
            usage_pattern = f'fill="url\\(#{re.escape(pattern_id)}\\)"[^>]*id="([^"]*)"'
            usage_match = re.search(usage_pattern, svg_content)
            if usage_match:
                element_id = usage_match.group(1)
                print(f"         🎯 Используется элементом: {element_id}")
                
                # Проверяем это dyno поле?
                if element_id.startswith('dyno.'):
                    field_type = determine_field_type(element_id)
                    print(f"         📐 Тип поля: {field_type}")
    
    # Ищем image элементы
    image_pattern = r'<image[^>]*id="([^"]*)"[^>]*>'
    images = re.findall(image_pattern, svg_content)
    
    if images:
        print("   📋 Найденные image элементы:")
        for image_id in images:
            print(f"      🖼️ #{image_id}")

def determine_field_type(field_name):
    """Определяет тип dyno поля"""
    field_lower = field_name.lower()
    
    if any(keyword in field_lower for keyword in ['image', 'photo', 'pic', 'headshot', 'logo', 'portrait']):
        return "изображение"
    elif any(keyword in field_lower for keyword in ['address', 'location', 'addr']):
        return "адрес"
    elif any(keyword in field_lower for keyword in ['name', 'title', 'text']):
        return "текст"
    elif any(keyword in field_lower for keyword in ['price', 'cost', 'amount']):
        return "цена"
    else:
        return "неизвестно"

def show_replacement_logic():
    """Показывает как работает логика замены"""
    print("\n🔧 КАК РАБОТАЕТ ЗАМЕНА DYNO ПОЛЕЙ")
    print("=" * 50)
    
    print("""
📋 АЛГОРИТМ ЗАМЕНЫ:

1. 🔍 ДЛЯ ИЗОБРАЖЕНИЙ:
   - Ищет элемент с id="dyno.fieldName"
   - Элемент должен иметь fill="url(#patternId)"
   - Находит pattern с этим ID
   - Внутри pattern ищет <use xlink:href="#imageId">
   - Заменяет href в соответствующем <image id="imageId">

2. 📝 ДЛЯ ТЕКСТА:
   - Ищет элемент <text id="dyno.fieldName">
   - Внутри ищет <tspan> элементы
   - Заменяет содержимое первого tspan

3. 🏠 ДЛЯ АДРЕСОВ:
   - Как текст, но с автоматическим переносом строк
   - Создает несколько tspan для длинных адресов

⚠️ ВАЖНО:
- Названия полей должны ТОЧНО совпадать
- dyno.companyLogo ≠ dyno.logo ≠ dyno.companylogo
- Регистр имеет значение!
""")

def create_field_mapping_suggestions(svg_content):
    """Создает предложения по маппингу полей"""
    print("\n💡 ПРЕДЛОЖЕНИЯ ПО МАППИНГУ ПОЛЕЙ")
    print("=" * 50)
    
    # Находим все dyno поля в SVG
    all_dyno_pattern = r'dyno\.[a-zA-Z][a-zA-Z0-9]*'
    svg_fields = sorted(set(re.findall(all_dyno_pattern, svg_content)))
    
    # Стандартные поля которые обычно отправляются
    standard_fields = [
        'dyno.agentName',
        'dyno.propertyAddress', 
        'dyno.price',
        'dyno.bedrooms',
        'dyno.bathrooms',
        'dyno.sqft',
        'dyno.agentPhone',
        'dyno.agentEmail',
        'dyno.agentPhoto',
        'dyno.propertyImage',
        'dyno.companyLogo'
    ]
    
    print("📋 ПОЛЯ В SVG ШАБЛОНЕ:")
    for field in svg_fields:
        print(f"   ✅ {field}")
    
    print("\n📋 СТАНДАРТНЫЕ ПОЛЯ (отправляемые):")
    for field in standard_fields:
        if field in svg_fields:
            print(f"   ✅ {field} - СОВПАДАЕТ")
        else:
            print(f"   ❌ {field} - НЕ НАЙДЕНО В SVG")
    
    print("\n🔧 РЕКОМЕНДАЦИИ:")
    print("1. Убедитесь что названия полей в SVG точно совпадают с отправляемыми")
    print("2. Проверьте регистр букв (dyno.companyLogo vs dyno.companylogo)")
    print("3. Добавьте недостающие поля в SVG или измените названия в коде")

def main():
    """Основная функция"""
    print("🔍 АНАЛИЗАТОР DYNO ПОЛЕЙ В SVG")
    print("=" * 60)
    
    analyze_svg_template()
    show_replacement_logic()
    
    # Анализируем конкретный шаблон если есть
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, svg_content FROM templates ORDER BY created_at DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result:
            template_id, template_name, svg_content = result
            print(f"\n🎯 ДЕТАЛЬНЫЙ АНАЛИЗ ПОСЛЕДНЕГО ШАБЛОНА: {template_name}")
            create_field_mapping_suggestions(svg_content)
    except:
        pass

if __name__ == "__main__":
    main()