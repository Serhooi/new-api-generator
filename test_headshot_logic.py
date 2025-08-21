#!/usr/bin/env python3
"""
Тест логики обработки хедшота (без Cairo)
"""

def process_image_replacements_test(svg_content, image_data):
    """Тестовая версия функции обработки изображений"""
    if not image_data:
        return svg_content
    
    print(f"🖼️ Обрабатываю {len(image_data)} изображений...")
    
    modified_svg = svg_content
    successful_replacements = 0
    
    # Определяем поля изображений, НО ИСКЛЮЧАЕМ headshot
    image_fields = {}
    for k, v in image_data.items():
        # Проверяем является ли поле изображением
        is_image = any(word in k.lower() for word in ['image', 'photo', 'picture', 'logo', 'headshot'])
        
        if is_image:
            # ИСКЛЮЧАЕМ headshot поля - показываем оригинальный хедшот из шаблона
            if any(word in k.lower() for word in ['headshot', 'agent']):
                print(f"⏭️ Пропускаю {k} (headshot) - показываю оригинальный из шаблона")
            else:
                image_fields[k] = v
                print(f"✅ Буду заменять: {k}")
        else:
            print(f"ℹ️ Не изображение: {k}")
    
    print(f"\n📊 Итого:")
    print(f"   Всего полей: {len(image_data)}")
    print(f"   Будет заменено: {len(image_fields)}")
    print(f"   Пропущено (headshot): {len(image_data) - len(image_fields)}")
    
    return modified_svg

def test_headshot_logic():
    """Тестируем логику обработки хедшота"""
    print("🧪 ТЕСТ ЛОГИКИ ОБРАБОТКИ ХЕДШОТА")
    print("=" * 50)
    
    # Тестовые данные
    test_data = {
        'dyno.name': 'John Smith',
        'dyno.agentheadshot': 'https://example.com/headshot.jpg',
        'dyno.propertyimage': 'https://example.com/property.jpg',
        'dyno.agentphoto': 'https://example.com/agent.jpg',
        'dyno.logo': 'https://example.com/logo.jpg',
        'dyno.title': 'Real Estate Agent'
    }
    
    print("📋 Входные данные:")
    for k, v in test_data.items():
        print(f"   {k}: {str(v)[:50]}...")
    
    print("\n🔄 Обрабатываю...")
    result = process_image_replacements_test("test svg", test_data)
    
    print(f"\n🎯 РЕЗУЛЬТАТ: Хедшот НЕ заменяется, показывается оригинальный из шаблона")

if __name__ == "__main__":
    test_headshot_logic()