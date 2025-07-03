#!/usr/bin/env python3
"""
🔓 BabaGAVAT Session Unlocker
Database lock sorununu çözer
"""

import os
import shutil
import time

def unlock_session():
    """Session lock'ını kaldır"""
    
    print("""
🔓 BABAGAVAT SESSION UNLOCK
💀 Database lock temizleniyor...
    """)
    
    session_path = "sessions/babagavat_conversation"
    
    # Journal dosyasını temizle (lock genelde buradan kaynaklanır)
    journal_path = f"{session_path}.session-journal"
    
    if os.path.exists(journal_path):
        print(f"📄 Journal dosyası bulundu: {journal_path}")
        
        # Journal'ı yedekle
        backup_journal = f"{journal_path}.backup_{int(time.time())}"
        shutil.copy(journal_path, backup_journal)
        print(f"✅ Journal yedeği alındı: {backup_journal}")
        
        # Journal'ı sil
        os.remove(journal_path)
        print("✅ Journal dosyası temizlendi")
    else:
        print("❌ Journal dosyası bulunamadı")
    
    # WAL ve SHM dosyalarını da kontrol et
    wal_path = f"{session_path}.session-wal"
    shm_path = f"{session_path}.session-shm"
    
    for path in [wal_path, shm_path]:
        if os.path.exists(path):
            os.remove(path)
            print(f"✅ {path} temizlendi")
    
    print("\n✅ Session lock temizlendi!")
    print("🚀 Artık BabaGAVAT kullanılabilir!")
    
    # Session'ı test et
    print("\n🧪 Session test ediliyor...")
    test_session()

def test_session():
    """Session'ı basit bir test ile kontrol et"""
    import sqlite3
    
    try:
        conn = sqlite3.connect("sessions/babagavat_conversation.session")
        cursor = conn.cursor()
        
        # Basit bir query çalıştır
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            print("✅ Session veritabanı erişilebilir!")
            print(f"   İlk tablo: {result[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Session test hatası: {e}")

if __name__ == "__main__":
    unlock_session() 