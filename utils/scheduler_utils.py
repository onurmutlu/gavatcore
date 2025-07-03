# utils/scheduler_utils.py

import asyncio
import random
import json
from pathlib import Path
from core.profile_loader import load_profile, get_all_profiles
from utils.log_utils import log_event
from telethon.errors import ChatWriteForbiddenError

DEFAULT_INTERVAL_SECONDS = (60, 180)  # 1-3 dakika (daha aktif spam)
BANNED_GROUP_IDS = set()
DEFAULT_MESSAGES_FILE = Path("data/group_spam_messages.json")

def load_default_spam_messages() -> list:
    """
    Default grup spam mesajlarını yükler.
    data/group_spam_messages.json dosyasında _template.engaging_messages varsa onu, yoksa sabit mesajları döner.
    """
    if DEFAULT_MESSAGES_FILE.exists():
        try:
            with open(DEFAULT_MESSAGES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                msgs = data.get("_template", {}).get("engaging_messages", [])
                if isinstance(msgs, list) and msgs:
                    return msgs
        except Exception as e:
            print(f"⚠️ group_spam_messages.json okunamadı: {e}")
    return [
        "💖 Selam yakışıklı! VIP grubum doluyor 😘",
        "🎀 Bugün benimle daha yakın olmak ister misin? DM 💌",
        "😈 Şımarmaya hazır mısın? VIP'e bekliyorum..."
    ]

async def spam_loop(client):
    """
    Güvenli spam döngüsü - Anti-spam koruması ile
    """
    print("🛡️ GÜVENLİ SPAM LOOP BAŞLATILIYOR!")
    
    # Session dosyasından username çıkar
    session_filename = getattr(client.session, "filename", None)
    if session_filename:
        # sessions/bot_geishaniz.session -> bot_geishaniz
        username = Path(session_filename).stem
    else:
        username = getattr(client, "username", None)
    
    if not username:
        print("⚠️ Client username bulunamadı.")
        return

    print(f"🔄 Güvenli spam loop başlatılıyor: {username}")
    log_event(username, f"🔄 Güvenli spam loop başlatılıyor: {username}")

    # Profili yükle
    profile = None
    try:
        # Direkt JSON dosyasından yükle
        profile_path = Path(f"data/personas/{username}.json")
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
        else:
            print(f"⚠️ Profil dosyası bulunamadı: {profile_path}")
            log_event(username, f"⚠️ Profil dosyası bulunamadı: {profile_path}")
            return
    except Exception as e:
        print(f"💥 Profil yükleme hatası: {e}")
        log_event(username, f"💥 Profil yükleme hatası (spam_loop): {e}")
        return

    if not profile or not profile.get("autospam"):
        print(f"ℹ️ {username} için otomatik spam aktif değil.")
        log_event(username, "ℹ️ Otomatik spam aktif değil.")
        return

    print(f"▶️ {username} için güvenli spam başlatıldı.")
    log_event(username, "▶️ Güvenli spam başlatıldı.")
    
    # Anti-spam guard ve safe spam handler'ı import et
    from utils.anti_spam_guard import anti_spam_guard
    from handlers.safe_spam_handler import safe_spam_handler
    from core.account_monitor import account_monitor
    from handlers.gpt_messaging_handler import gpt_messaging_handler
    from utils.dynamic_spam_scheduler import start_dynamic_spam_system
    
    # Hesap izlemeyi başlat
    await account_monitor.start_monitoring(client, username)
    
    # GPT messaging handler'ı başlat
    await gpt_messaging_handler.start_gpt_messaging_loop(client, username, profile)
    
    # Güvenli spam handler'ı başlat
    await safe_spam_handler.start_safe_spam_loop(client, username, profile)
    
    # Dinamik spam sistemini başlat
    await start_dynamic_spam_system(client, username, profile)
    
    # Tüm system botları için adaptif spam sistemi
    if profile.get("group_spam_enabled"):
        from utils.adaptive_spam_scheduler import start_adaptive_spam
        await start_adaptive_spam(client, username, profile)
    
    # @arayisvips grup davet kampanyası başlat
    from utils.group_invite_strategy import start_group_invite_campaign
    await start_group_invite_campaign(client, username)
    
    log_event(username, "🛡️ Güvenli spam sistemi + GPT entegrasyonu + Dinamik spam scheduler + Grup davet kampanyası aktif")
    
    # Sonsuz bekle (handler'lar kendi döngülerini yönetir)
    while True:
        await asyncio.sleep(3600)  # 1 saat bekle

    # Test mesajı
    print(f"🧪 {username} spam loop test başlıyor...")
    log_event(username, "🧪 Spam loop test başlıyor...")

    while True:
        # Dinamik bekleme aralığı (dilersen burada profile'a özel cool-down da ekleyebilirsin)
        wait_time = random.uniform(*DEFAULT_INTERVAL_SECONDS)
        print(f"⏰ {username} spam loop {wait_time:.1f} saniye bekliyor...")
        log_event(username, f"⏰ Spam loop {wait_time:.1f} saniye bekliyor...")
        await asyncio.sleep(wait_time)
        
        print(f"🚀 {username} spam döngüsü başlıyor...")
        log_event(username, f"🚀 Spam döngüsü başlıyor...")

        # Her döngüde profile güncelle (otospam iptal edildi mi kontrol)
        try:
            profile_path = Path(f"data/personas/{username}.json")
            if profile_path.exists():
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
            else:
                log_event(username, f"💥 Profil dosyası kayboldu: {profile_path}")
                break
        except Exception as e:
            log_event(username, f"💥 Profil reload hatası (spam_loop): {e}")
            break

        if not profile or not profile.get("autospam"):
            log_event(username, "🛑 Otomatik spam kapatıldı, döngü durduruldu.")
            break

        # Mesaj havuzunu çek - karışık mesaj sistemi ile
        from utils.smart_reply import smart_reply
        
        bot_engaging_messages = profile.get("engaging_messages")
        if not bot_engaging_messages or not isinstance(bot_engaging_messages, list):
            bot_engaging_messages = profile.get("group_spam_templates", [])
        
        # Karışık mesaj sistemi kullan
        if bot_engaging_messages:
            # Her döngüde farklı mesajlar için liste oluştur
            messages = []
            for _ in range(10):  # 10 farklı mesaj hazırla
                mixed_message = smart_reply.get_mixed_messages(bot_engaging_messages, "engaging")
                messages.append(mixed_message)
        else:
            # Fallback: sadece genel havuz
            messages = load_default_spam_messages()
        
        # Mesaj sayısını kontrol et
        if not messages:
            log_event(username, "⚠️ Hiç spam mesajı bulunamadı, döngü atlanıyor")
            continue

        sent_count = 0
        group_count = 0

        try:
            print(f"🔍 {username} için dialog'ları alınıyor...")
            log_event(username, f"🔍 Dialog'ları alınıyor...")
            
            dialogs = await client.get_dialogs()
            print(f"📋 {username} için {len(dialogs)} dialog bulundu")
            log_event(username, f"📋 {len(dialogs)} dialog bulundu")

            for dialog in dialogs:
                # Sadece aktif, gruplar ve engelli olmayan gruplar
                if not dialog.is_group:
                    continue
                    
                group_count += 1
                
                if dialog.id in BANNED_GROUP_IDS:
                    continue

                try:
                    # Her grup için ayrı rastgele mesaj seç
                    message = random.choice(messages)
                    print(f"📤 {username} -> [{dialog.name}]: {message[:50]}...")
                    await client.send_message(dialog.id, message)
                    log_event(username, f"📤 [{dialog.name}] mesaj gönderildi: {message}")
                    sent_count += 1
                    # Her mesaj arası daha uzun bekleme (rate limiting için)
                    await asyncio.sleep(random.uniform(3, 8))

                except ChatWriteForbiddenError:
                    BANNED_GROUP_IDS.add(dialog.id)
                    print(f"🚫 {username} -> [{dialog.name}] yazma engeli!")
                    log_event(username, f"🚫 Yazma engeli (banlandı): {dialog.name}")
                except Exception as e:
                    print(f"⚠️ {username} -> [{dialog.name}] hata: {e}")
                    log_event(username, f"⚠️ Mesaj gönderim hatası [{dialog.name}]: {e}")

            print(f"✅ {username}: {sent_count}/{group_count} gruba spam gönderildi")
            log_event(username, f"✅ {sent_count}/{group_count} gruba spam mesajı gönderildi.")

        except Exception as e:
            print(f"💥 {username} spam döngüsü hatası: {e}")
            log_event(username, f"💥 Spam döngüsü genel hatası: {e}")
            # Çok ciddi hatalarda döngüyü kırma, devam etsin
            await asyncio.sleep(10)

# ➕ Geliştirme için öneriler:
# - Spam döngüsünü dışarıdan başlat/durdur (state ile), istersen pause/resume mekanizması ekle.
# - Her grup için ayrı spam-cooldown zamanı ekle, message cooldownu profile'dan çek.
# - Logları merkezi bir yere (db, elasticsearch) gönderebilirsin.
# - Mesajları randomize etmek için message template'lerine dinamik alanlar ekleyebilirsin.
