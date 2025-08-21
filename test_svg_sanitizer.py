#!/usr/bin/env python3
"""
Тест санитайзера SVG - проверяем исправление проблем с <image> тегами
"""

import re
import xml.etree.ElementTree as ET

def sanitize_svg(svg: str) -> str:
    """
    Санитайзер SVG - исправляет проблемы с <image> тегами
    """
    print("🛡️ Санитизирую SVG...")
    
    # 1) Убираем лишние переводы строк и пробелы внутри data:base64
    def _clean_data_uri(m):
        full_match = m.group(0)
        # убираем все пробелы/переводы строк из data: URI
        cleaned = re.sub(r'\s+', '', full_match)
        return cleaned
    
    svg = re.sub(r'(?:href|xlink:href)=(["\'])\s*(data:image/[^;]+;base64,[^"\']+)\1',
                 _clean_data_uri, svg)
    
    # 2) Экранируем & в URL (НЕ в data:base64!)
    def _escape_url_entities(m):
        quote = m.group(1)
        url = m.group(2)
        if url.startswith('data:'):
            return m.group(0)  # не трогаем data:
        # экранируем амперсанды
        url = url.replace('&', '&amp;')
        # если есть кавычки — заменим на %22/%27
        url = url.replace('"', '%22').replace("'", '%27')
        return f'href={quote}{url}{quote}'
    
    svg = re.sub(r'href=(["\'])([^"\']+)\1', _escape_url_entities, svg)
    svg = re.sub(r'xlink:href=(["\'])([^"\']+)\1', _escape_url_entities, svg)
    
    # 3) Следим, чтобы <image ...> был самозакрывающимся (/>) 
    def _ensure_self_closed(m):
        tag = m.group(0)
        if tag.endswith('/>'):
            return tag
        return tag[:-1] + ' />'
    
    svg = re.sub(r'<image\b[^>]*?(?<!/)>', _ensure_self_closed, svg)
    
    # 4) То же для <use> тегов
    svg = re.sub(r'<use\b[^>]*?(?<!/)>', _ensure_self_closed, svg)
    
    print("✅ SVG санитизирован")
    return svg

def validate_xml(svg: str) -> bool:
    """
    Валидирует XML и выводит диагностику ошибок
    """
    try:
        ET.fromstring(svg)
        print("✅ XML валидация прошла успешно")
        return True
    except ET.ParseError as e:
        print(f"❌ XML parse error: {e}")
        
        # Пытаемся найти проблемное место
        msg = str(e)
        if 'line' in msg and 'column' in msg:
            # Извлекаем номер колонки из сообщения
            col_match = re.search(r'column (\d+)', msg)
            if col_match:
                col = int(col_match.group(1))
                start = max(0, col - 120)
                end = min(len(svg), col + 120)
                snippet = svg[start:end]
                print("\n=== XML ERROR CONTEXT ===")
                print(f"Позиция: колонка {col}")
                print(f"Контекст: ...{snippet}...")
                print("=" * 50)
        
        return False
    except Exception as e:
        print(f"❌ Другая ошибка валидации: {e}")
        return False

def test_svg_sanitizer():
    """Тестируем санитайзер SVG"""
    print("🧪 ТЕСТ САНИТАЙЗЕРА SVG")
    print("=" * 50)
    
    # Тестовые случаи с проблемами
    test_cases = [
        {
            'name': 'Незакрытый image тег',
            'svg': '<svg><image href="test.jpg" width="100" height="100"></svg>',
            'expected_fix': 'Должен стать самозакрывающимся'
        },
        {
            'name': 'Неэкранированный & в URL',
            'svg': '<svg><image href="http://example.com?a=1&b=2" width="100" height="100"/></svg>',
            'expected_fix': 'Амперсанд должен стать &amp;'
        },
        {
            'name': 'Пробелы в base64',
            'svg': '<svg><image href="data:image/png;base64,iVBOR w0KGgoA\nAANSUhEUgAA" width="100" height="100"/></svg>',
            'expected_fix': 'Пробелы и переводы строк должны быть убраны'
        },
        {
            'name': 'Кавычки в URL',
            'svg': '<svg><image href="http://example.com/test"quote".jpg" width="100" height="100"/></svg>',
            'expected_fix': 'Кавычки должны стать %22'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Тест: {test_case['name']}")
        print(f"   Исходный SVG: {test_case['svg'][:80]}...")
        print(f"   Ожидание: {test_case['expected_fix']}")
        
        # Проверяем валидность до санитизации
        print("   До санитизации:", end=" ")
        valid_before = validate_xml(test_case['svg'])
        
        # Применяем санитайзер
        sanitized = sanitize_svg(test_case['svg'])
        print(f"   Санитизированный: {sanitized[:80]}...")
        
        # Проверяем валидность после санитизации
        print("   После санитизации:", end=" ")
        valid_after = validate_xml(sanitized)
        
        if valid_after and not valid_before:
            print("   ✅ ИСПРАВЛЕНО!")
        elif valid_after and valid_before:
            print("   ✅ Остался валидным")
        else:
            print("   ❌ НЕ ИСПРАВЛЕНО")

if __name__ == "__main__":
    test_svg_sanitizer()