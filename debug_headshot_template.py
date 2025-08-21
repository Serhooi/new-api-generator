#!/usr/bin/env python3
"""
Отладка хедшота в шаблоне - что там на самом деле?
"""

import re

def debug_headshot_in_template():
    """Проверяем что в шаблоне с хедшотом"""
    print("🔍 ОТЛАДКА ХЕДШОТА В ШАБЛОНЕ")
    print("=" * 50)
    
    try:
        with open('main.svg', 'r') as f:
            svg_content = f.read()
        
        print(f"📊 Размер файла: {len(svg_content)} символов")
        
        # 1. Ищем элемент хедшота
        headshot_match = re.search(r'<rect[^>]*id="dyno\.agentheadshot"[^>]*>', svg_content)
        if headshot_match:
            print(f"✅ Найден элемент хедшота:")
            print(f"   {headshot_match.group(0)}")
            
            # Извлекаем pattern ID
            pattern_match = re.search(r'fill="url\(#([^)]+)\)"', headshot_match.group(0))
            if pattern_match:
                pattern_id = pattern_match.group(1)
                print(f"✅ Использует pattern: {pattern_id}")
                
                # 2. Ищем pattern
                pattern_pattern = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
                pattern_content_match = re.search(pattern_pattern, svg_content, re.DOTALL)
                if pattern_content_match:
                    pattern_content = pattern_content_match.group(1)
                    print(f"✅ Найден pattern:")
                    print(f"   {pattern_content[:200]}...")
                    
                    # 3. Ищем use элемент в pattern
                    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
                    if use_match:
                        image_id = use_match.group(1)
                        print(f"✅ Pattern использует image: {image_id}")
                        
                        # 4. Ищем image элемент
                        image_pattern = rf'<image[^>]*id="{re.escape(image_id)}"[^>]*>'
                        image_match = re.search(image_pattern, svg_content)
                        if image_match:
                            image_element = image_match.group(0)
                            print(f"✅ Найден image элемент:")
                            print(f"   {image_element[:200]}...")
                            
                            # Проверяем href
                            href_match = re.search(r'(?:xlink:href|href)="([^"]*)"', image_element)
                            if href_match:
                                href = href_match.group(1)
                                if href.startswith('data:image'):
                                    print(f"✅ Image содержит base64 данные ({len(href)} символов)")
                                    print(f"   Тип: {href[:50]}...")
                                elif href.startswith('http'):
                                    print(f"✅ Image содержит URL: {href}")
                                else:
                                    print(f"⚠️ Image содержит: {href[:100]}...")
                            else:
                                print(f"❌ href не найден в image элементе")
                        else:
                            print(f"❌ Image элемент {image_id} не найден")
                    else:
                        print(f"❌ use элемент не найден в pattern")
                else:
                    print(f"❌ Pattern {pattern_id} не найден")
            else:
                print(f"❌ Pattern ID не найден в элементе хедшота")
        else:
            print(f"❌ Элемент dyno.agentheadshot не найден")
            
    except FileNotFoundError:
        print("❌ Файл main.svg не найден")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    debug_headshot_in_template()