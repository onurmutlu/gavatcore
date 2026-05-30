#!/usr/bin/env python3
"""
🤖 GPT LOGS TEST
Test GPT response system and log mechanism
"""

import os
import sys
import asyncio
from datetime import datetime
import time

# Add current directory to path
sys.path.append('.')

def test_log_utils():
    """Test log utilities"""
    print("📝 LOG UTILS TEST")
    print("=" * 30)
    
    try:
        from utilities.log_utils import log_event
        
        # Test 1: Normal log event
        test_user = "test_user_999"
        test_message = "Test GPT log mesajı"
        
        log_event(test_user, test_message, "INFO")
        
        # Log dosyasını kontrol et
        log_file = f"logs/{test_user}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ Log dosyası oluşturuldu: {log_file}")
                print(f"📄 İçerik: {content.strip()}")
        else:
            print(f"❌ Log dosyası bulunamadı: {log_file}")
            
        # Test 2: Multiple log events
        for i in range(3):
            log_event(test_user, f"Test mesaj {i+1}", "INFO")
            
        # Test 3: Different log levels
        log_event(test_user, "Debug mesajı", "DEBUG")
        log_event(test_user, "Warning mesajı", "WARNING")
        log_event(test_user, "Error mesajı", "ERROR")
        
        # Final log content check
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"✅ Toplam log satırı: {len(lines)}")
                print("✅ Log utils test başarılı!")
        
        return True
        
    except Exception as e:
        print(f"❌ Log utils test hatası: {e}")
        return False

def test_gpt_client():
    """Test GPT client with fallback"""
    print("\n🤖 GPT CLIENT TEST")
    print("=" * 30)
    
    try:
        from gpt.gpt_call import GPTClient
        
        # GPT client oluştur
        gpt_client = GPTClient()
        
        # Test prompt
        test_prompt = "Merhaba, nasılsın?"
        
        print(f"📝 Test prompt: {test_prompt}")
        
        # Sync version test
        result = asyncio.run(gpt_client.gpt_call(test_prompt, "general"))
        
        print(f"✅ GPT yanıt: {result}")
        
        # Test different message types
        message_types = ["flirty", "mention_reply", "group_context"]
        
        for msg_type in message_types:
            result = asyncio.run(gpt_client.gpt_call(f"Test {msg_type}", msg_type))
            print(f"✅ {msg_type}: {result[:50]}...")
            
        print("✅ GPT client test başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ GPT client test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gpt_logs_integration():
    """Test GPT integration with logs"""
    print("\n🔄 GPT LOGS INTEGRATION TEST")
    print("=" * 40)
    
    try:
        from utilities.log_utils import log_event
        from gpt.gpt_call import GPTClient
        
        # Test user
        test_user = "gpt_log_test"
        
        # Log başlangıç
        log_event(test_user, "GPT integration test başladı", "INFO")
        
        # GPT client
        gpt_client = GPTClient()
        
        # Test prompts
        test_prompts = [
            "Merhaba canım",
            "Nasılsın bugün?",
            "Seni özledim",
            "Ne yapıyorsun?"
        ]
        
        for i, prompt in enumerate(test_prompts):
            # Log before GPT call
            log_event(test_user, f"GPT çağrısı {i+1}: {prompt}", "INFO")
            
            # GPT call
            start_time = time.time()
            result = asyncio.run(gpt_client.gpt_call(prompt, "general"))
            end_time = time.time()
            
            # Log result
            log_event(test_user, f"GPT yanıt {i+1}: {result}", "INFO")
            log_event(test_user, f"GPT süre {i+1}: {end_time - start_time:.2f}s", "INFO")
            
            print(f"✅ Test {i+1}: {prompt} -> {result[:30]}...")
            
        # Log bitiş
        log_event(test_user, "GPT integration test tamamlandı", "INFO")
        
        # Final log check
        log_file = f"logs/{test_user}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"✅ Integration log satırı: {len(lines)}")
                print("✅ Son 3 satır:")
                for line in lines[-3:]:
                    print(f"   {line.strip()}")
        
        print("✅ GPT logs integration test başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ GPT logs integration test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logs_directory():
    """Test logs directory structure"""
    print("\n📁 LOGS DIRECTORY TEST")
    print("=" * 30)
    
    try:
        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)
        
        # Check directory
        if os.path.exists("logs"):
            print("✅ Logs klasörü mevcut")
            
            # List files
            log_files = os.listdir("logs")
            print(f"📄 Mevcut log dosyaları: {len(log_files)}")
            
            for log_file in log_files:
                if log_file.endswith('.log'):
                    full_path = os.path.join("logs", log_file)
                    size = os.path.getsize(full_path)
                    print(f"   {log_file}: {size} bytes")
            
            return True
        else:
            print("❌ Logs klasörü bulunamadı")
            return False
            
    except Exception as e:
        print(f"❌ Logs directory test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 GPT LOGS COMPREHENSIVE TEST")
    print("=" * 50)
    
    results = []
    
    # Test 1: Logs directory
    results.append(test_logs_directory())
    
    # Test 2: Log utils
    results.append(test_log_utils())
    
    # Test 3: GPT client
    results.append(test_gpt_client())
    
    # Test 4: Integration
    results.append(test_gpt_logs_integration())
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 20)
    
    test_names = [
        "Logs Directory",
        "Log Utils",
        "GPT Client",
        "GPT Logs Integration"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    
    if success_rate >= 75:
        print("✅ GPT logs sistemi production ready!")
        return True
    else:
        print("❌ GPT logs sistemi düzeltmeye ihtiyaç var")
        return False

if __name__ == "__main__":
    main() 