#!/usr/bin/env python3
"""
Тест headshot замены
"""

import re

def test_headshot_replacement():
    """Тестируем замену headshot"""
    
    # Тестовый SVG с headshot (как в реальности)
    test_svg = '''<svg>
    <g id="dyno.agentheadshot">
        <rect width="100" height="100" fill="url(#pattern1)"/>
    </g>
    <defs>
        <pattern id="pattern1">
            <use xlink:href="#image1"/>
        </pattern>
        <image id="image1" href="old-headshot.jpg" xlink:href="old-headshot.jpg"/>
    </defs>
    </svg>'''
    
    print("🔍 Исходный SVG:")
    print(test_svg)
    print("\n" + "="*50)
    
    # Тестируем замену headshot
    new_headshot_url = "https://example.com/new-headshot.jpg"
    
    # Ищем элемент с id="dyno.agentheadshot"
    element_pattern = r'<g[^>]*id="dyno\.agentheadshot"[^>]*>.*?</g>'
    match = re.search(element_pattern, test_svg, re.DOTALL)
    
    if match:
        print(f"✅ Найден элемент headshot: {match.group(0)}")
        
        # Ищем pattern в fill атрибуте
        fill_pattern = r'fill="url\(#([^)]+)\)"'
        fill_match = re.search(fill_pattern, match.group(0))
        
        if fill_match:
            pattern_id = fill_match.group(1)
            print(f"✅ Найден pattern: {pattern_id}")
            
            # Ищем pattern блок
            pattern_block_pattern = f'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
            pattern_match = re.search(pattern_block_pattern, test_svg, re.DOTALL)
            
            if pattern_match:
                pattern_content = pattern_match.group(1)
                print(f"✅ Найден pattern блок: {pattern_content}")
                
                # Ищем use элемент внутри pattern
                use_pattern = r'<use[^>]*xlink:href="#([^"]*)"[^>]*/?>'
                use_match = re.search(use_pattern, pattern_content)
                
                if use_match:
                    image_id = use_match.group(1)
                    print(f"✅ Найден use элемент: #{image_id}")
                    
                    # Ищем соответствующий image элемент
                    image_pattern = f'<image[^>]*id="{re.escape(image_id)}"[^>]*/?>'
                    image_match = re.search(image_pattern, test_svg)
                    
                    if image_match:
                        old_image = image_match.group(0)
                        print(f"✅ Найден image элемент: {old_image}")
                        
                        # Заменяем URL
                        new_image = old_image
                        new_image = re.sub(r'href="[^"]*"', f'href="{new_headshot_url}"', new_image)
                        new_image = re.sub(r'xlink:href="[^"]*"', f'xlink:href="{new_headshot_url}"', new_image)
                        
                        print(f"🔄 Заменяем: {old_image}")
                        print(f"🔄 На: {new_image}")
                        
                        # Применяем замену
                        new_svg = test_svg.replace(old_image, new_image)
                        
                        print("\n" + "="*50)
                        print("✅ Результат замены:")
                        print(new_svg)
                        
                        # Проверяем, что замена произошла
                        if new_headshot_url in new_svg:
                            print("\n🎉 HEADSHOT ЗАМЕНЕН УСПЕШНО!")
                            return True
                        else:
                            print("\n❌ Headshot НЕ заменен!")
                            return False
                    else:
                        print("❌ Image элемент не найден")
                        return False
                else:
                    print("❌ Use элемент не найден в pattern")
                    return False
            else:
                print("❌ Pattern блок не найден")
                return False
        else:
            print("❌ Fill с pattern не найден")
            return False
    else:
        print("❌ Элемент headshot не найден")
        return False

if __name__ == "__main__":
    print("🧪 ТЕСТ HEADSHOT ЗАМЕНЫ")
    print("="*50)
    
    success = test_headshot_replacement()
    
    if success:
        print("\n🎯 ВСЕ РАБОТАЕТ! Headshot заменяется корректно!")
    else:
        print("\n💥 ЕСТЬ ПРОБЛЕМЫ! Headshot НЕ заменяется!")