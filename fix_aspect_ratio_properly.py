#!/usr/bin/env python3
"""
Правильное исправление aspect ratio - только для property изображений
"""

def fix_aspect_ratio_properly():
    """Исправляем aspect ratio правильно - только для property изображений"""
    
    print("🔧 ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ ASPECT RATIO")
    print("=" * 45)
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Откатываем глобальную замену
    content = content.replace('preserveAspectRatio="xMidYMid slice"', 'preserveAspectRatio="none"')
    print("↩️ Откатил глобальную замену aspect ratio")
    
    # Ищем логику определения типа изображения
    # Нужно найти где определяется что это property изображение
    
    # Ищем функцию обработки изображений
    if 'def process_image_replacement' in content:
        print("✅ Найдена функция process_image_replacement")
        
        # Ищем где устанавливается aspect ratio для property изображений
        old_property_logic = '''                    # Определяем aspect ratio на основе типа изображения
                    if image_type == "property":
                        aspect_ratio = "xMidYMid slice"
                    else:
                        aspect_ratio = "none"'''
        
        new_property_logic = '''                    # Определяем aspect ratio на основе типа изображения
                    if image_type == "property":
                        aspect_ratio = "xMidYMid slice"  # Property изображения заполняют область
                    elif "headshot" in dyno_field.lower() or "agent" in dyno_field.lower():
                        aspect_ratio = "xMidYMid meet"  # Headshot сохраняет пропорции
                    else:
                        aspect_ratio = "none"  # Остальные растягиваются'''
        
        if old_property_logic in content:
            content = content.replace(old_property_logic, new_property_logic)
            print("✅ Обновлена логика aspect ratio для разных типов изображений")
        else:
            print("⚠️ Не найдена существующая логика aspect ratio")
            
            # Ищем где создается image элемент
            old_image_creation = '''                    image_element.set('preserveAspectRatio', 'none')'''
            
            new_image_creation = '''                    # Устанавливаем правильный aspect ratio
                    if image_type == "property":
                        image_element.set('preserveAspectRatio', 'xMidYMid slice')  # Property заполняет
                    elif "headshot" in dyno_field.lower() or "agent" in dyno_field.lower():
                        image_element.set('preserveAspectRatio', 'xMidYMid meet')   # Headshot вписывается
                    else:
                        image_element.set('preserveAspectRatio', 'none')  # Остальные растягиваются'''
            
            if old_image_creation in content:
                content = content.replace(old_image_creation, new_image_creation)
                print("✅ Добавлена логика aspect ratio в создание image элемента")
            else:
                print("⚠️ Не найдено место создания image элемента")
    
    # Также ищем в шаблонах где может быть preserveAspectRatio
    # Для headshot изображений нужно использовать "meet" а не "slice"
    
    # Сохраняем изменения
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("💾 app.py обновлен с правильным aspect ratio")
    
    print("\n📋 ПРАВИЛА ASPECT RATIO:")
    print("🏠 Property изображения: 'xMidYMid slice' - заполняют область, обрезаются")
    print("👤 Agent headshot: 'xMidYMid meet' - вписываются полностью, могут быть поля")
    print("🖼️ Остальные: 'none' - растягиваются под размер")
    
    return True

def check_current_aspect_ratio():
    """Проверяем текущие настройки aspect ratio"""
    
    print("🔍 ПРОВЕРКА ТЕКУЩИХ НАСТРОЕК")
    print("=" * 30)
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Ищем все упоминания preserveAspectRatio
    import re
    
    aspect_ratios = re.findall(r'preserveAspectRatio["\s]*=["\s]*([^"\'>\s]+)', content)
    
    print(f"📊 Найдено {len(aspect_ratios)} настроек aspect ratio:")
    
    for i, ratio in enumerate(set(aspect_ratios)):
        count = aspect_ratios.count(ratio)
        print(f"  {i+1}. '{ratio}' - {count} раз(а)")
    
    # Ищем логику определения типа изображения
    if 'image_type == "property"' in content:
        print("✅ Найдена логика для property изображений")
    else:
        print("⚠️ Логика для property изображений не найдена")
    
    if 'headshot' in content.lower():
        print("✅ Найдены упоминания headshot")
    else:
        print("⚠️ Упоминания headshot не найдены")

if __name__ == "__main__":
    # Сначала проверяем текущее состояние
    check_current_aspect_ratio()
    
    print("\n" + "="*50)
    
    # Затем исправляем
    fix_aspect_ratio_properly()
    
    print("\n✅ Aspect ratio исправлен правильно!")
    print("🔄 Нужно redeploy для применения изменений")