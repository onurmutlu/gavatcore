#!/usr/bin/env python3
# fix_sessions.py - Session dosyalarını WAL mode'dan kurtarma

import os
import sqlite3
import glob

def fix_session_file(session_path):
    """Session dosyasını DELETE mode'a çevir"""
    print(f"🔧 Düzeltiliyor: {session_path}")
    
    try:
        # SQLite bağlantısı aç
        conn = sqlite3.connect(session_path)
        cursor = conn.cursor()
        
        # WAL mode'u DELETE'e çevir
        cursor.execute("PRAGMA journal_mode=DELETE")
        result = cursor.fetchone()
        print(f"   Journal mode: {result[0]}")
        
        # Diğer optimizasyonlar
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA cache_size=10000")
        
        # Değişiklikleri kaydet
        conn.commit()
        conn.close()
        
        print(f"   ✅ Başarıyla düzeltildi")
        return True
        
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False

def main():
    print("🛠️ SESSION DOSYALARI DÜZELTME")
    print("=" * 40)
    
    # Session dosyalarını bul
    session_files = glob.glob("sessions/*.session")
    session_files = [f for f in session_files if not f.endswith(".disabled")]
    
    print(f"📁 Bulunan session dosyaları: {len(session_files)}")
    
    success_count = 0
    for session_file in session_files:
        if fix_session_file(session_file):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(session_files)} dosya başarıyla düzeltildi")
    
    # Journal dosyalarını temizle
    journal_files = glob.glob("sessions/*.session-journal") + \
                   glob.glob("sessions/*.session-wal") + \
                   glob.glob("sessions/*.session-shm")
    
    if journal_files:
        print(f"\n🗑️ {len(journal_files)} journal dosyası temizleniyor...")
        for journal_file in journal_files:
            try:
                os.remove(journal_file)
                print(f"   Silindi: {journal_file}")
            except Exception as e:
                print(f"   Silinemedi {journal_file}: {e}")
    
    print("\n🎉 Session düzeltme tamamlandı!")

if __name__ == "__main__":
    main() 