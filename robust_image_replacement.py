#!/usr/bin/env python3
"""
Устойчивая система замены изображений с fallback'ами и обработкой ошибок.
"""

import re
import requests
import base64
from PIL import Image
import io
import time

def create_placeholder_image(width=142, height=56, color='#4F46E5', text='LOGO'):
    """Создает placeholder изображение локально"""
    try:
        from PIL import ImageDraw, ImageFont
        
        # Создаем изображение
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        
        # Пытаемся использовать системный шрифт
        try:
            # Для macOS
            font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 20)
        except:
            try:
                # Для Linux
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
            except:
                # Fallback на стандартный шрифт
                font = ImageFont.load_default()
        
        # Вычисляем позицию текста по центру
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Рисуем текст
        draw.text((x, y), text, fill='white', font=font)
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"⚠️ Ошибка создания placeholder: {e}")
        return None

def download_and_convert_image(url, timeout=10, retries=3):
    """Скачивает изображение по URL с повторными попытками"""
    
    # Список альтернативных сервисов placeholder'ов
    placeholder_alternatives = [
        'https://picsum.photos/142/56',  # Lorem Picsum
        'https://dummyimage.com/142x56/4F46E5/FFFFFF&text=LOGO',  # DummyImage
        'https://fakeimg.pl/142x56/4F46E5/FFFFFF/?text=LOGO'  # FakeImg
    ]
    
    urls_to_try = [url]
    
    # Если это via.placeholder.com, добавляем альтернативы
    if 'via.placeholder.com' in url:
        print(f"🔄 via.placeholder.com недоступен, пробую альтернативы...")
        urls_to_try.extend(placeholder_alternatives)
    
    for attempt_url in urls_to_try:
        for attempt in range(retries):
            try:
                print(f"📥 Попытка {attempt + 1}/{retries}: {attempt_url}")
                
                response = requests.get(attempt_url, timeout=timeout, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                # Открываем изображение
                img = Image.open(io.BytesIO(response.content))
                
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Сохраняем в буфер как JPEG
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                buffer.seek(0)
                
                # Кодируем в base64
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                base64_url = f"data:image/jpeg;base64,{img_base64}"
                
                print(f"✅ Изображение скачано и конвертировано ({len(base64_url)} символов)")
                return base64_url
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка сети (попытка {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(1)  # Пауза перед повтором
                continue
            except Exception as e:
                print(f"❌ Ошибка обработки изображения: {e}")
                break
    
    # Если все попытки неудачны, создаем placeholder локально
    print(f"🎨 Создаю placeholder изображение локально...")
    if 'placeholder' in url.lower() or 'logo' in url.lower():
        return create_placeholder_image()
    
    return None

def replace_image_url_in_svg_robust(svg_content, field_name, new_image_url):
    """
    Устойчивая замена изображений с обработкой ошибок
    """
    print(f"🖼️ Обрабатываю изображение: {field_name}")
    
    # Сначала ищем элемент с id равным field_name (прямое соответствие)
    direct_element_regex = rf'(<[^>]*id="{re.escape(field_name)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    direct_match = re.search(direct_element_regex, svg_content)
    
    if direct_match:
        print(f"✅ Найден прямой элемент с id: {field_name}")
        # Прямая замена URL
        new_svg_content = re.sub(direct_element_regex, 
                                lambda m: m.group(1) + new_image_url + m.group(2), 
                                svg_content)
        
        if new_svg_content != svg_content:
            print(f"✅ Изображение {field_name} заменено на: {new_image_url[:50]}...")
            return new_svg_content
    
    # Если прямого элемента нет, ищем через pattern
    print(f"🔍 Ищу через pattern для поля: {field_name}")
    
    # Ищем элемент с id содержащим field_name и fill="url(#pattern_id)"
    element_regex = rf'<[^>]*id="[^"]*{re.escape(field_name)}[^"]*"[^>]*fill="url\(#([^)]+)\)"[^>]*>'
    element_match = re.search(element_regex, svg_content, re.IGNORECASE)
    
    if not element_match:
        print(f"❌ Элемент с id содержащим {field_name} не найден")
        return svg_content
    
    pattern_id = element_match.group(1)
    print(f"✅ Найден pattern: {pattern_id}")
    
    # Ищем pattern с этим ID
    pattern_regex = rf'<pattern[^>]*id="{re.escape(pattern_id)}"[^>]*>(.*?)</pattern>'
    pattern_match = re.search(pattern_regex, svg_content, re.DOTALL)
    
    if not pattern_match:
        print(f"❌ Pattern с ID {pattern_id} не найден")
        return svg_content
    
    pattern_content = pattern_match.group(1)
    
    # Ищем use элемент в pattern
    use_match = re.search(r'<use[^>]*xlink:href="#([^"]+)"[^>]*/?>', pattern_content)
    if not use_match:
        print(f"❌ Use элемент не найден в pattern {pattern_id}")
        return svg_content
    
    image_id = use_match.group(1)
    print(f"✅ Найден image ID: {image_id}")
    
    # Определяем что делать с изображением
    if new_image_url.startswith('http'):
        # Пытаемся скачать и конвертировать
        replacement_url = download_and_convert_image(new_image_url)
        if not replacement_url:
            print(f"⚠️ Не удалось обработать изображение, использую исходный URL")
            replacement_url = new_image_url
    else:
        # Если это уже base64 или локальный файл
        replacement_url = new_image_url
    
    # Ищем и заменяем image элемент с этим ID
    image_regex = rf'(<image[^>]*id="{re.escape(image_id)}"[^>]*(?:xlink:href|href)=")[^"]*("[^>]*>)'
    
    def replace_image_href(match):
        return match.group(1) + replacement_url + match.group(2)
    
    new_svg_content = re.sub(image_regex, replace_image_href, svg_content)
    
    if new_svg_content != svg_content:
        print(f"✅ Изображение {field_name} заменено!")
        return new_svg_content
    else:
        print(f"❌ Изображение {field_name} не было заменено")
        return svg_content

def test_robust_replacement():
    """Тестируем устойчивую замену изображений"""
    
    print("🛡️ ТЕСТ УСТОЙЧИВОЙ ЗАМЕНЫ ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    
    # Читаем SVG файл
    try:
        with open('main.svg', 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except FileNotFoundError:
        print("❌ Файл main.svg не найден")
        return
    
    print(f"📄 Размер SVG файла: {len(svg_content)} символов")
    
    # Тестовые данные с проблемными URL
    test_data = {
        'dyno.logo': 'https://via.placeholder.com/142x56/4F46E5/FFFFFF?text=LOGO',  # Проблемный URL
        'dyno.propertyimage': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400&h=300',  # Рабочий URL
    }
    
    # Заменяем изображения
    modified_svg = svg_content
    
    for field_name, image_url in test_data.items():
        print(f"\n🔄 Тестирую: {field_name} = {image_url}")
        
        original_size = len(modified_svg)
        modified_svg = replace_image_url_in_svg_robust(modified_svg, field_name, image_url)
        new_size = len(modified_svg)
        
        if new_size != original_size:
            print(f"📊 Изменение размера: {new_size - original_size:+d} символов")
        
        print("-" * 40)
    
    # Сохраняем результат
    output_file = 'main_robust_replacement.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_svg)
    
    print(f"\n✅ Результат сохранен в: {output_file}")

if __name__ == "__main__":
    test_robust_replacement()