#!/usr/bin/env python3
"""
Telegram Client Kullanım Örnekleri
===================================

Telegram Client modülünün praktik kullanım senaryolarını gösterir.
"""

import asyncio
import json
from datetime import datetime, timedelta
from gavatcore_engine.telegram_client import (
    TelegramClientManager, TelegramClientPool, ClientConfig,
    ConnectionStatus, MessageResult, RetryConfig
)
from gavatcore_engine.redis_state import redis_state


async def ornek_1_basit_client():
    """Örnek 1: Basit Telegram client kullanımı."""
    print("📱 Örnek 1: Basit Telegram Client")
    
    # Client konfigürasyonu
    config = ClientConfig(
        session_name="lara_bot",
        api_id=12345678,  # Gerçek API ID
        api_hash="your_api_hash_here",  # Gerçek API hash
        phone="+905382617727",  # Lara'nın telefonu
        device_model="GavatCore Lara Bot",
        app_version="GavatCore v1.0"
    )
    
    # Client oluştur ve başlat
    client_manager = TelegramClientManager(config)
    
    try:
        success = await client_manager.initialize()
        
        if success:
            print("✅ Client başarıyla bağlandı")
            
            # Kullanıcı bilgilerini al
            user_info = await client_manager.get_me()
            print(f"👤 Bot: @{user_info.username} ({user_info.id})")
            
            # Basit mesaj gönder
            result = await client_manager.send_message(
                entity="me",  # Kendine gönder (Saved Messages)
                message="🌹 Merhaba! Ben Lara, GavatCore sistemi üzerinden yazıyorum!",
                parse_mode="html"
            )
            
            if result.success:
                print(f"✅ Mesaj gönderildi: ID {result.message_id}")
            else:
                print(f"❌ Mesaj gönderilemedi: {result.error}")
            
        else:
            print("❌ Client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_2_grup_mesajlama():
    """Örnek 2: Grup mesajlaması ve formatting."""
    print("👥 Örnek 2: Grup Mesajlaması")
    
    config = ClientConfig(
        session_name="geisha_bot",
        api_id=12345678,
        api_hash="your_api_hash_here",
        phone="+905486306226",  # Geisha'nın telefonu
        device_model="GavatCore Geisha Bot"
    )
    
    client_manager = TelegramClientManager(config)
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # Grup ID'si (gerçek grup ID'si kullanın)
            group_id = -1001234567890
            
            # Formatlanmış mesaj
            message = """
<b>🎭 Geisha Bot Aktif!</b>

<i>Özellikler:</i>
• 🤖 Akıllı mesajlaşma
• 🛡️ Spam koruması
• ⏰ Zamanlama sistemi
• 📊 Analitik takip

<code>Sistem: GavatCore Engine v1.0</code>
<code>Zaman: {}</code>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            result = await client_manager.send_message(
                entity=group_id,
                message=message,
                parse_mode="html",
                silent=True  # Sessiz gönderim
            )
            
            print(f"📤 Grup mesajı: {result.result.value}")
            
        else:
            print("❌ Geisha client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_3_retry_ve_hata_yonetimi():
    """Örnek 3: Retry mekanizması ve hata yönetimi."""
    print("🔄 Örnek 3: Retry ve Hata Yönetimi")
    
    config = ClientConfig(
        session_name="retry_test_bot",
        api_id=12345678,
        api_hash="your_api_hash_here",
        phone="+905551234567"
    )
    
    client_manager = TelegramClientManager(config)
    
    # Özel retry konfigürasyonu
    client_manager.retry_config = RetryConfig(
        max_retries=5,           # 5 kez deneme
        base_delay=1.0,          # 1 saniye başlangıç
        max_delay=30.0,          # Maksimum 30 saniye
        exponential_base=2.0,    # Exponential backoff
        jitter=True,             # Rastgele gecikme ekle
        retry_on_flood=True,     # Flood wait'te retry
        retry_on_server_error=True,
        retry_on_network_error=True
    )
    
    print(f"⚙️ Retry config: {client_manager.retry_config.max_retries} max retries")
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # Hata durumlarını test et
            test_cases = [
                {
                    "name": "Normal mesaj",
                    "entity": "me",
                    "message": "✅ Normal test mesajı"
                },
                {
                    "name": "Uzun mesaj (4096+ karakter)",
                    "entity": "me", 
                    "message": "🔄 " * 2000  # Çok uzun mesaj
                },
                {
                    "name": "Geçersiz entity",
                    "entity": "nonexistent_user_12345",
                    "message": "❌ Bu mesaj başarısız olmalı"
                }
            ]
            
            for test in test_cases:
                print(f"\n🧪 Test: {test['name']}")
                
                result = await client_manager.send_message(
                    entity=test["entity"],
                    message=test["message"]
                )
                
                print(f"   📊 Sonuç: {result.result.value}")
                if result.error:
                    print(f"   ❌ Hata: {result.error}")
                if result.retry_after:
                    print(f"   ⏱️ Retry after: {result.retry_after}s")
            
        else:
            print("❌ Test client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_4_client_pool():
    """Örnek 4: Multiple client pool kullanımı."""
    print("🏊 Örnek 4: Client Pool Yönetimi")
    
    pool = TelegramClientPool()
    
    # Birden fazla bot config'i
    bot_configs = [
        {
            "session_name": "lara_pool",
            "phone": "+905382617727",
            "device_model": "Pool Lara Bot"
        },
        {
            "session_name": "geisha_pool", 
            "phone": "+905486306226",
            "device_model": "Pool Geisha Bot"
        },
        {
            "session_name": "backup_pool",
            "phone": "+905551234567",
            "device_model": "Pool Backup Bot"
        }
    ]
    
    # Pool'a client'ları ekle
    for bot_config in bot_configs:
        config = ClientConfig(
            session_name=bot_config["session_name"],
            api_id=12345678,
            api_hash="your_api_hash_here",
            phone=bot_config["phone"],
            device_model=bot_config["device_model"]
        )
        
        print(f"🔄 Pool'a ekleniyor: {config.session_name}")
        success = await pool.add_client(config)
        
        if success:
            print(f"✅ {config.session_name} pool'a eklendi")
        else:
            print(f"❌ {config.session_name} eklenemedi")
    
    # Pool istatistikleri
    stats = await pool.get_pool_stats()
    print(f"\n📊 Pool Stats:")
    print(f"   Total clients: {stats['total_clients']}")
    print(f"   Connected clients: {stats['connected_clients']}")
    
    # Round-robin mesaj gönderimi
    print(f"\n🔄 Round-robin mesaj gönderimi:")
    
    for i in range(5):
        result = await pool.send_message(
            entity="me",
            message=f"🏊 Pool mesajı #{i+1} - Round robin test"
        )
        
        print(f"   📤 Mesaj {i+1}: {result.result.value}")
        if result.error:
            print(f"      ❌ Hata: {result.error}")
    
    # Belirli client ile mesaj gönderimi
    result = await pool.send_message(
        entity="me",
        message="🎯 Belirli client ile gönderilen mesaj",
        session_name="lara_pool"  # Belirli client
    )
    
    print(f"🎯 Belirli client: {result.result.value}")
    
    # Pool'u kapat
    await pool.shutdown()
    print("🧹 Pool kapatıldı")


async def ornek_5_gelismis_mesaj_ozellikleri():
    """Örnek 5: Gelişmiş mesaj özellikleri."""
    print("✨ Örnek 5: Gelişmiş Mesaj Özellikleri")
    
    config = ClientConfig(
        session_name="advanced_bot",
        api_id=12345678,
        api_hash="your_api_hash_here", 
        phone="+905382617727"
    )
    
    client_manager = TelegramClientManager(config)
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # 1. Zamanlanmış mesaj
            future_time = datetime.utcnow() + timedelta(minutes=1)
            result1 = await client_manager.send_message(
                entity="me",
                message="⏰ Bu mesaj 1 dakika sonra gönderildi!",
                schedule=future_time
            )
            print(f"📅 Zamanlanmış mesaj: {result1.result.value}")
            
            # 2. Sessiz mesaj
            result2 = await client_manager.send_message(
                entity="me",
                message="🔇 Bu sessiz bir mesajdır (bildirim yok)",
                silent=True
            )
            print(f"🔇 Sessiz mesaj: {result2.result.value}")
            
            # 3. Markdown formatı
            markdown_msg = """
**Bold text** ve *italic text*

`Inline code` örneği

```python
# Code block örneği
def hello():
    return "Merhaba GavatCore!"
```

[Link örneği](https://github.com)
            """
            
            result3 = await client_manager.send_message(
                entity="me",
                message=markdown_msg,
                parse_mode="markdown"
            )
            print(f"📝 Markdown mesaj: {result3.result.value}")
            
            # 4. Link preview'siz mesaj
            result4 = await client_manager.send_message(
                entity="me",
                message="🔗 Bu mesajda link preview yok: https://example.com",
                link_preview=False
            )
            print(f"🔗 Link preview'siz: {result4.result.value}")
            
        else:
            print("❌ Advanced client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_6_mesaj_alma_ve_analiz():
    """Örnek 6: Mesaj alma ve analiz."""
    print("📥 Örnek 6: Mesaj Alma ve Analiz")
    
    config = ClientConfig(
        session_name="reader_bot",
        api_id=12345678,
        api_hash="your_api_hash_here",
        phone="+905382617727"
    )
    
    client_manager = TelegramClientManager(config)
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # Son mesajları al (Saved Messages'dan)
            messages = await client_manager.get_messages(
                entity="me",
                limit=10
            )
            
            print(f"📥 {len(messages)} mesaj alındı")
            
            for i, msg in enumerate(messages[:5]):  # İlk 5'ini göster
                if msg.message:
                    print(f"   {i+1}. {msg.date}: {msg.message[:50]}...")
                else:
                    print(f"   {i+1}. {msg.date}: [Media/Special message]")
            
            # Entity bilgisi al
            me = await client_manager.get_entity("me")
            if me:
                print(f"\n👤 Bot bilgisi:")
                print(f"   ID: {me.id}")
                print(f"   Username: @{me.username}")
                print(f"   Ad: {me.first_name}")
                if hasattr(me, 'phone'):
                    print(f"   Telefon: {me.phone}")
            
        else:
            print("❌ Reader client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_7_event_handling():
    """Örnek 7: Event handling ve real-time mesaj dinleme."""
    print("👂 Örnek 7: Event Handling")
    
    config = ClientConfig(
        session_name="listener_bot",
        api_id=12345678,
        api_hash="your_api_hash_here",
        phone="+905382617727"
    )
    
    client_manager = TelegramClientManager(config)
    
    # Custom message handler
    async def on_new_message(event):
        sender = await event.get_sender()
        chat = await event.get_chat()
        
        print(f"📨 Yeni mesaj alındı:")
        print(f"   Gönderen: {sender.username if sender.username else sender.first_name}")
        print(f"   Chat: {chat.title if hasattr(chat, 'title') else 'Private'}")
        print(f"   Mesaj: {event.raw_text[:100]}...")
    
    # Custom disconnect handler
    async def on_disconnect():
        print("🔌 Client bağlantısı kesildi!")
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # Event handler'ları ekle
            client_manager.add_message_handler(on_new_message)
            client_manager.add_disconnect_handler(on_disconnect)
            
            print("👂 Event listener'lar aktif")
            print("💡 Bu bot artık gelen mesajları dinliyor...")
            print("📝 Test için kendinize bir mesaj gönderin")
            
            # Test mesajı gönder
            await client_manager.send_message(
                entity="me",
                message="🧪 Bu bir test mesajıdır - event handler test ediyor"
            )
            
            # 10 saniye dinle
            print("⏱️ 10 saniye dinleniyor...")
            await asyncio.sleep(10)
            
        else:
            print("❌ Listener client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def ornek_8_istatistikler_ve_monitoring():
    """Örnek 8: İstatistikler ve monitoring."""
    print("📊 Örnek 8: İstatistikler ve Monitoring")
    
    config = ClientConfig(
        session_name="stats_bot",
        api_id=12345678,
        api_hash="your_api_hash_here",
        phone="+905382617727"
    )
    
    client_manager = TelegramClientManager(config)
    
    try:
        success = await client_manager.initialize()
        
        if success:
            # Başlangıç stats
            initial_stats = await client_manager.get_stats()
            print("📊 Başlangıç İstatistikleri:")
            print(f"   Status: {initial_stats['connection_status']}")
            print(f"   Gönderilen mesaj: {initial_stats['messages_sent']}")
            print(f"   Başarısız mesaj: {initial_stats['messages_failed']}")
            
            # Birkaç mesaj gönder
            for i in range(5):
                result = await client_manager.send_message(
                    entity="me",
                    message=f"📊 İstatistik test mesajı #{i+1}"
                )
                print(f"   📤 Mesaj {i+1}: {result.result.value}")
                await asyncio.sleep(1)  # Rate limiting için
            
            # Final stats
            final_stats = await client_manager.get_stats()
            print("\n📊 Final İstatistikler:")
            print(f"   Gönderilen mesaj: {final_stats['messages_sent']}")
            print(f"   Başarısız mesaj: {final_stats['messages_failed']}")
            print(f"   Flood wait'ler: {final_stats['flood_waits']}")
            print(f"   Yeniden bağlanma: {final_stats['reconnections']}")
            
            if final_stats['uptime_seconds']:
                print(f"   Uptime: {final_stats['uptime_seconds']:.0f} saniye")
            
            if final_stats['last_activity']:
                print(f"   Son aktivite: {final_stats['last_activity']}")
            
            # Redis'e istatistikleri kaydet
            try:
                await redis_state.connect()
                await redis_state.hset(
                    "telegram_stats",
                    config.session_name,
                    json.dumps(final_stats, default=str)
                )
                print("✅ İstatistikler Redis'e kaydedildi")
            except Exception as e:
                print(f"❌ Redis kayıt hatası: {e}")
            
        else:
            print("❌ Stats client bağlanamadı")
            
    finally:
        await client_manager.disconnect()


async def main():
    """Ana demo fonksiyonu."""
    print("🚀 Telegram Client Kullanım Örnekleri")
    print("="*60)
    
    # Redis bağlantısını test et
    try:
        await redis_state.connect()
        print("✅ Redis bağlantısı kuruldu\n")
    except Exception as e:
        print(f"⚠️ Redis bağlantısı başarısız: {e}")
        print("⚠️ Redis gerektiren örnekler çalışmayabilir\n")
    
    # Örnekleri sırayla çalıştır
    examples = [
        ("Basit Client", ornek_1_basit_client),
        ("Grup Mesajlaması", ornek_2_grup_mesajlama),
        ("Retry ve Hata Yönetimi", ornek_3_retry_ve_hata_yonetimi),
        ("Client Pool", ornek_4_client_pool),
        ("Gelişmiş Mesaj Özellikleri", ornek_5_gelismis_mesaj_ozellikleri),
        ("Mesaj Alma ve Analiz", ornek_6_mesaj_alma_ve_analiz),
        ("Event Handling", ornek_7_event_handling),
        ("İstatistikler ve Monitoring", ornek_8_istatistikler_ve_monitoring),
    ]
    
    for i, (name, example_func) in enumerate(examples):
        print(f"{i+1}️⃣ {name}")
        print("-" * 40)
        
        try:
            await example_func()
            print("✅ Örnek tamamlandı\n")
        except Exception as e:
            print(f"❌ Örnek hatası: {e}\n")
        
        # Örnekler arası bekleme
        if i < len(examples) - 1:
            await asyncio.sleep(2)
    
    # Cleanup
    try:
        await redis_state.disconnect()
        print("🧹 Cleanup tamamlandı")
    except:
        pass
    
    print("\n" + "="*60)
    print("💡 Not: Bu örneklerin çalışması için gerçek Telegram API")
    print("   credentials gereklidir. config.py dosyanızda doğru")
    print("   API_ID ve API_HASH değerlerinin olduğundan emin olun.")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc() 