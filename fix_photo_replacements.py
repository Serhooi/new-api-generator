#!/usr/bin/env python3
"""
Исправляем проблему с photo replacements в app.py
"""

def fix_photo_replacements():
    """Исправляем app.py чтобы photo превью не использовало dyno.propertyimage"""
    
    print("🔧 Исправляю photo replacements в app.py...")
    
    # Читаем app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим и заменяем первое вхождение (в функции preview_carousel)
    old_pattern1 = """        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        photo_preview = create_preview_with_data(photo_svg, replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,"""
    
    new_pattern1 = """        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        
        # Для photo превью создаем отдельные replacements только с нужными полями
        photo_replacements = {}
        for key, value in replacements.items():
            # Исключаем dyno.propertyimage (это для main слайда)
            if key != 'dyno.propertyimage':
                photo_replacements[key] = value
        
        print(f"🔍 Photo превью replacements: {list(photo_replacements.keys())}")
        photo_preview = create_preview_with_data(photo_svg, photo_replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,"""
    
    # Заменяем первое вхождение
    if old_pattern1 in content:
        content = content.replace(old_pattern1, new_pattern1, 1)
        print("✅ Первое вхождение исправлено (preview_carousel)")
    else:
        print("❌ Первое вхождение не найдено")
    
    # Находим и заменяем второе вхождение
    old_pattern2 = """        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        photo_preview = create_preview_with_data(photo_svg, replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,
                **main_preview
            },
            'photo_preview': {
                'template_name': photo_name,
                'template_id': photo_template_id,
                **photo_preview
            }
        })"""
    
    new_pattern2 = """        # Генерируем превью для обоих шаблонов
        main_preview = create_preview_with_data(main_svg, replacements, preview_type)
        
        # Для photo превью создаем отдельные replacements только с нужными полями
        photo_replacements = {}
        for key, value in replacements.items():
            # Исключаем dyno.propertyimage (это для main слайда)
            if key != 'dyno.propertyimage':
                photo_replacements[key] = value
        
        print(f"🔍 Photo превью replacements: {list(photo_replacements.keys())}")
        photo_preview = create_preview_with_data(photo_svg, photo_replacements, preview_type)
        
        return jsonify({
            'success': True,
            'main_preview': {
                'template_name': main_name,
                'template_id': main_template_id,
                **main_preview
            },
            'photo_preview': {
                'template_name': photo_name,
                'template_id': photo_template_id,
                **photo_preview
            }
        })"""
    
    # Заменяем второе вхождение
    if old_pattern2 in content:
        content = content.replace(old_pattern2, new_pattern2, 1)
        print("✅ Второе вхождение исправлено")
    else:
        print("❌ Второе вхождение не найдено")
    
    # Сохраняем исправленный файл
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py исправлен!")

if __name__ == "__main__":
    fix_photo_replacements()