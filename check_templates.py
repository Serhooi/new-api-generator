#!/usr/bin/env python3
"""
Проверяем какие шаблоны есть в базе данных на сервере
"""

import requests
import json

def check_available_templates():
    """Проверяем доступные шаблоны"""
    
    url = "https://new-api-generator-1.onrender.com/api/templates/all-previews"
    
    print("🔍 Проверяю доступные шаблоны...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            templates = result.get('templates', [])
            print(f"✅ Найдено шаблонов: {len(templates)}")
            
            for i, template in enumerate(templates[:10]):  # Показываем первые 10
                print(f"📄 {i+1}. ID: {template.get('id', 'N/A')} | Имя: {template.get('name', 'N/A')}")
                
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Ошибка: {e}")

if __name__ == "__main__":
    check_available_templates()