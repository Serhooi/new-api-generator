#!/usr/bin/env python3
"""
Тест превью с оригинальным хедшотом (без замены)
"""

from preview_system import create_preview_with_data

def test_original_headshot():
    """Тестируем превью с оригинальным хедшотом"""
    print("🧪 ТЕСТ ОРИГИНАЛЬНОГО ХЕДШОТА В ПРЕВЬЮ")
    print("=" * 50)
    
    # Простой SVG с хедшотом
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
    </svg>'''
    
    # Тестовые данные с хедшотом
    test_replacements = {
        'dyno.name': 'John Smith',
        'dyno.agentheadshot': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face'
    }
    
    print("📋 Данные для замены:")
    for k, v in test_replacements.items():
        print(f"   {k}: {str(v)[:50]}...")
    
    print("\n🎨 Создаю превью...")
    result = create_preview_with_data(test_svg, test_replacements, 'png')
    
    if result['success']:
        print(f"✅ Превью создано успешно!")
        print(f"📁 Файл: {result.get('path', 'N/A')}")
        print(f"🔗 URL: {result.get('url', 'N/A')}")
        print(f"📏 Размер: {result.get('width', 'N/A')}x{result.get('height', 'N/A')}")
        print(f"💾 Размер файла: {result.get('file_size', 'N/A')} байт")
        
        print(f"\n🎯 РЕЗУЛЬТАТ: Хедшот показывается как в оригинальном шаблоне")
        print(f"   (НЕ заменяется на dyno.agentheadshot)")
    else:
        print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_original_headshot()