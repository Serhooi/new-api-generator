#!/usr/bin/env python3
"""
Проверка переменных окружения
"""

import os

def check_environment():
    """Проверяем переменные окружения"""
    
    print("🔍 ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 50)
    
    # Основные переменные
    env_vars = [
        'RENDER',
        'SUPABASE_URL', 
        'SUPABASE_ANON_KEY',
        'PORT',
        'PYTHON_VERSION'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Скрываем ключи для безопасности
            if 'KEY' in var and len(value) > 10:
                display_value = value[:10] + "..." + value[-5:]
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: не установлена")
    
    # Проверяем логику is_render
    print("\\n🔍 ЛОГИКА IS_RENDER:")
    render_var = os.environ.get('RENDER', False)
    supabase_url = os.environ.get('SUPABASE_URL')
    
    print(f"📋 RENDER: {render_var}")
    print(f"📋 SUPABASE_URL: {supabase_url}")
    
    if supabase_url:
        url_condition = supabase_url != 'https://vahgmyuowsilbxqdjjii.supabase.co'
        print(f"📋 URL != vahgmyuowsilbxqdjjii: {url_condition}")
    
    is_render = render_var or bool(supabase_url)
    print(f"🎯 is_render результат: {is_render}")
    
    if is_render:
        print("✅ Файлы будут загружаться в Supabase")
    else:
        print("📁 Файлы будут сохраняться локально")

def test_supabase_connection():
    """Тестируем подключение к Supabase"""
    
    print("\\n🔗 ТЕСТ ПОДКЛЮЧЕНИЯ К SUPABASE")
    print("=" * 40)
    
    try:
        from supabase import create_client, Client
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Переменные SUPABASE_URL или SUPABASE_ANON_KEY не установлены")
            return
        
        # Создаем клиент
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase клиент создан")
        
        # Проверяем доступ к storage
        try:
            buckets = supabase.storage.list_buckets()
            print(f"✅ Найдено buckets: {len(buckets)}")
            
            for bucket in buckets:
                print(f"  🪣 {bucket.name} (public: {bucket.public})")
                
        except Exception as e:
            print(f"❌ Ошибка доступа к storage: {e}")
            
    except ImportError:
        print("❌ Модуль supabase не установлен")
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")

if __name__ == "__main__":
    check_environment()
    test_supabase_connection()