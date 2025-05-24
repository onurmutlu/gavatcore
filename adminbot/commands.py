# // adminbot/commands.py

import json
import os
from datetime import datetime
from telethon import events
from config import GAVATCORE_ADMIN_ID

from core.license_checker import LicenseChecker
from core.profile_loader import (
    load_profile, update_profile,
    get_all_profiles, get_profile_path,
    save_profile
)
from utils.log_utils import get_logs, log_event
from core.gavat_client import is_session_available
from core.session_manager import create_session_flow
from core.profile_generator import generate_bot_persona, generate_showcu_persona

checker = LicenseChecker()

async def handle_admin_command(bot, event):
    if event.sender_id != int(GAVATCORE_ADMIN_ID):
        await event.respond("⛔️ Bu komut sadece admin tarafından kullanılabilir.")
        return

    message = event.raw_text.strip()
    args = message.split()
    command = args[0].lower()

    # ✅ /lisans [user_id]
    if command == "/lisans":
        if len(args) < 2 or not args[1].isdigit():
            await event.respond("⚠️ Kullanım: /lisans [user_id]")
            return
        user_id = int(args[1])
        checker.activate_license(user_id)
        await event.respond(f"✅ Kullanıcı {user_id} için lisans aktif edildi.")
        log_event(user_id, "🔓 Lisans aktif edildi (admin).")

    # ❌ /kapat [user_id]
    elif command == "/kapat":
        if len(args) < 2 or not args[1].isdigit():
            await event.respond("⚠️ Kullanım: /kapat [user_id]")
            return
        user_id = int(args[1])
        checker.deactivate_license(user_id)
        await event.respond(f"🔒 Kullanıcı {user_id} devre dışı bırakıldı.")
        log_event(user_id, "🔒 Lisans devre dışı bırakıldı (admin).")

    # 🔍 /durum [user_id]
    elif command == "/durum":
        if len(args) < 2 or not args[1].isdigit():
            await event.respond("⚠️ Kullanım: /durum [user_id]")
            return
        user_id = int(args[1])
        status = checker.get_license_status(user_id)
        await event.respond(f"📌 Kullanıcı {user_id} durumu: `{status}`")

    # ✨ /mod [user_id] [manual|gpt|hybrid|manualplus]
    elif command == "/mod":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /mod [user_id] [mod]")
            return
        user_id = int(args[1])
        new_mode = args[2]
        profile = load_profile(str(user_id))
        profile["reply_mode"] = new_mode
        update_profile(str(user_id), profile)
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
            await event.respond(f"👤 Profil JSON:\n```json\n{json.dumps(profile, indent=2, ensure_ascii=False)}```", parse_mode="markdown")
        except:
            await event.respond(f"❌ Profil bulunamadı: {user_id}")

    # 📬 /mesaj [user_id] mesaj metni...
    elif command == "/mesaj":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /mesaj [user_id] mesaj...")
            return
        user_id = int(args[1])
        msg = " ".join(args[2:])
        try:
            await bot.send_message(user_id, msg)
            await event.respond(f"✅ Mesaj gönderildi.")
            log_event(user_id, f"📨 Admin mesajı gönderildi: {msg}")
        except Exception as e:
            await event.respond(f"❌ Gönderilemedi: {e}")

    # 🔄 /klonla [kaynak_id] [hedef_id]
    elif command == "/klonla":
        if len(args) < 3:
            await event.respond("⚠️ Kullanım: /klonla [kaynak_id] [hedef_id]")
            return
        src, dest = args[1], args[2]
        try:
            profile = load_profile(src)
            update_profile(dest, profile)
            await event.respond(f"✅ {src} -> {dest} profili kopyalandı.")
        except:
            await event.respond("❌ Klonlama başarısız oldu.")

    # 🤖 /bots
    elif command == "/bots":
        bots = [p for p in get_all_profiles() if p.get("type") == "bot"]
        text = "\n".join([f"- {b['username']}" for b in bots])
        await event.respond(f"🤖 Aktif botlar:\n{text or 'Yok.'}")

    # 📁 /log [user_id]
    elif command == "/log":
        if len(args) < 2:
            await event.respond("⚠️ Kullanım: /log [user_id]")
            return
        uid = args[1]
        logs = get_logs(uid, limit=20)
        await event.respond(f"🗂 Son loglar:\n{logs}")

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
        demos = [u for u in users if checker.get_license_status(int(u["username"])) == "demo"]
        active = [u for u in users if checker.get_license_status(int(u["username"])) == "active"]

        text = f"""
📊 *GAVATCORE Durum Özeti*
👤 Şovcu Sayısı: {len(users)}
🤖 Bot Sayısı: {len(bots)}
🔓 Aktif Lisans: {len(active)}
⏳ Demo Kullanıcılar: {len(demos)}
🧠 Toplam Kayıt: {len(profiles)}
"""
        await event.respond(text, parse_mode="markdown")

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
        try:
            profile = generate_showcu_persona(username)
            save_profile(username, profile)
            await event.respond(f"✅ Showcu profili oluşturuldu: `{username}`")
        except Exception as e:
            await event.respond(f"❌ Oluşturulamadı: {e}")

    # 🤖 /bot_ekle [username]
    elif command == "/bot_ekle":
        if len(args) < 2:
            await event.respond("📌 Kullanım: /bot_ekle username")
            return
        username = args[1]
        try:
            profile = generate_bot_persona(username)
            save_profile(username, profile)
            await event.respond(f"✅ Bot profili oluşturuldu: `{username}`")
        except Exception as e:
            await event.respond(f"❌ Oluşturulamadı: {e}")

    else:
        await event.respond(
            "🤖 Komut tanınmadı. Kullanılabilir komutlar:\n"
            "`/lisans /kapat /durum /mod /profil /mesaj /klonla /bots /log /session_durum /durum_ozet /session_ac /bot_ekle /showcu_ekle`",
            parse_mode="markdown"
        )
