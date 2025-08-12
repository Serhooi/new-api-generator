#!/usr/bin/env python3
"""
Создание тестовых шаблонов с правильными dyno полями
"""

import sqlite3
import uuid

DATABASE_PATH = 'templates.db'

def create_test_templates():
    """Создает тестовые шаблоны с правильными dyno полями"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Main template SVG с dyno.propertyimage
    main_svg = '''<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="propertyImagePattern" patternUnits="objectBoundingBox" width="1" height="1">
                <image id="propertyImageElement" href="placeholder.jpg" width="1080" height="600" preserveAspectRatio="xMidYMid slice"/>
            </pattern>
            <pattern id="agentHeadshotPattern" patternUnits="objectBoundingBox" width="1" height="1">
                <image id="agentHeadshotElement" href="placeholder.jpg" width="200" height="200" preserveAspectRatio="xMidYMid slice"/>
            </pattern>
        </defs>
        
        <!-- Property Image -->
        <rect id="dyno.propertyimage" x="0" y="0" width="1080" height="600" fill="url(#propertyImagePattern)"/>
        
        <!-- Agent Headshot -->
        <circle id="dyno.agentheadshot" cx="900" cy="500" r="80" fill="url(#agentHeadshotPattern)"/>
        
        <!-- Text Fields -->
        <text id="dyno.propertyaddress" x="50" y="700" font-size="32" fill="white">
            <tspan x="50" y="700">Property Address</tspan>
        </text>
        <text id="dyno.price" x="50" y="750" font-size="28" fill="white">
            <tspan x="50" y="750">$450,000</tspan>
        </text>
        <text id="dyno.name" x="50" y="800" font-size="24" fill="white">
            <tspan x="50" y="800">Agent Name</tspan>
        </text>
        <text id="dyno.phone" x="50" y="850" font-size="20" fill="white">
            <tspan x="50" y="850">(555) 123-4567</tspan>
        </text>
    </svg>'''
    
    # Photo template SVG с dyno.propertyimage2
    photo_svg = '''<svg width="1080" height="1080" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="propertyImage2Pattern" patternUnits="objectBoundingBox" width="1" height="1">
                <image id="propertyImage2Element" href="placeholder.jpg" width="1080" height="800" preserveAspectRatio="xMidYMid slice"/>
            </pattern>
            <pattern id="agentHeadshotPattern2" patternUnits="objectBoundingBox" width="1" height="1">
                <image id="agentHeadshotElement2" href="placeholder.jpg" width="200" height="200" preserveAspectRatio="xMidYMid slice"/>
            </pattern>
        </defs>
        
        <!-- Property Image 2 -->
        <rect id="dyno.propertyimage2" x="0" y="0" width="1080" height="800" fill="url(#propertyImage2Pattern)"/>
        
        <!-- Agent Headshot -->
        <circle id="dyno.agentheadshot" cx="900" cy="900" r="80" fill="url(#agentHeadshotPattern2)"/>
        
        <!-- Text Fields -->
        <text id="dyno.propertyaddress" x="50" y="950" font-size="32" fill="white">
            <tspan x="50" y="950">Property Address</tspan>
        </text>
        <text id="dyno.name" x="50" y="1000" font-size="24" fill="white">
            <tspan x="50" y="1000">Agent Name</tspan>
        </text>
        <text id="dyno.phone" x="50" y="1050" font-size="20" fill="white">
            <tspan x="50" y="1050">(555) 123-4567</tspan>
        </text>
    </svg>'''
    
    # Создаем main template
    main_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [main_id, 'Test Main Template', 'test', 'main', main_svg, 'dyno.propertyimage,dyno.agentheadshot,dyno.propertyaddress,dyno.price,dyno.name,dyno.phone'])
    
    # Создаем photo template
    photo_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO templates (id, name, category, template_role, svg_content, dyno_fields)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', [photo_id, 'Test Photo Template', 'test', 'photo', photo_svg, 'dyno.propertyimage2,dyno.agentheadshot,dyno.propertyaddress,dyno.name,dyno.phone'])
    
    # Создаем карусель
    carousel_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO carousels (id, name, main_template_id, photo_template_id)
        VALUES (?, ?, ?, ?)
    ''', [carousel_id, 'Test Carousel', main_id, photo_id])
    
    conn.commit()
    conn.close()
    
    print(f"✅ Созданы тестовые шаблоны:")
    print(f"   📄 Main template: {main_id}")
    print(f"   📄 Photo template: {photo_id}")
    print(f"   🎠 Carousel: {carousel_id}")
    
    return main_id, photo_id, carousel_id

if __name__ == "__main__":
    create_test_templates()