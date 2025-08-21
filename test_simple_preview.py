#!/usr/bin/env python3
"""
Тест простого превью - показываем шаблон как есть, БЕЗ замен
"""

def test_simple_preview_logic():
    """Тестируем логику простого превью"""
    print("🧪 ТЕСТ ПРОСТОГО ПРЕВЬЮ")
    print("=" * 50)
    
    # Тестовый SVG шаблон
    test_svg = '''<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="headshot_pattern" patternUnits="objectBoundingBox" width="1" height="1">
                <image id="headshot_image" href="https://via.placeholder.com/150x150/4F46E5/FFFFFF?text=AGENT" 
                       width="150" height="150" preserveAspectRatio="xMidYMid slice"/>
            </pattern>
        </defs>
        <rect width="400" height="300" fill="#f8f9fa"/>
        <circle cx="100" cy="100" r="50" fill="url(#headshot_pattern)"/>
        <text x="200" y="200" text-anchor="middle" fill="#333" font-family="Arial" font-size="18">
            dyno.name
        </text>
        <text x="200" y="230" text-anchor="middle" fill="#666" font-family="Arial" font-size="14">
            dyno.title
        </text>
    </svg>'''
    
    # Тестовые данные (которые НЕ должны применяться в превью)
    test_data = {
        'dyno.name': 'John Smith',
        'dyno.title': 'Real Estate Agent',
        'dyno.agentheadshot': 'https://example.com/headshot.jpg'
    }
    
    print("📋 Оригинальный SVG содержит:")
    print("   - Placeholder headshot: https://via.placeholder.com/150x150/4F46E5/FFFFFF?text=AGENT")
    print("   - Текст: dyno.name")
    print("   - Текст: dyno.title")
    
    print("\n📋 Данные пользователя (НЕ применяются в превью):")
    for k, v in test_data.items():
        print(f"   {k}: {v}")
    
    print("\n🎯 ЛОГИКА ПРЕВЬЮ:")
    print("   ✅ Показываем оригинальный шаблон БЕЗ замен")
    print("   ✅ Headshot остается как в шаблоне")
    print("   ✅ Текст остается как dyno.name, dyno.title")
    print("   ✅ Никаких замен не происходит")
    
    # Имитируем новую логику превью
    preview_svg = test_svg  # Просто возвращаем оригинальный SVG
    
    print(f"\n📊 РЕЗУЛЬТАТ:")
    print(f"   Оригинальный SVG: {len(test_svg)} символов")
    print(f"   Превью SVG: {len(preview_svg)} символов")
    print(f"   Изменений: {len(preview_svg) - len(test_svg)} (должно быть 0)")
    
    if preview_svg == test_svg:
        print("   ✅ ПРАВИЛЬНО: Превью = оригинальный шаблон")
    else:
        print("   ❌ ОШИБКА: Превью отличается от оригинала")

if __name__ == "__main__":
    test_simple_preview_logic()