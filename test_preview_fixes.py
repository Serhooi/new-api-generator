#!/usr/bin/env python3
"""
ТЕСТ ИСПРАВЛЕНИЙ ПРЕВЬЮ
======================

Проверяем что все проблемы исправлены
"""

import requests
import json

def test_preview_api():
    """Тестируем API превью с исправлениями"""
    print("🧪 ТЕСТ API ПРЕВЬЮ С ИСПРАВЛЕНИЯМИ")
    print("=" * 50)
    
    # URL API (замените на ваш)
    api_url = "http://localhost:5000"
    
    # Сначала получаем список шаблонов
    print("1. Получаю список шаблонов...")
    try:
        response = requests.get(f"{api_url}/api/templates/all-previews")
        if response.status_code == 200:
            templates = response.json().get('templates', [])
            print(f"   ✅ Найдено {len(templates)} шаблонов")
            
            if templates:
                template_id = templates[0]['id']
                template_name = templates[0]['name']
                print(f"   🎯 Используем шаблон: {template_name} ({template_id})")
            else:
                print("   ❌ Шаблоны не найдены")
                return
        else:
            print(f"   ❌ Ошибка получения шаблонов: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # Тестовые данные с ВСЕМИ возможными полями
    test_data = {
        "template_id": template_id,
        "replacements": {
            # Основные поля
            "dyno.agentName": "John Smith",
            "dyno.propertyAddress": "123 Main Street, Beverly Hills, CA 90210",
            "dyno.price": "$450,000",
            "dyno.bedrooms": "3",
            "dyno.bathrooms": "2",
            "dyno.sqft": "1,850",
            "dyno.agentPhone": "(555) 123-4567",
            "dyno.agentEmail": "john@realty.com",
            
            # Изображения - пробуем разные URL
            "dyno.agentPhoto": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            "dyno.propertyImage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop",
            
            # Лого - пробуем все возможные названия
            "dyno.companyLogo": "https://via.placeholder.com/200x100/007bff/ffffff?text=COMPANY+LOGO",
            "dyno.logo": "https://via.placeholder.com/200x100/28a745/ffffff?text=LOGO",
            "dyno.brandLogo": "https://via.placeholder.com/200x100/dc3545/ffffff?text=BRAND",
            
            # Альтернативные названия для headshot
            "dyno.headshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            "dyno.agentHeadshot": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            
            # Альтернативные названия для property
            "dyno.propertyimage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop",
            "dyno.houseImage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop"
        },
        "type": "png",
        "width": 400,
        "height": 300
    }
    
    print(f"\n2. Отправляю запрос на генерацию превью...")
    print(f"   📋 Полей для замены: {len(test_data['replacements'])}")
    
    try:
        response = requests.post(
            f"{api_url}/api/preview/with-data",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        print(f"   📡 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("   ✅ Превью создано успешно!")
                print(f"   🖼️ URL превью: {result.get('url', 'N/A')}")
                print(f"   📏 Размер: {result.get('width')}x{result.get('height')}")
                print(f"   📊 Замен применено: {result.get('replacements_count', 'N/A')}")
                print(f"   💾 Размер файла: {result.get('file_size', 'N/A')} байт")
                
                # Проверяем что файл действительно создан
                if result.get('url'):
                    file_url = f"{api_url}{result['url']}"
                    file_response = requests.head(file_url)
                    if file_response.status_code == 200:
                        print(f"   ✅ Файл превью доступен: {file_url}")
                    else:
                        print(f"   ❌ Файл превью недоступен: {file_response.status_code}")
                
            else:
                print(f"   ❌ Ошибка создания превью: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📄 Детали ошибки: {error_data}")
            except:
                print(f"   📄 Ответ сервера: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")

def test_specific_fields():
    """Тестируем конкретные проблемные поля"""
    print("\n🎯 ТЕСТ КОНКРЕТНЫХ ПРОБЛЕМНЫХ ПОЛЕЙ")
    print("=" * 50)
    
    problematic_fields = [
        {
            "name": "Лого компании",
            "fields": ["dyno.companyLogo", "dyno.logo", "dyno.brandLogo"],
            "test_url": "https://via.placeholder.com/200x100/007bff/ffffff?text=TEST+LOGO"
        },
        {
            "name": "Фото агента (headshot)",
            "fields": ["dyno.agentPhoto", "dyno.headshot", "dyno.agentHeadshot"],
            "test_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face"
        },
        {
            "name": "Фото недвижимости",
            "fields": ["dyno.propertyImage", "dyno.propertyimage", "dyno.houseImage"],
            "test_url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop"
        }
    ]
    
    for field_group in problematic_fields:
        print(f"\n📋 Тестирую: {field_group['name']}")
        print(f"   🔍 Возможные названия полей: {field_group['fields']}")
        print(f"   🖼️ Тестовый URL: {field_group['test_url']}")
        
        # Здесь можно добавить логику проверки каждого поля
        # Но для этого нужно знать точную структуру SVG шаблона

def create_debug_html():
    """Создаем HTML файл для отладки"""
    print("\n📄 СОЗДАНИЕ HTML ДЛЯ ОТЛАДКИ")
    print("=" * 50)
    
    debug_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Debug Preview Issues</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .error { color: red; }
        .success { color: green; }
        button { padding: 10px 20px; margin: 5px; }
        #result { margin-top: 20px; }
        img { max-width: 500px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>🔍 Debug Preview Issues</h1>
    
    <div class="test-section">
        <h2>Test Preview Generation</h2>
        <button onclick="testPreview()">Test Preview API</button>
        <button onclick="testWithDifferentFields()">Test Different Field Names</button>
        <div id="result"></div>
    </div>
    
    <script>
        async function testPreview() {
            const result = document.getElementById('result');
            result.innerHTML = '<p>Testing...</p>';
            
            try {
                const response = await fetch('/api/preview/with-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        template_id: 'your-template-id-here',
                        replacements: {
                            'dyno.agentPhoto': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face',
                            'dyno.propertyImage': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop',
                            'dyno.companyLogo': 'https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO',
                            'dyno.agentName': 'John Smith Test',
                            'dyno.price': '$999,999'
                        },
                        type: 'png'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    result.innerHTML = `
                        <div class="success">
                            <h3>✅ Success!</h3>
                            <p>Preview URL: <a href="${data.url}" target="_blank">${data.url}</a></p>
                            <img src="${data.url}" alt="Preview">
                            <p>Replacements: ${data.replacements_count}</p>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="error">❌ Request failed: ${error.message}</div>`;
            }
        }
        
        async function testWithDifferentFields() {
            // Test with different field name variations
            const fieldVariations = [
                { 'dyno.logo': 'https://via.placeholder.com/200x100/007bff/ffffff?text=LOGO1' },
                { 'dyno.companyLogo': 'https://via.placeholder.com/200x100/28a745/ffffff?text=LOGO2' },
                { 'dyno.brandLogo': 'https://via.placeholder.com/200x100/dc3545/ffffff?text=LOGO3' }
            ];
            
            // Implementation for testing different field variations
            console.log('Testing field variations:', fieldVariations);
        }
    </script>
</body>
</html>'''
    
    with open('debug_preview.html', 'w', encoding='utf-8') as f:
        f.write(debug_html)
    
    print("   ✅ Создан файл debug_preview.html")
    print("   🌐 Откройте его в браузере для интерактивной отладки")

def main():
    """Основная функция тестирования"""
    print("🔧 ТЕСТ ИСПРАВЛЕНИЙ ПРЕВЬЮ")
    print("=" * 60)
    
    test_preview_api()
    test_specific_fields()
    create_debug_html()
    
    print("\n🎯 РЕКОМЕНДАЦИИ:")
    print("1. Запустите сервер: python app.py")
    print("2. Откройте debug_preview.html в браузере")
    print("3. Проверьте консоль браузера на ошибки")
    print("4. Убедитесь что все URL изображений доступны")
    print("5. Проверьте логи сервера на детали обработки")

if __name__ == "__main__":
    main()