import json
import os
from datetime import datetime, timedelta
from telethon import events
from config import GAVATCORE_ADMIN_ID
from core.license_checker import LicenseChecker
from core.profile_loader import (
    load_profile, update_profile,
    get_all_profiles, get_profile_path,
    save_profile
)
from utils.log_utils import get_logs, log_event, search_logs, get_log_stats
from core.gavat_client import is_session_available
from core.session_manager import create_session_flow, terminate_session
from core.profile_generator import generate_bot_persona, generate_showcu_persona

checker = LicenseChecker()

# Role-based komut sistemi
COMMANDS = [
    {
        "command": "/lisans",
        "desc": "🔓 Kullanıcı lisansını aktif eder",
        "roles": ["admin"]
    },
    {
        "command": "/kapat",
        "desc": "🔒 Kullanıcı lisansını devre dışı bırakır",
        "roles": ["admin"]
    },
    {
        "command": "/durum",
        "desc": "📌 Kullanıcı durumunu kontrol eder",
        "roles": ["admin"]
    },
    {
        "command": "/mod",
        "desc": "🧠 Yanıt modunu değiştirir",
        "roles": ["admin"]
    },
    {
        "command": "/profil",
        "desc": "👤 Profil bilgilerini gösterir",
        "roles": ["admin", "producer"]
    },
    {
        "command": "/panel",
        "desc": "🛠️ GPT kontrol panelini açar",
        "roles": ["admin"]
    },
    {
        "command": "/mesaj",
        "desc": "📬 Kullanıcıya mesaj gönderir",
        "roles": ["admin"]
    },
    {
        "command": "/klonla",
        "desc": "🔄 Profili kopyalar",
        "roles": ["admin"]
    },
    {
        "command": "/bots",
        "desc": "🤖 Aktif botları listeler",
        "roles": ["admin"]
    },
    {
        "command": "/list_users",
        "desc": "👥 Kayıtlı kullanıcıları listeler",
        "roles": ["admin"]
    },
    {
        "command": "/log",
        "desc": "🗂 Log kayıtlarını gösterir",
        "roles": ["admin"]
    },
    {
        "command": "/session_durum",
        "desc": "📡 Oturum durumunu kontrol eder",
        "roles": ["admin"]
    },
    {
        "command": "/durum_ozet",
        "desc": "📊 Sistem özetini gösterir",
        "roles": ["admin"]
    },
    {
        "command": "/demo_uyarilar",
        "desc": "🚨 Demo süresi dolmuş kullanıcıları gösterir",
        "roles": ["admin"]
    },
    {
        "command": "/demo_temizle",
        "desc": "🔄 Demo uyarısını temizler",
        "roles": ["admin"]
    },
    {
        "command": "/session_ac",
        "desc": "📱 Yeni session oluşturur",
        "roles": ["admin"]
    },
    {
        "command": "/showcu_ekle",
        "desc": "👩‍💻 Yeni içerik üretici ekler",
        "roles": ["admin"]
    },
    {
        "command": "/bot_ekle",
        "desc": "🤖 Yeni bot ekler",
        "roles": ["admin"]
    },
    {
        "command": "/force_dur",
        "desc": "⛔️ Uzaktan spam durdurur",
        "roles": ["admin"]
    },
    {
        "command": "/force_devam",
        "desc": "▶️ Uzaktan spam başlatır",
        "roles": ["admin"]
    },
    {
        "command": "/logs",
        "desc": "🗒️ Detaylı log görüntüler",
        "roles": ["admin"]
    },
    {
        "command": "/logara",
        "desc": "🔍 Log dosyasında arama yapar",
        "roles": ["admin"]
    },
    {
        "command": "/log_stats",
        "desc": "📊 Log istatistiklerini gösterir",
        "roles": ["admin"]
    },
    {
        "command": "/terminate_session",
        "desc": "🔥 Oturum sonlandırır",
        "roles": ["admin"]
    },
    {
        "command": "/backup",
        "desc": "💾 Sistem yedeği alır",
        "roles": ["admin"]
    },
    {
        "command": "/show_menu_list",
        "desc": "🎭 Show menülerini listeler",
        "roles": ["admin"]
    },
    {
        "command": "/show_menu_view",
        "desc": "👁️ Show menüsünü görüntüler",
        "roles": ["admin"]
    },
    {
        "command": "/show_menu_update",
        "desc": "✏️ Show menüsünü günceller",
        "roles": ["admin"]
    },
    {
        "command": "/help",
        "desc": "ℹ️ Yardım ve komut listesi",
        "roles": ["admin", "producer", "client"]
    },
    {
        "command": "/yardım",
        "desc": "ℹ️ Yardım ve destek",
        "roles": ["producer", "client"]
    },
    {
        "command": "/start",
        "desc": "👋 Sistemi başlat",
        "roles": ["producer", "client"]
    },
    {
        "command": "/menü",
        "desc": "📝 Hizmet menüsü",
        "roles": ["producer", "client"]
    },
    {
        "command": "/fiyat",
        "desc": "💸 Fiyat listesi",
        "roles": ["producer", "client"]
    },
    {
        "command": "/iban",
        "desc": "💳 IBAN & Papara bilgileri",
        "roles": ["producer", "client"]
    }
]

