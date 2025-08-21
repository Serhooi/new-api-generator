#!/usr/bin/env python3
"""
Исправление aspect ratio для правильного отображения изображений
"""

def fix_aspect_ratio_in_app():
    """Исправляем aspect ratio в app.py"""
    
    print("📝 Исправляю aspect ratio в app.py...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Ищем где устанавливается aspect ratio
    old_aspect_ratio = 'aspect_ratio = "xMidYMid slice"'
    new_aspect_ratio = 'aspect_ratio = "xMidYMid slice"'
    
    # Ищем где создается image тег
    old_image_creation = '''                    image_element = ET.SubElement(defs, 'image')
                    image_element.set('id', image_id)
                    image_element.set('width', str(original_width))
                    image_element.set('height', str(original_height))
                    image_element.set('preserveAspectRatio', 'none')
                    image_element.set('{http://www.w3.org/1999/xlink}href', image_data)'''
    
    new_image_creation = '''                    image_element = ET.SubElement(defs, 'image')
                    image_element.set('id', image_id)
                    image_element.set('width', str(original_width))
                    image_element.set('height', str(original_height))
                    image_element.set('preserveAspectRatio', 'xMidYMid slice')  # Правильный aspect ratio
                    image_element.set('{http://www.w3.org/1999/xlink}href', image_data)'''
    
    # Заменяем
    if old_image_creation in content:
        content = content.replace(old_image_creation, new_image_creation)
        print("✅ Aspect ratio исправлен в создании image элемента")
    else:
        print("⚠️ Не найден код создания image элемента")
    
    # Также ищем другие места где может быть preserveAspectRatio="none"
    content = content.replace('preserveAspectRatio="none"', 'preserveAspectRatio="xMidYMid slice"')
    print("✅ Все preserveAspectRatio='none' заменены на 'xMidYMid slice'")
    
    # Сохраняем
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с правильным aspect ratio")
    return True

if __name__ == "__main__":
    print("🖼️ ИСПРАВЛЕНИЕ ASPECT RATIO")
    print("=" * 40)
    
    fix_aspect_ratio_in_app()
    
    print("\n✅ Aspect ratio исправлен!")
    print("📋 Теперь изображения будут:")
    print("  - Сохранять пропорции")
    print("  - Заполнять всю область")
    print("  - Центрироваться")
    print("  - Обрезаться по краям (а не сжиматься)")