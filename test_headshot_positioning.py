#!/usr/bin/env python3
"""
ДИАГНОСТИКА ПРОБЛЕМ С ПОЗИЦИОНИРОВАНИЕМ HEADSHOT
===============================================

Проверяем почему headshot съезжает влево/вправо в круглых элементах
"""

import re

def analyze_headshot_positioning_issue():
    """Анализируем проблему с позиционированием headshot"""
    print("🔍 АНАЛИЗ ПРОБЛЕМЫ С ПОЗИЦИОНИРОВАНИЕМ HEADSHOT")
    print("=" * 60)
    
    print("📋 ТЕКУЩИЕ НАСТРОЙКИ В КОДЕ:")
    print("1. aspect_ratio = 'xMidYMid slice' для круглых headshot")
    print("2. scale(0.7) - уменьшение до 70%")
    print("3. translate(0.15, 0.05) - смещение для центрирования")
    print("4. patternTransform применяется к pattern элементу")
    
    print("\n⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
    print("1. 'xMidYMid slice' может обрезать лицо")
    print("2. Фиксированные значения translate не подходят для всех изображений")
    print("3. scale(0.7) может быть слишком маленьким")
    print("4. Не учитывается соотношение сторон исходного изображения")

def test_different_aspect_ratios():
    """Тестируем разные aspect ratio настройки"""
    print("\n🧪 ТЕСТ РАЗНЫХ ASPECT RATIO НАСТРОЕК")
    print("=" * 50)
    
    aspect_ratios = [
        {
            "name": "xMidYMid slice (текущий)",
            "value": "xMidYMid slice",
            "description": "Заполняет весь круг, может обрезать части изображения",
            "good_for": "Когда нужно заполнить весь круг",
            "problem": "Может обрезать лицо если оно не по центру"
        },
        {
            "name": "xMidYMid meet (альтернатива)",
            "value": "xMidYMid meet", 
            "description": "Показывает всё изображение, может оставить пустые области",
            "good_for": "Когда важно показать всё лицо",
            "problem": "Может оставить пустые области в круге"
        },
        {
            "name": "xMinYMid slice",
            "value": "xMinYMid slice",
            "description": "Выравнивание по левому краю",
            "good_for": "Если лицо смещено вправо на фото",
            "problem": "Может срезать правую часть"
        },
        {
            "name": "xMaxYMid slice", 
            "value": "xMaxYMid slice",
            "description": "Выравнивание по правому краю",
            "good_for": "Если лицо смещено влево на фото", 
            "problem": "Может срезать левую часть"
        }
    ]
    
    for ratio in aspect_ratios:
        print(f"\n📐 {ratio['name']}: {ratio['value']}")
        print(f"   📝 Описание: {ratio['description']}")
        print(f"   ✅ Хорошо для: {ratio['good_for']}")
        print(f"   ⚠️ Проблема: {ratio['problem']}")

def suggest_improved_headshot_logic():
    """Предлагаем улучшенную логику для headshot"""
    print("\n💡 ПРЕДЛАГАЕМОЕ РЕШЕНИЕ")
    print("=" * 50)
    
    print("🎯 АДАПТИВНАЯ ЛОГИКА ДЛЯ HEADSHOT:")
    print("1. Определять соотношение сторон исходного изображения")
    print("2. Использовать разные настройки для портретных/альбомных фото")
    print("3. Добавить возможность настройки позиционирования")
    print("4. Использовать viewBox для лучшего контроля")
    
    improved_code = '''
def get_headshot_settings(image_url, element_shape):
    """Улучшенная функция для настройки headshot"""
    
    if element_shape != 'circular':
        return 'xMidYMid meet', None, None
    
    # Для круглых headshot используем адаптивную логику
    settings = {
        'aspect_ratio': 'xMidYMid slice',  # Заполняем круг
        'scale': 1.0,  # Без уменьшения по умолчанию
        'translate_x': 0,  # Центрирование по X
        'translate_y': 0   # Центрирование по Y
    }
    
    # Можно добавить анализ изображения для определения лучших настроек
    # или позволить пользователю настраивать позицию
    
    return settings
    '''
    
    print("\n📝 УЛУЧШЕННЫЙ КОД:")
    print(improved_code)

def test_transform_combinations():
    """Тестируем разные комбинации transform"""
    print("\n🔧 ТЕСТ TRANSFORM КОМБИНАЦИЙ")
    print("=" * 50)
    
    transforms = [
        {
            "name": "Текущий (проблемный)",
            "transform": "scale(0.7) translate(0.15, 0.05)",
            "description": "Уменьшение + фиксированное смещение",
            "problem": "Фиксированное смещение не подходит для всех фото"
        },
        {
            "name": "Только центрирование",
            "transform": "translate(0, 0)",
            "description": "Без масштабирования, только центрирование",
            "benefit": "Сохраняет размер, точное центрирование"
        },
        {
            "name": "Адаптивное масштабирование",
            "transform": "scale(1.2) translate(-0.1, -0.05)",
            "description": "Увеличение для лучшего заполнения",
            "benefit": "Лучше заполняет круг, меньше пустых областей"
        },
        {
            "name": "Без transform",
            "transform": None,
            "description": "Полагаемся только на preserveAspectRatio",
            "benefit": "Простота, меньше переменных"
        }
    ]
    
    for t in transforms:
        print(f"\n🔧 {t['name']}:")
        if t['transform']:
            print(f"   Transform: {t['transform']}")
        print(f"   📝 {t['description']}")
        if 'problem' in t:
            print(f"   ⚠️ Проблема: {t['problem']}")
        if 'benefit' in t:
            print(f"   ✅ Преимущество: {t['benefit']}")

def create_test_svg_examples():
    """Создаем примеры SVG для тестирования"""
    print("\n📄 ПРИМЕРЫ SVG ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    # Пример проблемного SVG
    problematic_svg = '''
<svg width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <pattern id="headshot_pattern" patternUnits="objectBoundingBox" width="1" height="1" 
             patternTransform="scale(0.7) translate(0.15, 0.05)">
      <image id="headshot_image" href="agent_photo.jpg" width="1" height="1" 
             preserveAspectRatio="xMidYMid slice"/>
    </pattern>
    <clipPath id="circle_clip">
      <circle cx="100" cy="100" r="80"/>
    </clipPath>
  </defs>
  
  <rect id="dyno.agentPhoto" x="20" y="20" width="160" height="160" 
        fill="url(#headshot_pattern)" clip-path="url(#circle_clip)"/>
</svg>
    '''
    
    # Улучшенный SVG
    improved_svg = '''
<svg width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <pattern id="headshot_pattern" patternUnits="objectBoundingBox" width="1" height="1">
      <image id="headshot_image" href="agent_photo.jpg" width="1" height="1" 
             preserveAspectRatio="xMidYMid slice"/>
    </pattern>
    <clipPath id="circle_clip">
      <circle cx="100" cy="100" r="80"/>
    </clipPath>
  </defs>
  
  <rect id="dyno.agentPhoto" x="20" y="20" width="160" height="160" 
        fill="url(#headshot_pattern)" clip-path="url(#circle_clip)"/>
</svg>
    '''
    
    print("❌ ПРОБЛЕМНЫЙ SVG (с фиксированным transform):")
    print(problematic_svg)
    
    print("\n✅ УЛУЧШЕННЫЙ SVG (без фиксированного transform):")
    print(improved_svg)
    
    print("\n📋 КЛЮЧЕВЫЕ ОТЛИЧИЯ:")
    print("1. Убран patternTransform с фиксированными значениями")
    print("2. Полагаемся на preserveAspectRatio для позиционирования")
    print("3. Можно добавить настройки позиции через API")

def main():
    """Основная функция диагностики"""
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМ С HEADSHOT ПОЗИЦИОНИРОВАНИЕМ")
    print("=" * 70)
    
    analyze_headshot_positioning_issue()
    test_different_aspect_ratios()
    suggest_improved_headshot_logic()
    test_transform_combinations()
    create_test_svg_examples()
    
    print("\n🎯 РЕКОМЕНДАЦИИ ДЛЯ ИСПРАВЛЕНИЯ:")
    print("1. Убрать фиксированные значения translate(0.15, 0.05)")
    print("2. Использовать только preserveAspectRatio для позиционирования")
    print("3. Добавить возможность настройки позиции через API")
    print("4. Тестировать с разными типами фотографий")
    print("5. Возможно добавить предпросмотр для пользователя")

if __name__ == "__main__":
    main()