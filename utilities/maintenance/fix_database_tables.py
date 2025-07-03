#!/usr/bin/env python3
"""
🔧 Database Table Fixer
======================

Mevcut tabloları günceller ve eksik column'ları ekler.
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def fix_database_tables():
    """Mevcut tabloları düzelt ve eksik column'ları ekle."""
    try:
        db_path = 'gavatcore_v2.db'
        conn = sqlite3.connect(db_path)
        
        print(f"🔧 Fixing database: {db_path}")
        
        # Users tablosunu güncelle
        try:
            # Mevcut column'ları kontrol et
            cursor = conn.execute("PRAGMA table_info(users)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            print(f"📋 Mevcut users columns: {existing_columns}")
            
            # Eksik column'ları ekle
            columns_to_add = [
                ('display_name', 'TEXT'),
                ('first_name', 'TEXT'),
                ('last_name', 'TEXT'),
                ('phone', 'TEXT'),
                ('bio', 'TEXT'),
                ('is_bot', 'BOOLEAN DEFAULT FALSE'),
                ('is_verified', 'BOOLEAN DEFAULT FALSE'),
                ('is_premium', 'BOOLEAN DEFAULT FALSE'),
                ('language_code', 'TEXT DEFAULT "tr"'),
                ('last_seen', 'TEXT'),
                ('status', 'TEXT DEFAULT "active"'),
                ('total_messages', 'INTEGER DEFAULT 0'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        conn.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                        print(f"✅ Added column: users.{column_name}")
                    except Exception as e:
                        print(f"⚠️ Column {column_name} might already exist: {e}")
            
        except Exception as e:
            print(f"❌ Users table error: {e}")
        
        # Messages tablosunu güncelle
        try:
            cursor = conn.execute("PRAGMA table_info(messages)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            print(f"📋 Mevcut messages columns: {existing_columns}")
            
            columns_to_add = [
                ('message_id', 'TEXT'),
                ('username', 'TEXT'),
                ('chat_id', 'TEXT'),
                ('chat_title', 'TEXT'),
                ('message_type', 'TEXT DEFAULT "text"'),
                ('is_bot_message', 'BOOLEAN DEFAULT FALSE'),
                ('is_reply', 'BOOLEAN DEFAULT FALSE'),
                ('reply_to_message_id', 'TEXT'),
                ('language', 'TEXT DEFAULT "tr"'),
                ('word_count', 'INTEGER DEFAULT 0'),
                ('has_media', 'BOOLEAN DEFAULT FALSE'),
                ('media_type', 'TEXT'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        conn.execute(f"ALTER TABLE messages ADD COLUMN {column_name} {column_type}")
                        print(f"✅ Added column: messages.{column_name}")
                    except Exception as e:
                        print(f"⚠️ Column {column_name} might already exist: {e}")
                        
        except Exception as e:
            print(f"❌ Messages table error: {e}")
        
        # Yeni tabloları oluştur
        create_additional_tables(conn)
        
        # Demo data oluştur
        create_fixed_demo_data(conn)
        
        conn.commit()
        conn.close()
        print("🎉 Database başarıyla düzeltildi!")
        
    except Exception as e:
        print(f"❌ Database fix error: {e}")

def create_additional_tables(conn):
    """Ek tabloları oluştur."""
    try:
        # Groups tablosu
        conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                title TEXT,
                username TEXT,
                description TEXT,
                member_count INTEGER DEFAULT 0,
                type TEXT DEFAULT 'group',
                is_public BOOLEAN DEFAULT FALSE,
                invite_link TEXT,
                bot_is_admin BOOLEAN DEFAULT FALSE,
                bot_permissions TEXT,
                last_activity TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User Analytics tablosu
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                word_count INTEGER DEFAULT 0,
                active_minutes INTEGER DEFAULT 0,
                groups_active INTEGER DEFAULT 0,
                dm_count INTEGER DEFAULT 0,
                bot_interactions INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0,
                activity_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        
        # System Stats tablosu
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name TEXT UNIQUE NOT NULL,
                stat_value TEXT NOT NULL,
                stat_type TEXT DEFAULT 'counter',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot Sessions tablosu
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bot_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_username TEXT NOT NULL,
                session_file TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                last_activity TEXT,
                total_messages_sent INTEGER DEFAULT 0,
                total_groups INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Additional tables created!")
        
    except Exception as e:
        print(f"❌ Additional tables error: {e}")

def create_fixed_demo_data(conn):
    """Düzeltilmiş demo data oluştur."""
    try:
        print("📊 Creating fixed demo data...")
        
        # Mevcut users'ı güncelle
        demo_users = [
            ('demo_user_1', 'alice_streamer', 'Alice Streamer', 'Alice', 'Streamer', 'Professional streamer'),
            ('demo_user_2', 'bob_gamer', 'Bob Gamer', 'Bob', 'Wilson', 'Passionate gamer'),
            ('demo_user_3', 'carol_artist', 'Carol Artist', 'Carol', 'Davis', 'Digital artist'),
            ('user_12345', 'test_user', 'Test User', 'Test', 'User', 'Test user for analysis')
        ]
        
        for user_id, username, display_name, first_name, last_name, bio in demo_users:
            joined_date = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            last_seen = (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            
            # Update existing users
            conn.execute('''
                UPDATE users SET 
                    display_name = ?,
                    first_name = ?,
                    last_name = ?,
                    bio = ?,
                    last_seen = ?,
                    total_messages = ?,
                    status = 'active'
                WHERE user_id = ?
            ''', (display_name, first_name, last_name, bio, last_seen, random.randint(10, 100), user_id))
            
            # Insert if not exists
            conn.execute('''
                INSERT OR IGNORE INTO users (user_id, username, joined_date)
                VALUES (?, ?, ?)
            ''', (user_id, username, joined_date))
        
        # Demo messages güncelle
        demo_messages = [
            ('demo_user_1', 'group_1', 'Hey everyone! Starting my stream! 🎮', 0.8),
            ('demo_user_2', 'group_1', 'Looking forward to new releases! 🎯', 0.7),
            ('demo_user_3', 'group_2', 'Check out my latest artwork! 🎨', 0.9),
            ('user_12345', 'group_1', 'Hello community!', 0.7)
        ]
        
        # Mevcut mesajları güncelle
        for i, (user_id, group_id, message_text, sentiment) in enumerate(demo_messages):
            timestamp = (datetime.now() - timedelta(hours=i)).isoformat()
            
            conn.execute('''
                UPDATE messages SET 
                    message_type = 'text',
                    word_count = ?,
                    sentiment_score = ?,
                    chat_id = ?
                WHERE user_id = ? AND message_text = ?
            ''', (len(message_text.split()), sentiment, group_id, user_id, message_text))
        
        # System stats ekle
        system_stats = [
            ('total_users', '8', 'counter'),
            ('total_messages', '25', 'counter'),
            ('total_groups', '3', 'counter'),
            ('active_bots', '3', 'counter'),
            ('system_health', '98.5', 'percentage')
        ]
        
        for stat_name, stat_value, stat_type in system_stats:
            conn.execute('''
                INSERT OR REPLACE INTO system_stats (stat_name, stat_value, stat_type)
                VALUES (?, ?, ?)
            ''', (stat_name, stat_value, stat_type))
        
        # Bot sessions ekle
        bot_sessions = [
            ('yayincilara', 'sessions/_905382617727.session', True, 250, 3),
            ('babagavat', 'sessions/_905513272355.session', True, 180, 2),
            ('xxxgeisha', 'sessions/_905486306226.session', True, 120, 2)
        ]
        
        for bot_username, session_file, is_active, total_messages, total_groups in bot_sessions:
            last_activity = (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
            
            conn.execute('''
                INSERT OR REPLACE INTO bot_sessions 
                (bot_username, session_file, is_active, last_activity, total_messages_sent, total_groups)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (bot_username, session_file, is_active, last_activity, total_messages, total_groups))
        
        print("✅ Fixed demo data created!")
        
    except Exception as e:
        print(f"❌ Fixed demo data error: {e}")

if __name__ == "__main__":
    fix_database_tables() 