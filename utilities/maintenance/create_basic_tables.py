#!/usr/bin/env python3
"""
🗄️ Database Table Creator
========================

Admin dashboard'larda eksik olan temel tabloları oluşturur.
Bu script "no such table: users, messages" hatalarını çözer.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random

def create_basic_tables():
    """Temel tabloları oluştur."""
    try:
        # Ana database'e bağlan
        db_path = 'gavatcore_v2.db'
        conn = sqlite3.connect(db_path)
        
        print(f"🗄️ Database: {db_path}")
        
        # Users tablosunu oluştur
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                display_name TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                bio TEXT,
                is_bot BOOLEAN DEFAULT FALSE,
                is_verified BOOLEAN DEFAULT FALSE,
                is_premium BOOLEAN DEFAULT FALSE,
                language_code TEXT DEFAULT 'tr',
                joined_date TEXT,
                last_seen TEXT,
                status TEXT DEFAULT 'active',
                total_messages INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages tablosunu oluştur
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                user_id TEXT,
                username TEXT,
                chat_id TEXT,
                chat_title TEXT,
                message_text TEXT,
                message_type TEXT DEFAULT 'text',
                is_bot_message BOOLEAN DEFAULT FALSE,
                is_reply BOOLEAN DEFAULT FALSE,
                reply_to_message_id TEXT,
                sentiment_score REAL DEFAULT 0.0,
                language TEXT DEFAULT 'tr',
                word_count INTEGER DEFAULT 0,
                has_media BOOLEAN DEFAULT FALSE,
                media_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Groups tablosunu oluştur
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
        
        # User Analytics tablosunu oluştur
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
                UNIQUE(user_id, date),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # System Stats tablosunu oluştur
        conn.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_name TEXT UNIQUE NOT NULL,
                stat_value TEXT NOT NULL,
                stat_type TEXT DEFAULT 'counter',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bot Sessions tablosunu oluştur
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
        
        conn.commit()
        print("✅ Temel tablolar oluşturuldu!")
        
        # Demo data oluştur
        create_demo_data(conn)
        
        conn.close()
        print("🎉 Database hazırlandı!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def create_demo_data(conn):
    """Demo data oluştur."""
    try:
        print("📊 Demo data oluşturuluyor...")
        
        # Demo kullanıcıları
        demo_users = [
            ('demo_user_1', 'alice_streamer', 'Alice', 'Streamer', None, 'Professional streamer and content creator'),
            ('demo_user_2', 'bob_gamer', 'Bob', 'Wilson', None, 'Passionate gamer and community member'),
            ('demo_user_3', 'carol_artist', 'Carol', 'Davis', None, 'Digital artist and designer'),
            ('demo_user_4', 'david_tech', 'David', 'Chen', None, 'Tech enthusiast and developer'),
            ('demo_user_5', 'emma_writer', 'Emma', 'Johnson', None, 'Creative writer and storyteller'),
            ('user_12345', 'test_user', 'Test', 'User', None, 'Test user for behavioral analysis'),
            ('demo_user_6', 'frank_music', 'Frank', 'Miller', None, 'Music producer and DJ'),
            ('demo_user_7', 'grace_coach', 'Grace', 'Smith', None, 'Fitness coach and wellness expert')
        ]
        
        # Kullanıcıları ekle
        for user_data in demo_users:
            user_id, username, first_name, last_name, phone, bio = user_data
            joined_date = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            last_seen = (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
            
            conn.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, phone, bio, joined_date, last_seen, total_messages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, phone, bio, joined_date, last_seen, random.randint(10, 100)))
        
        # Demo mesajları
        demo_messages = [
            ('demo_user_1', 'group_1', 'Hey everyone! Starting my stream in 10 minutes! 🎮', 0.8),
            ('demo_user_2', 'group_1', 'Looking forward to the new game release! 🎯', 0.7),
            ('demo_user_3', 'group_2', 'Just finished my latest artwork! Check it out! 🎨', 0.9),
            ('demo_user_4', 'group_1', 'Found an interesting tech article, sharing the link...', 0.6),
            ('demo_user_5', 'group_2', 'Working on a new story chapter! 📖', 0.8),
            ('user_12345', 'group_1', 'Hello everyone! New to this community!', 0.7),
            ('demo_user_6', 'group_2', 'Drop the beat! New track coming soon! 🎵', 0.9),
            ('demo_user_7', 'group_1', 'Remember to stay hydrated during workouts! 💪', 0.8),
            ('demo_user_1', 'group_2', 'Thanks for all the support, amazing community! ❤️', 0.9),
            ('demo_user_2', 'group_2', 'Anyone up for a gaming session later?', 0.6)
        ]
        
        # Mesajları ekle
        for i, (user_id, group_id, message_text, sentiment) in enumerate(demo_messages):
            timestamp = (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
            message_id = f"msg_{i+1}_{user_id}"
            
            conn.execute('''
                INSERT INTO messages 
                (message_id, user_id, chat_id, message_text, sentiment_score, word_count, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (message_id, user_id, group_id, message_text, sentiment, len(message_text.split()), timestamp))
        
        # Demo grupları
        demo_groups = [
            ('group_1', 'Tech & Gaming Community', 'techgaming', 'Community for tech enthusiasts and gamers', 156),
            ('group_2', 'Creative Hub', 'creativehub', 'Space for artists, writers, and creators', 89),
            ('group_3', 'General Chat', None, 'General discussion group', 234)
        ]
        
        for group_id, title, username, description, member_count in demo_groups:
            last_activity = (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
            
            conn.execute('''
                INSERT OR REPLACE INTO groups 
                (group_id, title, username, description, member_count, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (group_id, title, username, description, member_count, last_activity))
        
        # System stats
        system_stats = [
            ('total_users', str(len(demo_users)), 'counter'),
            ('total_messages', str(len(demo_messages)), 'counter'),
            ('total_groups', str(len(demo_groups)), 'counter'),
            ('active_bots', '3', 'counter'),
            ('uptime_hours', '24', 'gauge'),
            ('system_health', '98.5', 'percentage')
        ]
        
        for stat_name, stat_value, stat_type in system_stats:
            conn.execute('''
                INSERT OR REPLACE INTO system_stats (stat_name, stat_value, stat_type)
                VALUES (?, ?, ?)
            ''', (stat_name, stat_value, stat_type))
        
        # Bot sessions
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
        
        # User analytics
        for user_data in demo_users:
            user_id = user_data[0]
            for days_ago in range(7):  # Son 7 gün
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                
                conn.execute('''
                    INSERT OR REPLACE INTO user_analytics 
                    (user_id, date, message_count, word_count, active_minutes, groups_active, engagement_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, date, 
                    random.randint(0, 15),  # message_count
                    random.randint(0, 200),  # word_count
                    random.randint(5, 120),  # active_minutes
                    random.randint(1, 3),    # groups_active
                    round(random.uniform(0.3, 0.9), 2)  # engagement_score
                ))
        
        conn.commit()
        print(f"✅ Demo data oluşturuldu!")
        print(f"   • {len(demo_users)} kullanıcı")
        print(f"   • {len(demo_messages)} mesaj") 
        print(f"   • {len(demo_groups)} grup")
        print(f"   • {len(system_stats)} sistem istatistiği")
        print(f"   • {len(bot_sessions)} bot session")
        
    except Exception as e:
        print(f"❌ Demo data error: {e}")

if __name__ == "__main__":
    create_basic_tables() 