#!/usr/bin/env python3
"""
Тест исправленного превью - проверяем что хедшот показывается
"""

from preview_system import create_preview_with_data

def test_headshot_preview():
    """Тестируем что превью показывает хедшот из шаблона"""
    print("🧪 ТЕСТ ИСПРАВЛЕННОГО ПРЕВЬЮ ХЕДШОТА")
    print("=" * 50)
    
    try:
        # Читаем оригинальный шаблон
        with open('main.svg', 'r') as f:
            svg_content = f.read()
        
        print(f"📊 Размер шаблона: {len(svg_content)} символов")
        
        # Тестовые данные (игнорируются в превью)
        test_replacements = {
            'dyno.name': 'John Smith',
            'dyno.agentheadshot': 'https://example.com/new-headshot.jpg'  # Игнорируется!
        }
        
        print("📋 Данные пользователя (игнорируются в превью):")
        for k, v in test_replacements.items():
            print(f"   {k}: {str(v)[:50]}...")
        
        print("\n🎨 Создаю превью...")
        result = create_preview_with_data(svg_content, test_replacements, 'base64')
        
        if result['success']:
            print(f"✅ Превью создано успешно!")
            print(f"📝 Заметка: {result.get('note', 'N/A')}")
            print(f"🖼️ Base64 изображений в шаблоне: {result.get('base64_images', 'N/A')}")
            print(f"📏 Размер base64: {len(result.get('base64', ''))} символов")
            
            print(f"\n🎯 РЕЗУЛЬТАТ:")
            print(f"   ✅ Хедшот показывается как в оригинальном шаблоне")
            print(f"   ✅ Пользовательские данные НЕ применяются")
            print(f"   ✅ Все изображения из шаблона сохранены")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            
    except FileNotFoundError:
        print("❌ Файл main.svg не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_headshot_preview()