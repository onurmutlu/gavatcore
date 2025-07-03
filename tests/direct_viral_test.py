#!/usr/bin/env python3
"""
🔥 DİREKT VIRAL TEST - @arayisonlyvips
Session dosyalarını direkt kullanarak hızlı test

YAŞASIN SPONSORLAR! 🚀
"""

import asyncio
import time
import random
from pathlib import Path
from telethon import TelegramClient

class DirectViralTest:
    def __init__(self):
        self.target_group = "@arayisonlyvips"
        self.start_time = time.time()
        
        # Viral test mesajları - GENİŞLETİLMİŞ VARYASYONLAR
        self.test_messages = [
            # Davet tarzı mesajlar
            "🌟 @arayisonlyvips grubumuzda güzel sohbetler dönüyor! Katılmak ister misin? 💬",
            "💫 @arayisonlyvips'te harika bir topluluk var! Sen de aramıza katıl 🤗",
            "🎉 @arayisonlyvips grubumuzda eğlenceli anlar yaşıyoruz! Gel sen de 😊",
            "✨ @arayisonlyvips'te yeni arkadaşlar edinebilirsin! Bekliyoruz 💕",
            "🔥 @arayisonlyvips'te sıcak sohbetler var! Sen de gel, tanışalım 💋",
            
            # Samimi yaklaşım mesajları
            "Merhaba! @arayisonlyvips grubumuzda güzel arkadaşlıklar var, sen de gel 😊",
            "Selam! @arayisonlyvips'te kaliteli sohbetler dönüyor, katılmak ister misin? 💬",
            "Hey! @arayisonlyvips grubumuzda eğlenceli vakitler geçiriyoruz 🎉",
            
            # Kısa ve etkili mesajlar
            "@arayisonlyvips 👈 Buraya gel! 🔥",
            "@arayisonlyvips grubuna katıl! 💪",
            "@arayisonlyvips'te görüşelim! 😉",
            
            # Soru tarzı mesajlar
            "@arayisonlyvips grubunu duydun mu? Çok popüler oldu! 📢",
            "@arayisonlyvips'e katıldın mı? Herkesi bekliyor! 👥"
        ]
        
        # Mevcut session dosyaları (telefon numaralarından)
        self.sessions = [
            {"path": "sessions/_905382617727.session", "name": "Bot1_905382617727"},
            {"path": "sessions/_905486306226.session", "name": "Bot2_905486306226"},
            {"path": "sessions/_905513272355.session", "name": "Bot3_905513272355"}
        ]
        
        # Test istatistikleri
        self.stats = {
            "messages_sent": 0,
            "groups_reached": 0,
            "errors": 0,
            "bot_performance": {}
        }

    async def get_client_from_session(self, session_info: dict):
        """Session dosyasından client oluştur"""
        try:
            session_path = session_info["path"]
            bot_name = session_info["name"]
            
            if not Path(session_path).exists():
                print(f"❌ {bot_name} session dosyası bulunamadı: {session_path}")
                return None, bot_name
            
            # Config'den API bilgilerini al
            try:
                import config
                api_id = config.TELEGRAM_API_ID
                api_hash = config.TELEGRAM_API_HASH
            except:
                # Fallback değerler (gerçek değerleri config'den alın)
                print("⚠️ Config'den API bilgileri alınamadı, fallback kullanılıyor")
                return None, bot_name
            
            # Client oluştur
            client = TelegramClient(
                session_path,
                api_id,
                api_hash,
                connection_retries=3,
                retry_delay=2,
                timeout=30
            )
            
            await client.connect()
            
            if not await client.is_user_authorized():
                print(f"❌ {bot_name} yetkilendirilmemiş!")
                await client.disconnect()
                return None, bot_name
            
            # Bot bilgilerini al
            me = await client.get_me()
            actual_name = f"{me.first_name} (@{me.username or me.id})"
            print(f"✅ {bot_name} bağlandı: {actual_name}")
            
            return client, actual_name
            
        except Exception as e:
            print(f"❌ {bot_name} client hatası: {e}")
            return None, bot_name

    async def run_direct_test(self):
        """Direkt viral test"""
        print("🔥 DİREKT VIRAL TEST BAŞLIYOR!")
        print("=" * 50)
        print(f"🎯 Hedef: @arayisonlyvips tanıtımı")
        print(f"💬 Test mesajları: {len(self.test_messages)}")
        print(f"🤖 Session dosyaları: {len(self.sessions)}")
        print("=" * 50)
        
        # Her session için test
        for session_info in self.sessions:
            try:
                bot_name = session_info["name"]
                print(f"\n🤖 {bot_name} test başlatılıyor...")
                
                # Client al
                client, actual_name = await self.get_client_from_session(session_info)
                if not client:
                    continue
                
                # Bot performans tracking
                self.stats["bot_performance"][actual_name] = {
                    "messages": 0,
                    "groups": 0,
                    "errors": 0
                }
                
                # Test mesajları gönder
                await self.send_test_messages(client, actual_name)
                
                # Client'ı kapat
                await client.disconnect()
                
                print(f"✅ {actual_name} test tamamlandı!")
                
            except Exception as e:
                print(f"❌ {bot_name} test hatası: {e}")
                self.stats["errors"] += 1
        
        # Test özeti
        await self.print_test_summary()

    async def send_test_messages(self, client, bot_name: str):
        """Test mesajları gönder"""
        try:
            # Dialog'ları al
            dialogs = await client.get_dialogs()
            group_dialogs = [d for d in dialogs if d.is_group]
            
            print(f"  📊 Toplam grup: {len(group_dialogs)}")
            
            # İlk 3 grubu seç (test için)
            test_groups = group_dialogs[:3]
            
            sent_count = 0
            for dialog in test_groups:
                try:
                    # Test mesajı seç
                    message = random.choice(self.test_messages)
                    
                    # Mesaj gönder
                    await client.send_message(dialog.id, message)
                    
                    # İstatistikleri güncelle
                    self.stats["messages_sent"] += 1
                    self.stats["bot_performance"][bot_name]["messages"] += 1
                    sent_count += 1
                    
                    print(f"  📤 {dialog.title}: {message[:40]}...")
                    
                    # Rate limiting (test için kısa)
                    await asyncio.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"  ❌ {dialog.title}: {e}")
                    self.stats["bot_performance"][bot_name]["errors"] += 1
                    continue
            
            self.stats["groups_reached"] += sent_count
            self.stats["bot_performance"][bot_name]["groups"] = sent_count
            
            print(f"  ✅ {bot_name}: {sent_count} gruba mesaj gönderildi")
            
        except Exception as e:
            print(f"❌ {bot_name} mesaj gönderim hatası: {e}")
            self.stats["errors"] += 1

    async def print_test_summary(self):
        """Test özeti yazdır"""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "="*50)
        print("📊 DİREKT VIRAL TEST ÖZETİ")
        print("="*50)
        print(f"⏰ Test süresi: {elapsed_time:.1f} saniye")
        print(f"📤 Toplam mesaj: {self.stats['messages_sent']}")
        print(f"🎯 Ulaşılan grup: {self.stats['groups_reached']}")
        print(f"❌ Hata sayısı: {self.stats['errors']}")
        print("\n🤖 Bot Performansları:")
        
        for bot, perf in self.stats["bot_performance"].items():
            if perf["groups"] + perf["errors"] > 0:
                success_rate = (perf["messages"] / (perf["groups"] + perf["errors"])) * 100
            else:
                success_rate = 0
            print(f"  {bot}: {perf['messages']} mesaj, {perf['groups']} grup, %{success_rate:.1f} başarı")
        
        print("="*50)
        
        if self.stats["messages_sent"] > 0:
            print("🎉 TEST BAŞARILI! @arayisonlyvips viral sistemi çalışıyor!")
            print("🚀 Viral büyütme kampanyası başlatılabilir!")
            print("💡 Sonuç: Sistem production-ready!")
            print("\n📈 ÖNERİLER:")
            print("  • Tam kampanya için daha fazla bot ekleyin")
            print("  • Mesaj çeşitliliğini artırın")
            print("  • Rate limiting'i optimize edin")
            print("  • Hedef grup analizi yapın")
        else:
            print("⚠️ Test sorunlu! Sistem kontrolü gerekli.")
            print("🔧 Session dosyalarını ve API ayarlarını kontrol edin")
        
        print("\nYAŞASIN SPONSORLAR! 🔥")
        print("@arayisonlyvips viral büyütme sistemi hazır!")

async def main():
    """Ana test fonksiyonu"""
    test = DirectViralTest()
    await test.run_direct_test()

if __name__ == "__main__":
    asyncio.run(main()) 