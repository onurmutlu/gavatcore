#!/usr/bin/env python3
"""
🧠 Behavioral Dashboard Test
===========================

Behavioral Insights Dashboard test ve demo verisi oluşturur.
"""

import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Demo kullanıcıları ve mesajları oluştur."""
    try:
        conn = sqlite3.connect('gavatcore_v2.db')
        
        # Demo kullanıcıları oluştur
        demo_users = [
            ('demo_user_1', 'Alice_Streamr', '2025-01-01'),
            ('demo_user_2', 'Bob_Gamer', '2025-01-02'),
            ('demo_user_3', 'Carol_Artist', '2025-01-03'),
            ('demo_user_4', 'David_Tech', '2025-01-04'),
            ('demo_user_5', 'Emma_Writer', '2025-01-05')
        ]
        
        # Users tablosunu oluştur
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                joined_date TEXT
            )
        ''')
        
        # Messages tablosunu oluştur
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message_text TEXT,
                timestamp TEXT,
                sentiment_score REAL
            )
        ''')
        
        # Demo kullanıcıları ekle
        for user_id, username, joined_date in demo_users:
            conn.execute(
                'INSERT OR REPLACE INTO users (user_id, username, joined_date) VALUES (?, ?, ?)',
                (user_id, username, joined_date)
            )
        
        # Demo mesajları oluştur
        demo_messages = [
            # Alice - Pozitif, sosyal
            ('demo_user_1', 'Hey everyone! Great stream today! 😊', 0.8),
            ('demo_user_1', 'Love this community so much! ❤️', 0.9),
            ('demo_user_1', 'Can\'t wait for tomorrow\'s show!', 0.7),
            ('demo_user_1', 'You guys are amazing! Keep it up!', 0.85),
            ('demo_user_1', 'Having such a good time here 🎉', 0.75),
            
            # Bob - Nötr, gamer
            ('demo_user_2', 'gg that was a good match', 0.3),
            ('demo_user_2', 'what build are you using?', 0.1),
            ('demo_user_2', 'laggy connection today :/', -0.2),
            ('demo_user_2', 'nice plays everyone', 0.4),
            ('demo_user_2', 'see you next game', 0.2),
            
            # Carol - Sanatsal, değişken mood
            ('demo_user_3', 'This art is absolutely beautiful! 🎨', 0.8),
            ('demo_user_3', 'Feeling uninspired today...', -0.4),
            ('demo_user_3', 'Colors don\'t feel right ugh', -0.3),
            ('demo_user_3', 'Finally finished my piece!', 0.7),
            ('demo_user_3', 'Art block is the worst 😞', -0.6),
            
            # David - Teknik, analitik
            ('demo_user_4', 'The latency optimization looks good', 0.3),
            ('demo_user_4', 'Need to debug this API issue', -0.1),
            ('demo_user_4', 'Performance metrics are improving', 0.5),
            ('demo_user_4', 'Code review feedback implemented', 0.2),
            ('demo_user_4', 'System architecture needs refactoring', -0.2),
            
            # Emma - Yaratıcı, duygusal
            ('demo_user_5', 'Words flowing like poetry today ✨', 0.8),
            ('demo_user_5', 'Writer\'s block hitting hard...', -0.5),
            ('demo_user_5', 'This story is coming together beautifully', 0.7),
            ('demo_user_5', 'Struggling with character development', -0.3),
            ('demo_user_5', 'Just published my new chapter! 📖', 0.9)
        ]
        
        # Zaman damgaları ile mesajları ekle
        base_time = datetime.now() - timedelta(days=7)
        
        for i, (user_id, message, sentiment) in enumerate(demo_messages):
            timestamp = base_time + timedelta(hours=i*2, minutes=random.randint(0, 59))
            conn.execute(
                'INSERT INTO messages (user_id, message_text, timestamp, sentiment_score) VALUES (?, ?, ?, ?)',
                (user_id, message, timestamp.isoformat(), sentiment)
            )
        
        conn.commit()
        conn.close()
        
        print("✅ Demo data created successfully!")
        print(f"   • {len(demo_users)} demo users")
        print(f"   • {len(demo_messages)} demo messages")
        
        return demo_users
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        return []

def test_behavioral_dashboard():
    """Behavioral dashboard endpoints'ini test et."""
    base_url = "http://localhost:5056"
    
    print("\n🧠 Testing Behavioral Insights Dashboard")
    print("=" * 50)
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test cache metrics
    try:
        response = requests.get(f"{base_url}/api/behavioral/cache/metrics", timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Cache metrics:")
            print(f"   • Total profiles: {metrics['total_profiles']}")
            print(f"   • Hit rate: {metrics['hit_rate_24h']:.1f}%")
            print(f"   • Avg response time: {metrics['avg_response_time']:.4f}s")
        else:
            print(f"❌ Cache metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache metrics error: {e}")
    
    # Test user profiles
    demo_user_ids = ['demo_user_1', 'demo_user_2', 'demo_user_3']
    
    for user_id in demo_user_ids:
        try:
            print(f"\n🔍 Testing profile for {user_id}...")
            response = requests.get(f"{base_url}/api/behavioral/profile/{user_id}", timeout=15)
            
            if response.status_code == 200:
                profile_data = response.json()
                profile = profile_data['profile']
                
                print(f"✅ Profile analysis successful:")
                print(f"   • Username: {profile['username']}")
                print(f"   • Big Five Traits:")
                for trait, score in profile['big_five_scores'].items():
                    print(f"     - {trait.capitalize()}: {score:.3f}")
                
                print(f"   • Risk Assessment:")
                for risk_type, score in profile['risk_assessment'].items():
                    print(f"     - {risk_type.replace('_', ' ').title()}: {score:.3f}")
                
                print(f"   • Interaction Patterns:")
                patterns = profile['interaction_patterns']
                print(f"     - Total messages: {patterns['total_messages']}")
                print(f"     - Avg sentiment: {patterns['avg_sentiment']:.3f}")
                print(f"     - Most active hour: {patterns['most_active_hour']}")
                print(f"     - Activity score: {patterns['activity_score']:.3f}")
                
                # Cache performance
                cache_perf = profile_data['cache_performance']
                print(f"   • Cache Performance:")
                print(f"     - Hit rate: {cache_perf['hit_rate']:.1f}%")
                print(f"     - Total analyses: {cache_perf['total_analyses']}")
                
            else:
                print(f"❌ Profile analysis failed: {response.status_code}")
                if response.text:
                    print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Profile analysis error for {user_id}: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    # Test insights summary
    try:
        print(f"\n📊 Testing insights summary...")
        response = requests.get(f"{base_url}/api/behavioral/insights/summary", timeout=10)
        
        if response.status_code == 200:
            summary = response.json()
            print("✅ Insights summary:")
            print(f"   • Total users analyzed: {summary['total_users']}")
            print(f"   • Overall sentiment trend: {summary['overall_sentiment_trend']:.3f}")
            
            if 'avg_big_five_traits' in summary:
                print(f"   • Average Big Five traits:")
                for trait, score in summary['avg_big_five_traits'].items():
                    print(f"     - {trait.capitalize()}: {score:.3f}")
            
            cache_perf = summary.get('cache_performance', {})
            print(f"   • Cache performance:")
            print(f"     - Hit rate: {cache_perf.get('hit_rate', 0):.1f}%")
            print(f"     - Total analyses: {cache_perf.get('total_analyses', 0)}")
            
        else:
            print(f"❌ Insights summary failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Insights summary error: {e}")
    
    # Test high-risk users
    try:
        print(f"\n⚠️ Testing high-risk users...")
        response = requests.get(f"{base_url}/api/behavioral/users/high-risk?risk_threshold=0.3", timeout=10)
        
        if response.status_code == 200:
            risk_data = response.json()
            print(f"✅ High-risk users analysis:")
            print(f"   • Risk threshold: {risk_data['risk_threshold']}")
            print(f"   • High-risk users found: {risk_data['count']}")
            
            for user in risk_data['high_risk_users'][:3]:  # Show top 3
                print(f"   • {user['username']} (ID: {user['user_id']})")
                print(f"     - Overall risk: {user['overall_risk']:.3f}")
                
        else:
            print(f"❌ High-risk users failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ High-risk users error: {e}")

def main():
    """Ana test fonksiyonu."""
    print("🧠 Behavioral Insights Dashboard Test Suite")
    print("=" * 60)
    
    # Demo data oluştur
    demo_users = create_demo_data()
    
    if demo_users:
        # Dashboard'u test et
        test_behavioral_dashboard()
        
        print("\n🎉 Test Suite Complete!")
        print("=" * 30)
        print("🌐 Dashboard URL: http://localhost:5056")
        print("📊 API Docs: http://localhost:5056/api/behavioral/")
        print("🧠 Test users created for analysis")
    else:
        print("❌ Failed to create demo data, skipping tests")

if __name__ == "__main__":
    main() 