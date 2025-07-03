#!/usr/bin/env python3
"""
🔥 BASİT VIRAL TEST - @arayisonlyvips
Config bağımlılığı olmadan hızlı test

YAŞASIN SPONSORLAR! 🚀
"""

import asyncio
import time
import random
import json
from pathlib import Path
from telethon import TelegramClient

class SimpleViralTest:
    def __init__(self):
        self.target_group = "@arayisonlyvips"
        self.start_time = time.time()
        
        # Viral test mesajları
        self.test_messages = [
            "🌟 @arayisonlyvips grubumuzda güzel sohbetler dönüyor! Katılmak ister misin? 💬",
            "💫 @arayisonlyvips'te harika bir topluluk var! Sen de aramıza katıl 🤗",
            "🎉 @arayisonlyvips grubumuzda eğlenceli anlar yaşıyoruz! Gel sen de 😊",
            "✨ @arayisonlyvips'te yeni arkadaşlar edinebilirsin! Bekliyoruz 💕",
            "🔥 @arayisonlyvips'te sıcak sohbetler var! Sen de gel, tanışalım 💋"
        ]
        
        # Test istatistikleri
        self.stats = {
            "messages_sent": 0,
            "groups_reached": 0,
            "errors": 0,
            "bot_performance": {}
        }

    def load_bot_profile(self, bot_username: str):
        """Bot profilini yükle"""
        try:
            profile_path = Path(f"data/profiles/{bot_username}.json")
            if profile_path.exists():
                with open(profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Profil yükleme hatası {bot_username}: {e}")
            return None

    async def get_bot_client(self, bot_username: str):
        """Bot client'ını al"""
        try:
            # Profil yükle
            profile = self.load_bot_profile(bot_username)
            if not profile:
                print(f"❌ {bot_username} profili bulunamadı!")
                return None
            
            # Session path
            phone = profile.get("phone", "")
            session_name = phone.replace("+", "_")
            session_path = f"sessions/{session_name}.session"
            
            if not Path(session_path).exists():
                print(f"❌ {bot_username} session dosyası bulunamadı: {session_path}")
                return None
            
            # Client oluştur
            client = TelegramClient(
                session_path,
                profile.get("api_id"),
                profile.get("api_hash"),
                connection_retries=3,
                retry_delay=2,
                timeout=30
            )
            
            await client.connect()
            
            if not await client.is_user_authorized():
                print(f"❌ {bot_username} yetkilendirilmemiş!")
                await client.disconnect()
                return None
            
            # Bot bilgilerini al
            me = await client.get_me()
            print(f"✅ {bot_username} bağlandı: {me.first_name} (@{me.username or me.id})")
            
            return client
            
        except Exception as e:
            print(f"❌ {bot_username} client hatası: {e}")
            return None

    async def run_simple_test(self):
        """Basit viral test"""
        print("🔥 BASİT VIRAL TEST BAŞLIYOR!")
        print("=" * 50)
        print(f"🎯 Hedef: @arayisonlyvips tanıtımı")
        print(f"💬 Test mesajları: {len(self.test_messages)}")
        print("=" * 50)
        
        # Mevcut profilleri kontrol et
        profiles_dir = Path("data/profiles")
        if not profiles_dir.exists():
            print("❌ Profiles klasörü bulunamadı!")
            return
        
        profile_files = list(profiles_dir.glob("*.json"))
        test_bots = [f.stem for f in profile_files[:3]]  # İlk 3 bot
        
        print(f"🤖 Test botları: {test_bots}")
        print()
        
        # Her bot için test
        for bot_username in test_bots:
            try:
                print(f"🤖 {bot_username} test başlatılıyor...")
                
                # Client al
                client = await self.get_bot_client(bot_username)
                if not client:
                    continue
                
                # Bot performans tracking
                self.stats["bot_performance"][bot_username] = {
                    "messages": 0,
                    "groups": 0,
                    "errors": 0
                }
                
                # Test mesajları gönder
                await self.send_test_messages(client, bot_username)
                
                # Client'ı kapat
                await client.disconnect()
                
                print(f"✅ {bot_username} test tamamlandı!")
                print()
                
            except Exception as e:
                print(f"❌ {bot_username} test hatası: {e}")
                self.stats["errors"] += 1
        
        # Test özeti
        await self.print_test_summary()

    async def send_test_messages(self, client, bot_username: str):
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
                    self.stats["bot_performance"][bot_username]["messages"] += 1
                    sent_count += 1
                    
                    print(f"  📤 {dialog.title}: {message[:40]}...")
                    
                    # Rate limiting (test için kısa)
                    await asyncio.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"  ❌ {dialog.title}: {e}")
                    self.stats["bot_performance"][bot_username]["errors"] += 1
                    continue
            
            self.stats["groups_reached"] += sent_count
            self.stats["bot_performance"][bot_username]["groups"] = sent_count
            
            print(f"  ✅ {bot_username}: {sent_count} gruba mesaj gönderildi")
            
        except Exception as e:
            print(f"❌ {bot_username} mesaj gönderim hatası: {e}")
            self.stats["errors"] += 1

    async def print_test_summary(self):
        """Test özeti yazdır"""
        elapsed_time = time.time() - self.start_time
        
        print("="*50)
        print("📊 BASİT VIRAL TEST ÖZETİ")
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
            print("🎉 TEST BAŞARILI! Viral sistem çalışıyor!")
            print("🚀 @arayisonlyvips viral büyütme sistemi hazır!")
            print("💡 Tam kampanya için sistemleri optimize edin")
        else:
            print("⚠️ Test sorunlu! Sistem kontrolü gerekli.")
            print("🔧 Session dosyalarını ve profilleri kontrol edin")
        
        print("\nYAŞASIN SPONSORLAR! 🔥")

async def main():
    """Ana test fonksiyonu"""
    test = SimpleViralTest()
    await test.run_simple_test()

if __name__ == "__main__":
    asyncio.run(main()) 