#!/usr/bin/env python3
"""
Прямое удаление тестовых шаблонов из базы данных
"""

import sqlite3

def delete_test_templates():
    """Удаляет все тестовые шаблоны напрямую из базы"""
    
    print("🗑️ УДАЛЕНИЕ ТЕСТОВЫХ ШАБЛОНОВ")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('templates.db')
        cursor = conn.cursor()
        
        # Сначала показываем что будем удалять
        cursor.execute('''
            SELECT id, name, category 
            FROM templates 
            WHERE category = 'test' OR LOWER(name) LIKE '%test%'
        ''')
        
        test_templates = cursor.fetchall()
        
        if test_templates:
            print(f"📋 Найдено тестовых шаблонов: {len(test_templates)}")
            print("\n🎯 Будут удалены:")
            for template_id, name, category in test_templates:
                print(f"  - {name} (ID: {template_id}, Category: {category})")
            
            # Удаляем
            cursor.execute('''
                DELETE FROM templates 
                WHERE category = 'test' OR LOWER(name) LIKE '%test%'
            ''')
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            print(f"\n✅ Удалено шаблонов: {rows_affected}")
            
            # Проверяем что осталось
            cursor.execute('SELECT id, name, category FROM templates')
            remaining = cursor.fetchall()
            
            print(f"\n📊 Осталось шаблонов: {len(remaining)}")
            if remaining:
                print("\n📋 Оставшиеся шаблоны:")
                for template_id, name, category in remaining:
                    print(f"  - {name} (Category: {category})")
        else:
            print("ℹ️ Тестовых шаблонов не найдено")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    delete_test_templates()