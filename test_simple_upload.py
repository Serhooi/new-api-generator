#!/usr/bin/env python3
"""
Простой тест загрузки без Supabase
"""

import os
import requests
import json

def test_local_save():
    """Тестируем локальное сохранение"""
    
    print("🧪 ТЕСТ ЛОКАЛЬНОГО СОХРАНЕНИЯ")
    print("=" * 50)
    
    # Временно отключаем Supabase
    os.environ.pop('SUPABASE_URL', None)
    os.environ.pop('SUPABASE_ANON_KEY', None)
    
    print("🔧 Supabase переменные отключены")
    
    # Запускаем сервер
    print("🚀 Запускаем сервер...")
    
    try:
        # Проверяем health
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"🏥 Health статус: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Сервер не работает")
            return False
        
        # Тестируем загрузку
        print("📤 Тестируем загрузку...")
        upload_response = requests.post(
            "http://localhost:5000/api/test-supabase",
            json={},
            timeout=10
        )
        
        print(f"📊 Upload статус: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print("✅ Загрузка успешна!")
            print(f"📄 Файл: {result.get('filename')}")
            print(f"🌐 URL: {result.get('url')}")
            return True
        else:
            print(f"❌ Ошибка: {upload_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка: {e}")
        return False

def restore_supabase_env():
    """Восстанавливаем переменные Supabase"""
    
    print("\n🔧 Восстанавливаем переменные Supabase...")
    os.environ['SUPABASE_URL'] = 'https://vahgmyuowsilbxqdjjii.supabase.co'
    os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhaGdteXVvd3NpbGJ4cWRqamlpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUyNTAyMTksImV4cCI6MjA2MDgyNjIxOX0.DLgDw26_qV8plubf-0ReBwuWtXPD-VHxQ1_RIGkSX6I'
    print("✅ Переменные восстановлены")

if __name__ == "__main__":
    try:
        test_local_save()
    finally:
        restore_supabase_env()