def get_user_role(user_id):
    """Kullanıcının rolünü belirler"""
    try:
        # Admin kontrolü
        if str(user_id) == str(GAVATCORE_ADMIN_ID):
            return "admin"
        
        # Profil kontrolü
        from core.profile_loader import load_profile
        try:
            profile = load_profile(str(user_id))
            user_type = profile.get("type", "client")
            
            # Profil tipine göre rol mapping
            if user_type == "bot":
                return "producer"
            elif user_type == "user":
                return "producer"
            else:
                return "client"
        except:
            # Profil yoksa client
            return "client"
            
    except Exception as e:
        return "client"

def get_available_commands(user_id):
    """Kullanıcının erişebileceği komutları döndürür"""
    role = get_user_role(user_id)
    available_cmds = [c for c in COMMANDS if role in c["roles"]]
    return available_cmds

def export_botfather_commands_for_role(role):
    """BotFather için komut listesi export eder"""
    cmds = [c for c in COMMANDS if role in c["roles"]]
    return "\n".join([f"{c['command']} - {c['desc']}" for c in cmds])

async def handle_admin_command(bot, event):
    if event.sender_id != int(GAVATCORE_ADMIN_ID):
        await event.respond("⛔️ Bu komut sadece admin tarafından kullanılabilir.")
        return

    message = event.raw_text.strip()
    args = message.split()
    command = args[0].lower()

    # ✅ /lisans [user_id] [gün]
    if command == "/lisans":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /lisans [user_id] [gün(sayısı)]")
            return
        user_id = args[1]
        days = int(args[2]) if len(args) > 2 else 30
        checker.activate_license(user_id, days=days)
        await event.respond(f"✅ Kullanıcı {user_id} için lisans {days} gün uzatıldı/aktifleştirildi.")
        log_event(user_id, f"🔓 Lisans aktif/güncellendi (admin, {days} gün).")

    # ❌ /kapat [user_id]
    elif command == "/kapat":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /kapat [user_id]")
            return
        user_id = args[1]
        checker.deactivate_license(user_id)
        await event.respond(f"🔒 Kullanıcı {user_id} devre dışı bırakıldı.")
        log_event(user_id, "🔒 Lisans devre dışı bırakıldı (admin).")

    # 🔍 /durum [user_id]
    elif command == "/durum":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /durum [user_id]")
            return
        user_id = args[1]
        status = checker.get_license_status(user_id)
        await event.respond(f"📌 Kullanıcı {user_id} durumu: `{status}`")

    # ✨ /mod [user_id] [manual|gpt|hybrid|manualplus]
    elif command == "/mod":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /mod [user_id] [mod]")
            return
        user_id, new_mode = args[1], args[2]
        update_profile(str(user_id), {"reply_mode": new_mode})
        await event.respond(f"✅ Yanıt modu `{new_mode}` olarak güncellendi.")
        log_event(user_id, f"Yanıt modu {new_mode} olarak ayarlandı (admin).")

    # 📄 /profil [user_id]
    elif command == "/profil":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /profil [user_id]")
            return
        user_id = args[1]
        try:
            profile = load_profile(user_id)
            profile_str = json.dumps(profile, indent=2, ensure_ascii=False)
            if len(profile_str) > 3800:
                profile_str = profile_str[:3800] + "\n...\n"
            await event.respond(f"👤 Profil JSON:\n```json\n{profile_str}```", parse_mode="markdown")
        except Exception as e:
            await event.respond(f"❌ Profil bulunamadı: {user_id}\n{e}")

    # 📬 /mesaj [user_id] mesaj metni...
    elif command == "/mesaj":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /mesaj [user_id] mesaj...")
            return
        user_id = args[1]
        msg = " ".join(args[2:])
        await bot.send_message(user_id, msg)
        await event.respond(f"✅ Mesaj gönderildi.")
        log_event(user_id, f"📨 Admin mesajı gönderildi: {msg}")

    # 🔄 /klonla [kaynak_id] [hedef_id]
    elif command == "/klonla":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /klonla [kaynak_id] [hedef_id]")
            return
        src, dest = args[1], args[2]
        profile = load_profile(src)
        update_profile(dest, profile)
        await event.respond(f"✅ {src} -> {dest} profili kopyalandı.")

    # 🤖 /bots
    elif command == "/bots":
        bots = [p for p in get_all_profiles() if p.get("type") == "bot"]
        text = "\n".join([f"- {b['username']}" for b in bots])
        await event.respond(f"🤖 Aktif botlar:\n{text or 'Yok.'}")

    # 👤 /list_users
    elif command == "/list_users":
        profiles = get_all_profiles()
        users = [p.get("display_name", p.get("username")) for p in profiles]
        await event.respond("👥 Kayıtlı kullanıcılar:\n" + "\n".join(users))

    # 📁 /log [user_id]
    elif command == "/log":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /log [user_id]")
            return
        uid = args[1]
        logs = get_logs(uid, limit=20)
        await event.respond(f"🗂 Son loglar:\n```\n{logs[:3800]}\n```", parse_mode="markdown")

    # ⚙️ /session_durum [username]
    elif command == "/session_durum":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /session_durum [username]")
            return
        username = args[1]
        if is_session_available(username):
            await event.respond(f"✅ {username} için oturum AKTİF.")
        else:
            await event.respond(f"❌ {username} için oturum YOK veya BOZUK.")

    # 📊 /durum_ozet
    elif command == "/durum_ozet":
        profiles = get_all_profiles()
        bots = [p for p in profiles if p.get("type") == "bot"]
        users = [p for p in profiles if p.get("type") == "user"]
        demos = [u for u in users if checker.get_license_status(str(u["username"])) == "demo"]
        active = [u for u in users if checker.get_license_status(str(u["username"])) == "active"]
        
        # Demo uyarıları
        demo_alerts = checker.get_demo_alerts()
        expired_demos = len(demo_alerts)
        
        text = f"""
📊 *GAVATCORE Durum Özeti*
👤 İçerik Üretici Sayısı: {len(users)}
🤖 Bot Sayısı: {len(bots)}
🔓 Aktif Lisans: {len(active)}
⏳ Demo Kullanıcılar: {len(demos)}
🚨 Demo Süresi Dolmuş: {expired_demos}
🧠 Toplam Kayıt: {len(profiles)}

💡 Demo uyarıları için: /demo_uyarilar
"""
        await event.respond(text, parse_mode="markdown")

    # 🚨 /demo_uyarilar
    elif command == "/demo_uyarilar":
        demo_alerts = checker.get_demo_alerts()
        
        if not demo_alerts:
            await event.respond("✅ Hiç demo süresi dolmuş kullanıcı yok!")
            return
        
        text = "🚨 *Demo Süresi Dolmuş Kullanıcılar:*\n\n"
        
        for user_id, alert_data in demo_alerts.items():
            bot_username = alert_data.get("bot_username", "unknown")
            expired_at = alert_data.get("demo_expired_at", "unknown")
            profile_data = alert_data.get("profile_data", {})
            
            # Tarih formatla
            try:
                from datetime import datetime
                expired_dt = datetime.fromisoformat(expired_at)
                expired_str = expired_dt.strftime("%d.%m.%Y %H:%M")
            except:
                expired_str = expired_at
            
            text += f"🤖 **{bot_username}** (ID: `{user_id}`)\n"
            text += f"   ⏰ Süre Dolma: {expired_str}\n"
            text += f"   📊 Tip: {profile_data.get('type', 'unknown')}\n"
            text += f"   🧠 Mod: {profile_data.get('reply_mode', 'unknown')}\n"
            text += f"   📤 Spam: {'Aktifti' if profile_data.get('autospam') else 'Pasifti'}\n"
            text += f"   💡 Aktif et: `/lisans {user_id}`\n\n"
        
        await event.respond(text, parse_mode="markdown")

    # 🔄 /demo_temizle [user_id]
    elif command == "/demo_temizle":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /demo_temizle [user_id]")
            return
        
        user_id = args[1]
        checker.clear_demo_alert(int(user_id))
        await event.respond(f"✅ {user_id} için demo uyarısı temizlendi.")
        log_event("ADMIN_PANEL", f"🧹 Demo uyarısı manuel temizlendi: {user_id}")

    # 📱 /session_ac [telefon]
    elif command == "/session_ac":
        if len(args) < 2:
            await event.respond("📞 Kullanım: /session_ac +905xxxxxxxxx")
            return
        phone = args[1]
        await event.respond("📲 Yeni session oluşturuluyor...")
        path = await create_session_flow(phone_override=phone)
        if path:
            await event.respond(f"✅ Session açıldı: `{path}`", parse_mode="markdown")
        else:
            await event.respond("❌ Session oluşturulamadı.")

    # 🧠 /showcu_ekle [username]
    elif command == "/showcu_ekle":
        if len(args) < 2:
            await event.respond("📌 Kullanım: /showcu_ekle username")
            return
        username = args[1]
        profile = generate_showcu_persona(username)
        save_profile(username, profile)
        await event.respond(f"✅ İçerik üretici profili oluşturuldu: `{username}`")

    # 🤖 /bot_ekle [username]
    elif command == "/bot_ekle":
        if len(args) < 2:
            await event.respond("📌 Kullanım: /bot_ekle username")
            return
        username = args[1]
        profile = generate_bot_persona(username)
        save_profile(username, profile)
        await event.respond(f"✅ Bot profili oluşturuldu: `{username}`")

    # ⛔️ /force_dur [@username]
    elif command == "/force_dur":
        if len(args) < 2:
            await event.respond("Kullanıcı adı belirtmelisin: /force_dur @username")
            return
        username = args[1].replace("@", "")
        update_profile(username, {"autospam": False})
        await event.respond(f"⛔️ @{username} için spam durduruldu.")
    
    # 💰 /musteri_listesi - Müşteri listesi
    elif command == "/musteri_listesi":
        try:
            profiles = get_all_profiles()
            customers = []
            
            for username, profile in profiles.items():
                if profile.get("type") == "customer_bot":
                    customer_info = profile.get("customer_info", {})
                    customers.append({
                        "username": username,
                        "package": customer_info.get("package_name", "Bilinmiyor"),
                        "expires": customer_info.get("expires_at", "Bilinmiyor")[:10],
                        "status": profile.get("customer_status", "unknown")
                    })
            
            if not customers:
                await event.respond("📋 Henüz müşteri kaydı yok.")
                return
            
            customer_text = "💰 **Müşteri Listesi**\n\n"
            for i, customer in enumerate(customers, 1):
                status_emoji = "🟢" if customer["status"] == "active" else "🔴"
                customer_text += f"{i}. {status_emoji} @{customer['username']}\n"
                customer_text += f"   📦 {customer['package']}\n"
                customer_text += f"   📅 {customer['expires']}\n\n"
            
            await event.respond(customer_text, parse_mode="markdown")
            
        except Exception as e:
            await event.respond(f"❌ Müşteri listesi alınamadı: {e}")
    
    # ✅ /musteri_aktif [@username] - Müşteriyi aktif et
    elif command == "/musteri_aktif":
        if len(args) < 2:
            await event.respond("Kullanım: /musteri_aktif @username")
            return
        username = args[1].replace("@", "")
        try:
            update_profile(username, {"customer_status": "active"})
            await event.respond(f"✅ @{username} müşteri hesabı aktif edildi.")
        except Exception as e:
            await event.respond(f"❌ Hata: {e}")
    
    # ❌ /musteri_pasif [@username] - Müşteriyi pasif et
    elif command == "/musteri_pasif":
        if len(args) < 2:
            await event.respond("Kullanım: /musteri_pasif @username")
            return
        username = args[1].replace("@", "")
        try:
            update_profile(username, {"customer_status": "inactive"})
            await event.respond(f"❌ @{username} müşteri hesabı pasif edildi.")
        except Exception as e:
            await event.respond(f"❌ Hata: {e}")
    
    # 📊 /musteri_detay [@username] - Müşteri detayları
    elif command == "/musteri_detay":
        if len(args) < 2:
            await event.respond("Kullanım: /musteri_detay @username")
            return
        username = args[1].replace("@", "")
        try:
            profile = load_profile(username)
            if profile.get("type") != "customer_bot":
                await event.respond(f"❌ @{username} müşteri hesabı değil.")
                return
            
            customer_info = profile.get("customer_info", {})
            bot_config = profile.get("bot_config", {})
            
            detail_text = f"""📊 **Müşteri Detayları: @{username}**

👤 **Müşteri Bilgileri:**
• Telegram: @{customer_info.get('customer_username', 'Bilinmiyor')}
• User ID: {customer_info.get('customer_user_id', 'Bilinmiyor')}
• Durum: {'🟢 Aktif' if profile.get('customer_status') == 'active' else '🔴 Pasif'}

📦 **Paket Bilgileri:**
• Paket: {customer_info.get('package_name', 'Bilinmiyor')}
• Fiyat: {customer_info.get('package_price', 'Bilinmiyor')}₺
• Başlangıç: {customer_info.get('activated_at', 'Bilinmiyor')[:10]}
• Bitiş: {customer_info.get('expires_at', 'Bilinmiyor')[:10]}

🤖 **Bot Ayarları:**
• DM Davet: {'✅' if bot_config.get('dm_invite_enabled') else '❌'}
• Grup Daveti: {'✅' if bot_config.get('group_invite_aggressive') else '❌'}
• Yanıt Modu: {profile.get('reply_mode', 'manual')}
• VIP Fiyat: {profile.get('vip_price', '250')}₺

📱 **Teknik Bilgiler:**
• Telefon: {profile.get('phone', 'Bilinmiyor')}
• Telegram ID: {profile.get('user_id', 'Bilinmiyor')}
• Oluşturma: {profile.get('created_at', 'Bilinmiyor')[:10]}"""
            
            await event.respond(detail_text, parse_mode="markdown")
            
        except Exception as e:
            await event.respond(f"❌ Müşteri detayları alınamadı: {e}")

    # ▶️ /force_devam [@username]
    elif command == "/force_devam":
        if len(args) < 2:
            await event.respond("Kullanıcı adı belirtmelisin: /force_devam @username")
            return
        username = args[1].replace("@", "")
        update_profile(username, {"autospam": True})
        await event.respond(f"✅ @{username} için spam başlatıldı.")

    # 🗒️ /logs [@username] [n]
    elif command == "/logs":
        if len(args) < 2:
            await event.respond("Kullanıcı adı belirtmelisin: /logs @username [n]")
            return
        username = args[1].replace("@", "")
        limit = int(args[2]) if len(args) > 2 else 20
        logs = get_logs(username, limit=limit)
        await event.respond(f"🗒️ Son {limit} log:\n{logs}")

    # 🔍 /logara [@username] [keyword] [level] [after]
    elif command == "/logara":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /logara @username [keyword] [level] [after_date]")
            return
        username = args[1].replace("@", "")
        keyword = args[2] if len(args) > 2 else ""
        level = args[3] if len(args) > 3 else ""
        after = args[4] if len(args) > 4 else ""
        
        result = search_logs(username, keyword=keyword, level=level, after=after)
        await event.respond(f"🔍 Log arama sonucu:\n{result}")

    # 📊 /log_stats [@username]
    elif command == "/log_stats":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /log_stats @username")
            return
        username = args[1].replace("@", "")
        stats = get_log_stats(username)
        
        if not stats.get("exists"):
            await event.respond(f"📭 {username} için log dosyası bulunamadı.")
            return
        
        if "error" in stats:
            await event.respond(f"❌ Log istatistik hatası: {stats['error']}")
            return
        
        stats_text = f"""📊 **{username} Log İstatistikleri**

📝 Toplam Satır: {stats['total_lines']}
💾 Dosya Boyutu: {stats['file_size']} byte
ℹ️ INFO: {stats['info_count']}
⚠️ WARNING: {stats['warning_count']}
❌ ERROR: {stats['error_count']}

📅 İlk Log: {stats['first_log']}
📅 Son Log: {stats['last_log']}"""
        
        await event.respond(stats_text, parse_mode="markdown")

    # 🛠️ /panel [@username] - GPT Kontrol Paneli
    elif command == "/panel":
        from telethon import Button
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /panel @username")
            return
        username = args[1].replace("@", "")
        
        # Kullanıcı profilini yükle
        try:
            profile = load_profile(username)
            current_gpt_mode = profile.get("gpt_enhanced", False)
            current_spam_speed = profile.get("spam_speed", "medium")
            
            buttons = [
                [Button.inline("🤖 GPT Modu", f"gpt_mode_{username}")],
                [Button.inline("🕒 Spam Sıklığı", f"spam_speed_{username}")],
                [Button.inline("💎 VIP Mesajı", f"vip_edit_{username}")],
                [Button.inline("💳 Papara Bilgisi", f"update_papara_{username}")],
                [Button.inline("📊 Durum", f"status_{username}")]
            ]
            
            status_text = f"""🛠️ **{username} Kontrol Paneli**

🤖 GPT Modu: {'✅ Aktif' if current_gpt_mode else '❌ Kapalı'}
🕒 Spam Hızı: {current_spam_speed.title()}

Ayarlamak istediğin özelliği seç:"""
            
            await event.respond(status_text, buttons=buttons, parse_mode="markdown")
            log_event(username, f"🛠️ Admin panel açıldı")
            
        except Exception as e:
            await event.respond(f"❌ Profil yüklenemedi: {username}\n{e}")

    # 🔥 /terminate_session [@username]
    elif command == "/terminate_session":
        if len(args) < 2:
            await event.respond("Kullanıcı adı: /terminate_session @username")
            return
        username = args[1].replace("@", "")
        result = terminate_session(username)
        if result:
            await event.respond(f"🔥 Oturum sonlandırıldı: @{username}")
        else:
            await event.respond(f"❌ Oturum kapatılamadı: @{username}")

    # 💾 /backup
    elif command == "/backup":
        try:
            from utils.file_utils import backup_file
            files = [
                *[os.path.join("data", f) for f in os.listdir("data") if f.endswith(".json")],
                *[os.path.join("sessions", f) for f in os.listdir("sessions") if f.endswith(".session")]
            ]
            results = []
            for f in files:
                b = backup_file(f)
                if b:
                    results.append(f"✔️ {os.path.basename(f)} yedeklendi.")
            await event.respond("\n".join(results) or "Hiçbir dosya yedeklenmedi.")
        except Exception as e:
            await event.respond(f"Backup hatası: {e}")

    # /show_menu_list - Show menülerini listele
    elif command == "/show_menu_list":
        from utils.menu_manager import show_menu_manager
        available_menus = show_menu_manager.list_available_menus()
        if available_menus:
            menu_text = "🎭 *Mevcut Show Menüleri:*\n\n"
            for bot_name, title in available_menus.items():
                menu_text += f"🤖 **{bot_name}**: {title}\n"
            await event.respond(menu_text, parse_mode="markdown")
        else:
            await event.respond("❌ Hiç show menüsü bulunamadı.")

    # /show_menu_view [bot_name] [compact] - Show menüsünü görüntüle
    elif command.startswith("/show_menu_view"):
        try:
            from utils.menu_manager import show_menu_manager
            parts = command.split()
            if len(parts) < 2:
                await event.respond("⚠️ Kullanım: /show_menu_view [bot_name] [compact]")
                return
            
            bot_name = parts[1]
            compact = len(parts) > 2 and parts[2].lower() == "compact"
            
            menu = show_menu_manager.get_show_menu(bot_name, compact=compact)
            if menu:
                menu_type = "Kısa" if compact else "Tam"
                await event.respond(f"🎭 **{bot_name}** {menu_type} Show Menüsü:\n\n{menu}")
            else:
                await event.respond(f"❌ {bot_name} için show menüsü bulunamadı.")
        except Exception as e:
            await event.respond(f"❌ Hata: {str(e)}")

    # /show_menu_update [bot_name] [title] | [content] - Show menüsünü güncelle
    elif command.startswith("/show_menu_update"):
        try:
            from utils.menu_manager import show_menu_manager
            content = command.replace("/show_menu_update", "").strip()
            if "|" not in content:
                await event.respond("⚠️ Kullanım: /show_menu_update [bot_name] [title] | [menü içeriği]")
                return
            
            header, menu_content = content.split("|", 1)
            header_parts = header.strip().split()
            if len(header_parts) < 1:
                await event.respond("⚠️ Bot adı belirtilmedi.")
                return
            
            bot_name = header_parts[0]
            title = " ".join(header_parts[1:]) if len(header_parts) > 1 else None
            
            success = show_menu_manager.update_show_menu(bot_name, menu_content.strip(), title)
            if success:
                await event.respond(f"✅ {bot_name} show menüsü güncellendi!")
            else:
                await event.respond(f"❌ {bot_name} show menüsü güncellenirken hata oluştu.")
        except Exception as e:
            await event.respond(f"❌ Hata: {str(e)}")

    # Yardım/yardır - Role-based help
    elif command in ["/help", "/yardım"]:
        user_id = event.sender_id
        role = get_user_role(user_id)
        available_cmds = get_available_commands(user_id)
        
        # Role başlığı
        role_titles = {
            "admin": "🛠️ *Admin Komut Listesi*",
            "producer": "👩‍💻 *İçerik Üretici Komutları*", 
            "client": "👤 *Kullanıcı Komutları*"
        }
        
        title = role_titles.get(role, "📋 *Komut Listesi*")
        
        # Komutları kategorilere ayır
        admin_cmds = [c for c in available_cmds if "admin" in c["roles"]]
        producer_cmds = [c for c in available_cmds if "producer" in c["roles"] and "admin" not in c["roles"]]
        client_cmds = [c for c in available_cmds if "client" in c["roles"] and "producer" not in c["roles"]]
        
        help_text = f"{title}\n\n"
        
        if admin_cmds:
            help_text += "👑 *Admin Komutları:*\n"
            for cmd in admin_cmds:
                help_text += f"• {cmd['command']} — {cmd['desc']}\n"
            help_text += "\n"
        
        if producer_cmds:
            help_text += "👩‍💻 *İçerik Üretici Komutları:*\n"
            for cmd in producer_cmds:
                help_text += f"• {cmd['command']} — {cmd['desc']}\n"
            help_text += "\n"
        
        if client_cmds:
            help_text += "👤 *Kullanıcı Komutları:*\n"
            for cmd in client_cmds:
                help_text += f"• {cmd['command']} — {cmd['desc']}\n"
            help_text += "\n"
        
        # Rol bilgisi ekle
        help_text += f"📋 *Rolünüz:* {role.title()}\n"
        help_text += f"🔢 *Toplam Komut:* {len(available_cmds)}"
        
        await event.respond(help_text, parse_mode="markdown")
    else:
        await event.respond("🤖 Bilinmeyen admin komutu. /help yaz!")

