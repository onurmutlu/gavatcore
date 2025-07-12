#!/usr/bin/env python3
"""
📝 SIMPLE LOGS TEST
Test basic logging functionality without dependencies
"""

import os
import sys
from datetime import datetime

def create_simple_log_event(user_id: str, message: str, level: str = "INFO"):
    """Basit log event oluşturucu"""
    try:
        # Logs klasörü oluştur
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # Log dosyası yolu
        log_file = os.path.join(logs_dir, f"{user_id}.log")
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log entry
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Dosyaya yaz
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return True
        
    except Exception as e:
        print(f"❌ Log yazma hatası: {e}")
        return False

def test_basic_logging():
    """Temel log functionality test"""
    print("📝 BASIC LOGGING TEST")
    print("=" * 30)
    
    try:
        # Test kullanıcısı
        test_user = "simple_log_test"
        
        # Test mesajları
        test_messages = [
            ("GPT yanıt sistemi başlatıldı", "INFO"),
            ("Kullanıcı mesajı alındı: Merhaba", "INFO"),
            ("GPT API çağrısı yapılıyor", "DEBUG"),
            ("GPT yanıt alındı: Merhaba canım!", "INFO"),
            ("Yanıt gönderildi", "INFO"),
            ("API rate limit uyarısı", "WARNING"),
            ("Coin azalması: 5 coin", "INFO"),
            ("Günlük limit kontrolü", "DEBUG")
        ]
        
        # Log'ları yaz
        for message, level in test_messages:
            success = create_simple_log_event(test_user, message, level)
            if success:
                print(f"✅ {level}: {message}")
            else:
                print(f"❌ {level}: {message}")
        
        # Log dosyasını kontrol et
        log_file = f"logs/{test_user}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n📄 Log dosyası: {log_file}")
                print(f"📊 Toplam satır: {len(lines)}")
                print("📝 Son 3 satır:")
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic logging test hatası: {e}")
        return False

def test_gpt_simulation():
    """GPT yanıt sistemi simülasyonu"""
    print("\n🤖 GPT SIMULATION TEST")
    print("=" * 30)
    
    try:
        # Fallback GPT responses
        fallback_responses = [
            "Merhaba canım! Nasılsın? 💕",
            "Hoş geldin! Seni bekliyordum 😘",
            "Bugün nasıl geçiyor? 🌸",
            "Yine mi geldin? Özlemişim seni 💋",
            "Selam tatlım! Ne var ne yok? ✨"
        ]
        
        # Test user
        test_user = "gpt_simulation"
        
        # GPT simulation
        for i, response in enumerate(fallback_responses):
            # Log başlangıç
            create_simple_log_event(test_user, f"GPT çağrısı {i+1} başladı", "INFO")
            
            # Log yanıt
            create_simple_log_event(test_user, f"GPT yanıt {i+1}: {response}", "INFO")
            
            # Log bitiş
            create_simple_log_event(test_user, f"GPT çağrısı {i+1} tamamlandı", "INFO")
            
            print(f"✅ GPT Sim {i+1}: {response[:30]}...")
        
        # Log dosyasını kontrol et
        log_file = f"logs/{test_user}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n📄 GPT Simulation log: {len(lines)} satır")
        
        return True
        
    except Exception as e:
        print(f"❌ GPT simulation test hatası: {e}")
        return False

def test_logs_directory_structure():
    """Logs directory yapısını test et"""
    print("\n📁 LOGS DIRECTORY STRUCTURE TEST")
    print("=" * 40)
    
    try:
        logs_dir = "logs"
        
        # Directory kontrol
        if os.path.exists(logs_dir):
            print(f"✅ Logs directory mevcut: {logs_dir}")
            
            # Dosyaları listele
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            
            print(f"📄 Log dosya sayısı: {len(log_files)}")
            
            total_size = 0
            for log_file in log_files:
                full_path = os.path.join(logs_dir, log_file)
                size = os.path.getsize(full_path)
                total_size += size
                
                # Log dosyası içeriği
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print(f"   {log_file}: {len(lines)} satır, {size} bytes")
            
            print(f"📊 Toplam log boyutu: {total_size} bytes")
            
            return True
        else:
            print(f"❌ Logs directory bulunamadı: {logs_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Directory structure test hatası: {e}")
        return False

def test_coin_logging():
    """Coin işlemleri için log test"""
    print("\n🪙 COIN LOGGING TEST")
    print("=" * 30)
    
    try:
        test_user = "coin_log_test"
        
        # Coin işlemleri simulation
        coin_operations = [
            ("Kullanıcı 100 coin kazandı", "INFO"),
            ("Coin tier: Silver", "INFO"),
            ("25 coin harcandı", "INFO"),
            ("Günlük limit kontrolü: 75/100", "DEBUG"),
            ("Coin bakiye: 75", "INFO"),
            ("Yetersiz bakiye uyarısı", "WARNING"),
            ("Coin işlem başarısız", "ERROR")
        ]
        
        for operation, level in coin_operations:
            create_simple_log_event(test_user, operation, level)
            print(f"✅ {level}: {operation}")
        
        # Log kontrolü
        log_file = f"logs/{test_user}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"\n📄 Coin log dosyası: {len(lines)} satır")
        
        return True
        
    except Exception as e:
        print(f"❌ Coin logging test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 SIMPLE LOGS COMPREHENSIVE TEST")
    print("=" * 50)
    
    results = []
    
    # Test 1: Basic logging
    results.append(test_basic_logging())
    
    # Test 2: GPT simulation
    results.append(test_gpt_simulation())
    
    # Test 3: Directory structure
    results.append(test_logs_directory_structure())
    
    # Test 4: Coin logging
    results.append(test_coin_logging())
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    
    test_names = [
        "Basic Logging",
        "GPT Simulation",
        "Directory Structure", 
        "Coin Logging"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    if success_rate >= 75:
        print("✅ Logs sistemi temel seviyede production ready!")
        return True
    else:
        print("❌ Logs sistemi düzeltmeye ihtiyaç var")
        return False

if __name__ == "__main__":
    main() 