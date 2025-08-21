#!/usr/bin/env python3
"""
Отладка проблемы с headshot на превью
"""

import requests
import re

def debug_headshot_on_preview():
    """Отлаживаем проблему с headshot"""
    
    print("🔍 ОТЛАДКА HEADSHOT НА ПРЕВЬЮ")
    print("=" * 35)
    
    # Получаем реальный SVG с API
    api_url = "https://new-api-generator.onrender.com/api/generate/carousel"
    
    test_data = {
        "main_template_id": "9cb08943-8d1e-440c-a712-92111ec23048",
        "photo_template_id": "f6ed8d52-3bbf-495e-8b67-61dc7d4ff47d", 
        "data": {
            "propertyaddress": "Debug Headshot Test",
            "price": "$999,999",
            "beds": "3",
            "baths": "2",
            "name": "Test Agent",
            "phone": "+1 555 123 4567",
            "email": "test@agent.com",
            "agentheadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
            "propertyimage2": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800"
        }
    }
    
    try:
        print("📡 Отправляю запрос с headshot...")
        response = requests.post(api_url, json=test_data, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ API ошибка: {response.status_code}")
            return
        
        result = response.json()
        
        if not result.get('success'):
            print("❌ API вернул success: false")
            return
        
        # Получаем main SVG
        main_svg_url = result['urls'][0]
        print(f"📥 Загружаю main SVG: {main_svg_url}")
        
        svg_response = requests.get(main_svg_url, timeout=10)
        svg_content = svg_response.text
        
        print(f"📊 SVG размер: {len(svg_content)} символов")
        
        # Анализируем headshot в SVG
        print("\n🔍 АНАЛИЗ HEADSHOT В SVG:")
        
        # Ищем все упоминания headshot
        headshot_mentions = re.findall(r'[^>]*headshot[^<]*', svg_content, re.IGNORECASE)
        print(f"📋 Упоминаний 'headshot': {len(headshot_mentions)}")
        
        for i, mention in enumerate(headshot_mentions[:3]):
            print(f"  {i+1}: {mention[:100]}...")
        
        # Ищем все упоминания agent
        agent_mentions = re.findall(r'[^>]*agent[^<]*', svg_content, re.IGNORECASE)
        print(f"📋 Упоминаний 'agent': {len(agent_mentions)}")
        
        for i, mention in enumerate(agent_mentions[:3]):
            print(f"  {i+1}: {mention[:100]}...")
        
        # Ищем image теги с headshot или agent
        image_tags = re.findall(r'<image[^>]*(?:headshot|agent)[^>]*>', svg_content, re.IGNORECASE)
        print(f"📋 Image тегов с headshot/agent: {len(image_tags)}")
        
        for i, tag in enumerate(image_tags):
            print(f"  {i+1}: {tag[:150]}...")
            
            # Проверяем есть ли href
            if 'href=' in tag:
                href_match = re.search(r'href="([^"]*)"', tag)
                if href_match:
                    href = href_match.group(1)
                    if href.startswith('data:image'):
                        print(f"    ✅ Содержит base64 данные ({len(href)} символов)")
                    elif href.startswith('http'):
                        print(f"    ✅ Содержит URL: {href[:50]}...")
                    else:
                        print(f"    ⚠️ Неизвестный href: {href[:50]}...")
                else:
                    print(f"    ❌ Нет href в теге")
            else:
                print(f"    ❌ Нет href атрибута")
        
        # Ищем pattern элементы с headshot
        pattern_tags = re.findall(r'<pattern[^>]*>[^<]*<use[^>]*(?:headshot|agent)[^>]*>', svg_content, re.IGNORECASE)
        print(f"📋 Pattern тегов с headshot/agent: {len(pattern_tags)}")
        
        # Проверяем есть ли вообще изображения в SVG
        all_images = re.findall(r'<image[^>]*>', svg_content)
        print(f"📋 Всего image тегов: {len(all_images)}")
        
        base64_images = len(re.findall(r'data:image/[^;]+;base64,', svg_content))
        print(f"📋 Base64 изображений: {base64_images}")
        
        url_images = len(re.findall(r'https?://[^"\'>\s]+\.(jpg|jpeg|png|gif)', svg_content))
        print(f"📋 URL изображений: {url_images}")
        
        # Сохраняем для анализа
        with open('debug_headshot_svg.svg', 'w') as f:
            f.write(svg_content)
        
        print("💾 SVG сохранен: debug_headshot_svg.svg")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def analyze_headshot_in_template():
    """Анализируем headshot в оригинальном шаблоне"""
    
    print("\n🔍 АНАЛИЗ HEADSHOT В ОРИГИНАЛЬНОМ ШАБЛОНЕ")
    print("=" * 45)
    
    # Читаем оригинальный main.svg
    with open('main.svg', 'r') as f:
        template_content = f.read()
    
    print(f"📊 Размер шаблона: {len(template_content)} символов")
    
    # Ищем headshot элементы
    headshot_elements = re.findall(r'[^>]*headshot[^<]*', template_content, re.IGNORECASE)
    print(f"📋 Headshot элементов в шаблоне: {len(headshot_elements)}")
    
    for i, element in enumerate(headshot_elements):
        print(f"  {i+1}: {element[:100]}...")
    
    # Ищем agent элементы
    agent_elements = re.findall(r'[^>]*agent[^<]*', template_content, re.IGNORECASE)
    print(f"📋 Agent элементов в шаблоне: {len(agent_elements)}")
    
    for i, element in enumerate(agent_elements):
        print(f"  {i+1}: {element[:100]}...")

if __name__ == "__main__":
    # Анализируем оригинальный шаблон
    analyze_headshot_in_template()
    
    # Анализируем результат API
    debug_headshot_on_preview()