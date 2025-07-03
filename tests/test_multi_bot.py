#!/usr/bin/env python3
"""
🧪 Multi-Bot Launcher Test Script 🧪

3 bot'un durumunu test eder ve rapor verir.
"""

import asyncio
import json
import os
from telethon import TelegramClient
from config import API_ID, API_HASH

async def test_bot_connections():
    """3 bot'un bağlantısını test eder"""
    
    print("🔍 Bot Session Test Başlıyor...\n")
    
    bots = [
        {"name": "xxxgeisha", "display": "Geisha", "phone": "+905486306226"},
        {"name": "yayincilara", "display": "Lara", "phone": "+905382617727"},
        {"name": "babagavat", "display": "Gavat Baba", "phone": "+905513272355"}
    ]
    
    results = []
    
    for bot in bots:
        session_path = f"sessions/{bot['name']}_conversation.session"
        
        print(f"🤖 {bot['display']} ({bot['name']}) test ediliyor...")
        
        try:
            # Session var mı kontrol et
            if not os.path.exists(session_path):
                results.append({
                    "bot": bot,
                    "status": "❌ SESSION_NOT_FOUND",
                    "details": f"Session dosyası bulunamadı: {session_path}"
                })
                continue
            
            # Telegram'a bağlanmayı dene
            client = TelegramClient(session_path.replace('.session', ''), API_ID, API_HASH)
            
            try:
                await client.start(phone=bot['phone'])
                me = await client.get_me()
                
                results.append({
                    "bot": bot,
                    "status": "✅ CONNECTED",
                    "details": f"@{me.username} (ID: {me.id})",
                    "user_info": me
                })
                
                print(f"  ✅ Başarılı: @{me.username} (ID: {me.id})")
                
            except Exception as e:
                results.append({
                    "bot": bot,
                    "status": "❌ CONNECTION_FAILED", 
                    "details": str(e)
                })
                print(f"  ❌ Bağlantı hatası: {e}")
            
            finally:
                await client.disconnect()
            
        except Exception as e:
            results.append({
                "bot": bot,
                "status": "❌ UNKNOWN_ERROR",
                "details": str(e)
            })
            print(f"  ❌ Bilinmeyen hata: {e}")
    
    # Sonuçları raporla
    print("\n" + "="*50)
    print("📊 BOT CONNECTION TEST REPORT")
    print("="*50)
    
    connected_count = 0
    for result in results:
        status = result["status"]
        bot_name = result["bot"]["display"]
        details = result["details"]
        
        print(f"{status} {bot_name}: {details}")
        
        if "CONNECTED" in status:
            connected_count += 1
    
    success_rate = (connected_count / len(bots)) * 100
    print(f"\n🎯 Başarı Oranı: {connected_count}/{len(bots)} ({success_rate:.1f}%)")
    
    if connected_count == len(bots):
        print("🎉 Tüm bot'lar hazır! Multi-bot launcher çalıştırılabilir.")
    elif connected_count > 0:
        print("⚠️ Bazı bot'lar hazır değil. Session'ları kontrol edin.")
    else:
        print("🚨 Hiç bot hazır değil. Session'lar oluşturulmalı.")
    
    return results

async def main():
    print("""
🧪 GavatCore Multi-Bot Test v1.0 🧪

Bu script 3 bot'un session durumunu kontrol eder:
• xxxgeisha (Geisha)
• yayincilara (Lara) 
• babagavat (Gavat Baba)

Başlatılıyor...
""")
    
    results = await test_bot_connections()
    
    # JSON rapor oluştur
    report = {
        "timestamp": "2025-05-30T05:52:00",
        "test_type": "multi_bot_connection_test",
        "results": results,
        "summary": {
            "total_bots": len(results),
            "connected": len([r for r in results if "CONNECTED" in r["status"]]),
            "failed": len([r for r in results if "CONNECTED" not in r["status"]])
        }
    }
    
    report_file = "multi_bot_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📋 Detaylı rapor: {report_file}")

if __name__ == "__main__":
    asyncio.run(main()) 