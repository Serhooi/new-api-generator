#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import sqlite3
import os

DATABASE_PATH = 'templates.db'

def ensure_db_exists():
    """
    Создает базу данных и таблицы если они не существуют
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу templates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            dyno_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создаем таблицу carousels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carousels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            templates TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ База данных {DATABASE_PATH} инициализирована!")

if __name__ == "__main__":
    ensure_db_exists()