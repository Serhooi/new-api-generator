#!/usr/bin/env python3
"""
ИСПРАВЛЕННАЯ ОБРАБОТКА HEADSHOT ПОЗИЦИОНИРОВАНИЯ
===============================================

Убираем фиксированные transform значения и улучшаем позиционирование
"""

import re

def process_headshot_improved(svg_content, dyno_field, image_url):
    """
    УЛУЧШЕННАЯ функция обработки headshot без фиксированных смещений
    """
    print(f"🎯 УЛУЧШЕННАЯ обработка headshot: {dyno_field}")
    
    # Определяем тип изображения
    field_lower = dyno_field.lower()
    is_headshot = any(keyword in field_lower for keyword in ['headshot', 'agent', 'profile', 'portrait'])
    
    if not is_headshot:
        print("   ⚠️ Не headshot поле, используем стандартную обработку")
        return svg_content
    
    # Безопасное экранирование URL
    safe_url = str(image_url).replace('&', '&amp;')
    
    # Ищем элемент с id
    element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\(#([^)]+)\\)"[^>]*>'
    match = re.search(element_pattern, svg_content)
    
    if not match:
        print(f"   ❌ Элемент с id {dyno_field} не найден")
        return svg_content
    
    pattern_id = match.group(1)
    print(f"   🎯 Найден pattern: {pattern_id}")
    
    # Определяем форму элемента (круглый или прямоугольный)
    element_shape = determine_element_shape(svg_content, pattern_id)
    print(f"   🔍 Форма элемента: {element_shape}")
    
    # Выбираем правильные настройки для headshot
    if element_shape == 'circular':
        # Для круглых headshot - заполняем круг, но без фиксированных смещений
        aspect_ratio = 'xMidYMid slice'
        use_transform = False  # УБИРАЕМ фиксированные transform!
        print(f"   ⚙️ Круглый headshot: {aspect_ratio}, без transform")
    else:
        # Для прямоугольных headshot - показываем всё лицо
        aspect_ratio = 'xMidYMid meet'
        use_transform = False
        print(f"   ⚙️ Прямоугольный headshot: {aspect_ratio}")
    
    # Ищем pattern блок
    pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
    pattern_match = re.search(pattern_block_pattern, svg_content, re.DOTALL)
    
    if not pattern_match:
        print(f"   ❌ Pattern блок {pattern_id} не найден")
        return svg_content
    
    pattern_content = pattern_match.group(1)
    pattern_full = pattern_match.group(0)
    
    # УБИРАЕМ любые существующие patternTransform
    old_pattern = pattern_full
    
    # Удаляем patternTransform если есть
    new_pattern = re.sub(r'\s*patternTransform="[^"]*"', '', old_pattern)
    
    # Удаляем transform если есть
    new_pattern = re.sub(r'\s*transform="[^"]*"', '', new_pattern)
    
    if new_pattern != old_pattern:
        svg_content = svg_content.replace(old_pattern, new_pattern)
        print(f"   ✅ Удалены фиксированные transform из pattern")
    
    # Ищем use элемент внутри pattern
    use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
    use_match = re.search(use_pattern, pattern_content)
    
    if use_match:
        image_id = use_match.group(1)
        print(f"   🔗 Найден use элемент: #{image_id}")
        
        # Ищем соответствующий image элемент
        image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
        image_match = re.search(image_pattern, svg_content)
        
        if image_match:
            old_image = image_match.group(0)
            new_image = old_image
            
            # Заменяем URL
            new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
            new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
            
            # Устанавливаем правильный preserveAspectRatio
            if 'preserveAspectRatio=' in new_image:
                new_image = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', new_image)
            else:
                if new_image.endswith('/>'):
                    new_image = new_image[:-2] + f' preserveAspectRatio="{aspect_ratio}"/>'
                elif new_image.endswith('>'):
                    new_image = new_image[:-1] + f' preserveAspectRatio="{aspect_ratio}">'
            
            svg_content = svg_content.replace(old_image, new_image)
            print(f"   ✅ Headshot заменен с настройкой: {aspect_ratio}")
            print(f"   🎯 БЕЗ фиксированных смещений - изображение будет центрировано автоматически")
        else:
            print(f"   ❌ Image элемент #{image_id} не найден")
    else:
        print(f"   ❌ Use элемент в pattern не найден")
    
    return svg_content

def determine_element_shape(svg_content, pattern_id):
    """Определяет форму элемента (круглый или прямоугольный)"""
    
    # Ищем clipPath связанный с pattern
    clip_pattern = f'<clipPath[^>]*id="[^"]*{re.escape(pattern_id)}[^"]*"[^>]*>(.*?)</clipPath>'
    clip_match = re.search(clip_pattern, svg_content, re.DOTALL)
    
    if clip_match:
        clip_content = clip_match.group(1)
        
        # Проверяем наличие circle или ellipse
        if '<circle' in clip_content or '<ellipse' in clip_content:
            return 'circular'
        
        # Проверяем наличие rect с большими rx/ry (скругленные углы)
        rect_pattern = r'<rect[^>]*rx="([^"]*)"[^>]*ry="([^"]*)"[^>]*>'
        rect_match = re.search(rect_pattern, clip_content)
        if rect_match:
            try:
                rx = float(rect_match.group(1) or 0)
                ry = float(rect_match.group(2) or 0)
                
                # Если радиус скругления большой, считаем круглым
                if rx > 20 or ry > 20:
                    return 'circular'
            except:
                pass
        
        # Проверяем path с круглыми формами
        if '<path' in clip_content:
            path_pattern = r'd="([^"]*)"'
            path_match = re.search(path_pattern, clip_content)
            if path_match:
                path_data = path_match.group(1)
                # Ищем команды дуг (A) или много кривых (C)
                if 'A' in path_data or path_data.count('C') > 4:
                    return 'circular'
    
    # Альтернативный способ - анализ размеров pattern
    pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*width="([^"]*)"[^>]*height="([^"]*)"[^>]*>'
    pattern_match = re.search(pattern_pattern, svg_content)
    
    if pattern_match:
        try:
            width = float(pattern_match.group(1) or 0)
            height = float(pattern_match.group(2) or 0)
            
            # Если ширина и высота примерно равны, скорее всего круглый
            if abs(width - height) < 5:
                return 'circular'
        except:
            pass
    
    # По умолчанию считаем прямоугольным
    return 'rectangular'

def create_improved_headshot_function():
    """Создаем улучшенную функцию для замены в основном коде"""
    
    improved_function = '''
def process_headshot_without_fixed_transforms(svg_content, dyno_field, image_url):
    """
    ИСПРАВЛЕННАЯ функция обработки headshot:
    - Убираем фиксированные transform значения
    - Полагаемся на preserveAspectRatio для позиционирования
    - Лучше работает с разными типами фотографий
    """
    
    field_lower = dyno_field.lower()
    is_headshot = any(keyword in field_lower for keyword in ['headshot', 'agent', 'profile', 'portrait'])
    
    if not is_headshot:
        return svg_content
    
    # Безопасное экранирование URL
    safe_url = str(image_url).replace('&', '&amp;')
    
    # Ищем элемент с pattern
    element_pattern = f'<[^>]*id="{re.escape(dyno_field)}"[^>]*fill="url\\\\(#([^)]+)\\\\)"[^>]*>'
    match = re.search(element_pattern, svg_content)
    
    if not match:
        return svg_content
    
    pattern_id = match.group(1)
    
    # Определяем форму элемента
    element_shape = determine_element_shape(svg_content, pattern_id)
    
    # Выбираем aspect ratio без фиксированных смещений
    if element_shape == 'circular':
        aspect_ratio = 'xMidYMid slice'  # Заполняет круг, центрирует автоматически
    else:
        aspect_ratio = 'xMidYMid meet'   # Показывает всё изображение
    
    # Убираем любые patternTransform из pattern
    pattern_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>'
    pattern_match = re.search(pattern_pattern, svg_content)
    
    if pattern_match:
        old_pattern_tag = pattern_match.group(0)
        # Удаляем patternTransform и transform
        new_pattern_tag = re.sub(r'\\s*patternTransform="[^"]*"', '', old_pattern_tag)
        new_pattern_tag = re.sub(r'\\s*transform="[^"]*"', '', new_pattern_tag)
        
        if new_pattern_tag != old_pattern_tag:
            svg_content = svg_content.replace(old_pattern_tag, new_pattern_tag)
    
    # Находим и обновляем image элемент
    use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
    pattern_content_match = re.search(f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>', svg_content, re.DOTALL)
    
    if pattern_content_match:
        pattern_content = pattern_content_match.group(1)
        use_match = re.search(use_pattern, pattern_content)
        
        if use_match:
            image_id = use_match.group(1)
            image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
            image_match = re.search(image_pattern, svg_content)
            
            if image_match:
                old_image = image_match.group(0)
                new_image = old_image
                
                # Обновляем URL и aspect ratio
                new_image = re.sub(r'href="[^"]*"', f'href="{safe_url}"', new_image)
                new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{safe_url}"', new_image)
                
                if 'preserveAspectRatio=' in new_image:
                    new_image = re.sub(r'preserveAspectRatio="[^"]*"', f'preserveAspectRatio="{aspect_ratio}"', new_image)
                else:
                    if new_image.endswith('/>'):
                        new_image = new_image[:-2] + f' preserveAspectRatio="{aspect_ratio}"/>'
                    elif new_image.endswith('>'):
                        new_image = new_image[:-1] + f' preserveAspectRatio="{aspect_ratio}">'
                
                svg_content = svg_content.replace(old_image, new_image)
    
    return svg_content
    '''
    
    return improved_function

def test_improved_logic():
    """Тестируем улучшенную логику"""
    print("\n🧪 ТЕСТ УЛУЧШЕННОЙ ЛОГИКИ")
    print("=" * 50)
    
    test_svg = '''<svg width="200" height="200">
  <defs>
    <pattern id="agent_pattern" patternUnits="objectBoundingBox" width="1" height="1" 
             patternTransform="scale(0.7) translate(0.15, 0.05)">
      <use xlink:href="#agent_image"/>
    </pattern>
    <image id="agent_image" href="old_url.jpg" width="1" height="1" 
           preserveAspectRatio="xMidYMid meet"/>
    <clipPath id="circle_clip">
      <circle cx="100" cy="100" r="80"/>
    </clipPath>
  </defs>
  
  <rect id="dyno.agentPhoto" x="20" y="20" width="160" height="160" 
        fill="url(#agent_pattern)" clip-path="url(#circle_clip)"/>
</svg>'''
    
    print("📝 Исходный SVG (с проблемным patternTransform):")
    print(test_svg)
    
    # Применяем улучшенную обработку
    result = process_headshot_improved(test_svg, "dyno.agentPhoto", "https://example.com/new_agent.jpg")
    
    print("\n✅ Результат после улучшенной обработки:")
    print(result)
    
    print("\n📋 ЧТО ИЗМЕНИЛОСЬ:")
    print("1. ❌ Удален patternTransform='scale(0.7) translate(0.15, 0.05)'")
    print("2. ✅ Обновлен URL изображения")
    print("3. ✅ Установлен preserveAspectRatio='xMidYMid slice' для круглого элемента")
    print("4. ✅ Изображение будет автоматически центрироваться без фиксированных смещений")

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С HEADSHOT ПОЗИЦИОНИРОВАНИЕМ")
    print("=" * 70)
    
    print("🎯 ПРОБЛЕМА:")
    print("Фиксированные значения transform='scale(0.7) translate(0.15, 0.05)' не подходят для всех фотографий")
    print("Это приводит к смещению headshot влево/вправо в круглых элементах")
    
    print("\n💡 РЕШЕНИЕ:")
    print("1. Убираем все фиксированные patternTransform и transform")
    print("2. Полагаемся на preserveAspectRatio для автоматического центрирования")
    print("3. Используем 'xMidYMid slice' для круглых headshot")
    print("4. Изображение автоматически центрируется и заполняет круг")
    
    test_improved_logic()
    
    improved_code = create_improved_headshot_function()
    print(f"\n📝 УЛУЧШЕННАЯ ФУНКЦИЯ ДЛЯ ЗАМЕНЫ В КОДЕ:")
    print(improved_code)
    
    print("\n🎯 КАК ПРИМЕНИТЬ ИСПРАВЛЕНИЕ:")
    print("1. Найти в app.py строки с patternTransform и фиксированными translate")
    print("2. Заменить логику на улучшенную версию")
    print("3. Убрать все фиксированные смещения")
    print("4. Тестировать с разными типами фотографий")

if __name__ == "__main__":
    main()