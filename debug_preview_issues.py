#!/usr/bin/env python3
"""
ДИАГНОСТИКА ПРОБЛЕМ С ПРЕВЬЮ
============================

Анализируем почему не работают замены изображений в превью
"""

import re

def analyze_preview_issues():
    """Анализируем проблемы с превью"""
    print("🔍 АНАЛИЗ ПРОБЛЕМ С ПРЕВЬЮ")
    print("=" * 50)
    
    print("📋 ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ:")
    print("1. ❌ Лого не отображается")
    print("2. ❌ Фото агента съехало (headshot positioning)")
    print("3. ❌ Фото недвижимости не заменилось")
    
    print("\n🔍 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
    
    print("\n1. ПРОБЛЕМА С ЛОГО:")
    print("   - Поле dyno.companyLogo может не существовать в шаблоне")
    print("   - Или называется по-другому (dyno.logo, dyno.brandLogo)")
    print("   - Или не определяется как изображение")
    
    print("\n2. ПРОБЛЕМА С HEADSHOT:")
    print("   - Исправление headshot может не работать в preview_system.py")
    print("   - Функция process_svg_font_perfect может не вызываться")
    print("   - Или вызывается старая версия без исправлений")
    
    print("\n3. ПРОБЛЕМА С PROPERTY IMAGE:")
    print("   - Поле dyno.propertyImage может называться по-другому")
    print("   - Или не определяется как изображение")
    print("   - Или URL не загружается правильно")

def test_field_detection():
    """Тестируем определение полей изображений"""
    print("\n🧪 ТЕСТ ОПРЕДЕЛЕНИЯ ПОЛЕЙ ИЗОБРАЖЕНИЙ")
    print("=" * 50)
    
    # Импортируем функции из app.py
    try:
        from app import determine_image_type, is_image_field
        
        test_fields = [
            'dyno.agentPhoto',
            'dyno.propertyImage', 
            'dyno.companyLogo',
            'dyno.logo',
            'dyno.brandLogo',
            'dyno.headshot',
            'dyno.agentHeadshot'
        ]
        
        for field in test_fields:
            is_image = is_image_field(field)
            if is_image:
                image_type = determine_image_type(field)
                print(f"✅ {field}: {image_type}")
            else:
                print(f"❌ {field}: НЕ определяется как изображение")
                
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверим логику определения полей вручную...")
        
        # Ручная проверка логики
        def manual_is_image_field(dyno_field):
            field_lower = dyno_field.lower()
            explicit_image_indicators = ['image', 'headshot', 'logo', 'photo', 'pic', 'portrait']
            
            for indicator in explicit_image_indicators:
                if indicator in field_lower:
                    return True
            
            if 'agent' in field_lower and any(img in field_lower for img in ['photo', 'image', 'pic', 'headshot']):
                return True
            
            return False
        
        test_fields = [
            'dyno.agentPhoto',
            'dyno.propertyImage', 
            'dyno.companyLogo',
            'dyno.logo',
            'dyno.brandLogo'
        ]
        
        for field in test_fields:
            is_image = manual_is_image_field(field)
            print(f"{'✅' if is_image else '❌'} {field}: {'изображение' if is_image else 'НЕ изображение'}")

def check_svg_template_fields():
    """Проверяем какие поля есть в SVG шаблоне"""
    print("\n📄 АНАЛИЗ ПОЛЕЙ В SVG ШАБЛОНЕ")
    print("=" * 50)
    
    print("Нужно проверить исходный SVG шаблон на наличие полей:")
    print("1. Найти все id='dyno.*' в SVG")
    print("2. Проверить какие из них связаны с изображениями")
    print("3. Убедиться что названия полей совпадают с отправляемыми данными")
    
    # Пример анализа SVG
    sample_svg_patterns = [
        r'id="dyno\.([^"]*)"',
        r'id=\'dyno\.([^\']*)\'',
        r'\{\{dyno\.([^}]*)\}\}',
        r'\{dyno\.([^}]*)\}'
    ]
    
    print("\n🔍 ПАТТЕРНЫ ДЛЯ ПОИСКА DYNO ПОЛЕЙ:")
    for pattern in sample_svg_patterns:
        print(f"   {pattern}")

def suggest_fixes():
    """Предлагаем исправления"""
    print("\n💡 ПРЕДЛАГАЕМЫЕ ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    print("1. ИСПРАВЛЕНИЕ ЛОГО:")
    print("   - Проверить точное название поля в SVG (dyno.logo vs dyno.companyLogo)")
    print("   - Добавить 'logo' в explicit_image_indicators если отсутствует")
    print("   - Убедиться что поле определяется как изображение")
    
    print("\n2. ИСПРАВЛЕНИЕ HEADSHOT:")
    print("   - Проверить что preview_system.py использует исправленную версию process_svg_font_perfect")
    print("   - Убедиться что импорт работает правильно")
    print("   - Возможно нужно скопировать исправления в preview_system.py")
    
    print("\n3. ИСПРАВЛЕНИЕ PROPERTY IMAGE:")
    print("   - Проверить название поля (dyno.propertyImage vs dyno.propertyimage)")
    print("   - Убедиться что URL загружается и доступен")
    print("   - Проверить что поле определяется как изображение")
    
    print("\n4. ОБЩИЕ ИСПРАВЛЕНИЯ:")
    print("   - Добавить больше логирования в preview_system.py")
    print("   - Проверить что все замены применяются")
    print("   - Тестировать с простыми локальными изображениями")

def create_test_data():
    """Создаем тестовые данные для отладки"""
    print("\n🧪 ТЕСТОВЫЕ ДАННЫЕ ДЛЯ ОТЛАДКИ")
    print("=" * 50)
    
    test_data = {
        'dyno.agentName': 'John Smith',
        'dyno.propertyAddress': '123 Main Street, Beverly Hills, CA 90210',
        'dyno.price': '$450,000',
        'dyno.bedrooms': '3',
        'dyno.bathrooms': '2',
        'dyno.sqft': '1,850',
        'dyno.agentPhone': '(555) 123-4567',
        'dyno.agentEmail': 'john@realty.com',
        
        # Тестируем разные варианты названий полей изображений
        'dyno.agentPhoto': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
        'dyno.propertyImage': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop',
        'dyno.companyLogo': 'https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO',
        
        # Альтернативные названия
        'dyno.logo': 'https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO',
        'dyno.brandLogo': 'https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO',
        'dyno.headshot': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
        'dyno.agentHeadshot': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
    }
    
    print("📝 Тестовые данные для API запроса:")
    print("```json")
    import json
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print("```")
    
    print("\n🔧 Команда для тестирования через curl:")
    print("""
curl -X POST http://localhost:5000/api/preview/with-data \\
  -H "Content-Type: application/json" \\
  -d '{
    "template_id": "your-template-id",
    "replacements": {
      "dyno.agentPhoto": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
      "dyno.propertyImage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop",
      "dyno.companyLogo": "https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO"
    },
    "type": "png"
  }'
    """)

def main():
    """Основная функция диагностики"""
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМ С ПРЕВЬЮ")
    print("=" * 60)
    
    analyze_preview_issues()
    test_field_detection()
    check_svg_template_fields()
    suggest_fixes()
    create_test_data()
    
    print("\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Проверить исходный SVG шаблон на наличие нужных полей")
    print("2. Убедиться что preview_system.py использует исправленную логику")
    print("3. Добавить логирование для отладки замен")
    print("4. Протестировать с простыми изображениями")

if __name__ == "__main__":
    main()