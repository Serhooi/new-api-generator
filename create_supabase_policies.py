#!/usr/bin/env python3
"""
Создание политик для Supabase Storage
"""

import os
from supabase import create_client, Client

def create_storage_policies():
    """Создаем политики для публичного доступа к файлам"""
    
    print("🔧 СОЗДАНИЕ ПОЛИТИК SUPABASE STORAGE")
    print("=" * 50)
    
    # Получаем переменные окружения
    supabase_url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Переменные SUPABASE_URL или SUPABASE_SERVICE_ROLE_KEY не установлены")
        return False
    
    try:
        # Создаем клиент с service role ключом
        supabase: Client = create_client(supabase_url, service_key)
        print(f"✅ Supabase клиент создан с service role")
        
        # Список bucket для которых нужны политики
        buckets = ['carousel-assets', 'images']
        
        for bucket_name in buckets:
            print(f"\n🪣 Создаю политики для bucket: {bucket_name}")
            
            # Политика для публичного чтения
            select_policy = f"""
            CREATE POLICY "Public read access for {bucket_name}" ON storage.objects
            FOR SELECT USING (bucket_id = '{bucket_name}');
            """
            
            # Политика для загрузки файлов
            insert_policy = f"""
            CREATE POLICY "Allow public uploads to {bucket_name}" ON storage.objects
            FOR INSERT WITH CHECK (bucket_id = '{bucket_name}');
            """
            
            # Политика для обновления файлов
            update_policy = f"""
            CREATE POLICY "Allow public updates in {bucket_name}" ON storage.objects
            FOR UPDATE USING (bucket_id = '{bucket_name}');
            """
            
            # Политика для удаления файлов
            delete_policy = f"""
            CREATE POLICY "Allow public deletes in {bucket_name}" ON storage.objects
            FOR DELETE USING (bucket_id = '{bucket_name}');
            """
            
            policies = [
                ("SELECT", select_policy),
                ("INSERT", insert_policy), 
                ("UPDATE", update_policy),
                ("DELETE", delete_policy)
            ]
            
            for policy_type, policy_sql in policies:
                try:
                    result = supabase.rpc('exec_sql', {'sql': policy_sql}).execute()
                    print(f"  ✅ {policy_type} политика создана")
                except Exception as e:
                    print(f"  ⚠️ {policy_type} политика: {str(e)}")
        
        print(f"\n🎉 Политики созданы!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания политик: {e}")
        return False

def test_public_access():
    """Тестируем публичный доступ к файлам"""
    
    print("\n🧪 ТЕСТ ПУБЛИЧНОГО ДОСТУПА")
    print("=" * 40)
    
    import requests
    
    # Тестовые URL
    test_urls = [
        "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/carousel-assets/test/test.svg",
        "https://vahgmyuowsilbxqdjjii.supabase.co/storage/v1/object/public/images/test/test.svg"
    ]
    
    for url in test_urls:
        print(f"\n🌐 Тестирую: {url}")
        try:
            response = requests.head(url, timeout=10)
            print(f"📊 Статус: {response.status_code}")
            
            if response.status_code == 404:
                print("ℹ️ Файл не найден (это нормально для теста)")
            elif response.status_code == 200:
                print("✅ Файл доступен")
            elif response.status_code == 403:
                print("❌ Доступ запрещен - политики не работают")
            else:
                print(f"⚠️ Неожиданный статус: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    success = create_storage_policies()
    if success:
        test_public_access()
    else:
        print("❌ Не удалось создать политики")