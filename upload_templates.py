#!/usr/bin/env python3
"""
Скрипт для загрузки SVG шаблонов в базу данных
"""

import sqlite3
import uuid
import os
import re

DATABASE_PATH = 'templates.db'

def extract_dyno_fields(svg_content):
    """Извлекает dyno поля из SVG"""
    fields = set()
    
    patterns = [
        r'id="(dyno\.[^"]*)"',        # id="dyno.field"
        r"id='(dyno\.[^']*)'",        # id='dyno.field'
        r'\{\{(dyno\.[^}]+)\}\}',     # {{dyno.field}}
        r'\{(dyno\.[^}]+)\}',         # {dyno.field}
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, svg_content)
        fields.update(matches)
    
    return sorted(list(fields))

def upload_template(svg_file_path, template_name, template_role):
    """Загружает SVG шаблон в базу данных"""
    
    if not os.path.exists(svg_file_path):
        print(f"❌ Файл не найден: {svg_file_path}")
        return None
    
    # Читаем SVG файл
    with open(svg_file_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Извлекаем dyno поля
    dyno_fields = extract_dyno_fields(svg_content)
    
    print(f"📄 Загружаю шаблон: {template_name}")
    print(f"   Файл: {svg_file_path}")
    print(f"   Роль: {template_role}")
    print(f"   Найдено dyno полей: {len(dyno_fields)}")
    
    for field in dyno_fields:
        print(f"      - {field}")
    
    # Сохраняем в базу данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    template_id = str(uuid.uuid4())
    
    cursor.execute('''
        INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [template_id, template_name, 'uploaded', template_role, svg_content, ','.join(dyno_fields)])
    
    conn.commit()
    conn.close()
    
    print(f"✅ Шаблон загружен с ID: {template_id}")
    return template_id

def upload_templates_interactive():
    """Интерактивная загрузка шаблонов"""
    
    print("📤 ЗАГРУЗКА SVG ШАБЛОНОВ")
    print("=" * 50)
    
    # Проверяем текущую директорию на наличие SVG файлов
    svg_files = [f for f in os.listdir('.') if f.endswith('.svg')]
    
    if svg_files:
        print(f"🔍 Найдены SVG файлы в текущей директории:")
        for i, file in enumerate(svg_files, 1):
            print(f"   {i}. {file}")
        print()
    
    templates = []
    
    # Загружаем main шаблон
    print("1️⃣ MAIN ШАБЛОН")
    main_path = input("Введите путь к main SVG файлу (или просто имя файла): ").strip()
    
    if main_path and os.path.exists(main_path):
        main_name = input("Введите название main шаблона: ").strip() or "Main Template"
        main_id = upload_template(main_path, main_name, 'main')
        if main_id:
            templates.append(('main', main_id, main_name))
    else:
        print(f"❌ Main шаблон не загружен")
    
    print()
    
    # Загружаем photo шаблон
    print("2️⃣ PHOTO ШАБЛОН")
    photo_path = input("Введите путь к photo SVG файлу (или просто имя файла): ").strip()
    
    if photo_path and os.path.exists(photo_path):
        photo_name = input("Введите название photo шаблона: ").strip() or "Photo Template"
        photo_id = upload_template(photo_path, photo_name, 'photo')
        if photo_id:
            templates.append(('photo', photo_id, photo_name))
    else:
        print(f"❌ Photo шаблон не загружен")
    
    # Создаем карусель если загружены оба шаблона
    if len(templates) == 2:
        print(f"\n🎠 Создаю карусель...")
        
        main_id = next(t[1] for t in templates if t[0] == 'main')
        photo_id = next(t[1] for t in templates if t[0] == 'photo')
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        carousel_id = str(uuid.uuid4())
        carousel_name = input("Введите название карусели: ").strip() or "Uploaded Carousel"
        
        cursor.execute('''
            INSERT INTO carousels (id, name, main_template_id, photo_template_id)
            VALUES (?, ?, ?, ?)
        ''', [carousel_id, carousel_name, main_id, photo_id])
        
        conn.commit()
        conn.close()
        
        print(f"✅ Карусель создана: {carousel_name} ({carousel_id})")
    
    print(f"\n📊 ИТОГО ЗАГРУЖЕНО:")
    for role, template_id, name in templates:
        print(f"   {role.upper()}: {name} ({template_id})")
    
    return templates

def quick_upload():
    """Быстрая загрузка если файлы называются стандартно"""
    
    print("⚡ БЫСТРАЯ ЗАГРУЗКА")
    print("=" * 30)
    
    # Ищем файлы по стандартным именам
    main_files = ['main.svg', 'main_template.svg', 'template_main.svg']
    photo_files = ['photo.svg', 'photo_template.svg', 'template_photo.svg']
    
    main_path = None
    photo_path = None
    
    for file in main_files:
        if os.path.exists(file):
            main_path = file
            break
    
    for file in photo_files:
        if os.path.exists(file):
            photo_path = file
            break
    
    templates = []
    
    if main_path:
        print(f"📄 Найден main шаблон: {main_path}")
        main_id = upload_template(main_path, "Main Template", 'main')
        if main_id:
            templates.append(('main', main_id, "Main Template"))
    
    if photo_path:
        print(f"📄 Найден photo шаблон: {photo_path}")
        photo_id = upload_template(photo_path, "Photo Template", 'photo')
        if photo_id:
            templates.append(('photo', photo_id, "Photo Template"))
    
    if len(templates) == 2:
        # Создаем карусель
        main_id = next(t[1] for t in templates if t[0] == 'main')
        photo_id = next(t[1] for t in templates if t[0] == 'photo')
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        carousel_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO carousels (id, name, main_template_id, photo_template_id)
            VALUES (?, ?, ?, ?)
        ''', [carousel_id, "Quick Upload Carousel", main_id, photo_id])
        
        conn.commit()
        conn.close()
        
        print(f"✅ Карусель создана: {carousel_id}")
    
    return templates

if __name__ == "__main__":
    print("Выберите способ загрузки:")
    print("1. Интерактивная загрузка")
    print("2. Быстрая загрузка (ищет main.svg и photo.svg)")
    
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    if choice == "2":
        quick_upload()
    else:
        upload_templates_interactive()