# core/session_manager.py

import os
import asyncio
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import logging
import json

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

logger = logging.getLogger("gavatcore.session_manager")
logger.setLevel(logging.INFO)

def get_session_path(phone: str) -> str:
    """Telefon numarasına uygun session dosya yolu üretir."""
    session_name = phone.replace("+", "_")
    return os.path.join(SESSIONS_DIR, f"{session_name}.session")

async def open_session(
    phone: str,
    api_id: int,
    api_hash: str,
    code_cb,
    password_cb,
    session_str: str = None,
    custom_session_path: str = None
):
    """
    Telegram oturumu açar (kod ve 2FA callback'li).
    Login başarılı olduğunda session dosyası kalıcı olarak kaydedilir.
    """
    client = None
    session_path = custom_session_path or get_session_path(phone)
    
    # SQLite lock'ları için retry mekanizması
    max_retries = 3
    retry_delay = 2.0
    
    for attempt in range(max_retries):
        try:
            if session_str:
                # String session kullanılıyorsa direkt oluştur
                client = TelegramClient(
                    StringSession(session_str),
                    api_id,
                    api_hash,
                    connection_retries=3,
                    retry_delay=2,
                    timeout=30
                )
                await client.connect()
            else:
                # Debug: Session path'i logla
                logger.info(f"[SESSION] Session path kontrol ediliyor: {session_path}")
                logger.info(f"[SESSION] Dosya var mı: {os.path.exists(session_path)}")
                
                # Eğer session dosyası zaten varsa, onu kullan
                if os.path.exists(session_path):
                    logger.info(f"[SESSION] Mevcut session dosyası kullanılıyor: {session_path}")
                    client = TelegramClient(
                        session_path,
                        api_id,
                        api_hash,
                        connection_retries=3,
                        retry_delay=2,
                        timeout=30
                    )
                    await client.connect()
                else:
                    # Yeni session için direkt dosya yolu kullan
                    logger.info(f"[SESSION] Yeni session dosyası oluşturuluyor: {session_path}")
                    client = TelegramClient(
                        session_path,
                        api_id,
                        api_hash,
                        connection_retries=3,
                        retry_delay=2,
                        timeout=30
                    )
                    await client.connect()
            
            # Yetkilendirme kontrolü
            if not await client.is_user_authorized():
                logger.info(f"[SESSION] {phone} için giriş akışı başlatılıyor...")
                
                # Kod gönder
                await client.send_code_request(phone)
                code = await code_cb()
                
                try:
                    # Kod ile giriş yap
                    await client.sign_in(phone, code)
                    logger.info(f"[SESSION] Kod ile giriş başarılı")
                except errors.SessionPasswordNeededError:
                    # 2FA gerekli
                    logger.info(f"[SESSION] 2FA gerekli, şifre isteniyor...")
                    pw = await password_cb()
                    await client.sign_in(password=pw)
                    logger.info(f"[SESSION] 2FA ile giriş başarılı")
                
                # Login başarılı olduktan sonra session'ı kaydet
                await client.disconnect()
                await asyncio.sleep(1.0)  # Bağlantı kapanması için bekle
                await client.connect()
                
                # Session dosyasının düzgün oluştuğunu kontrol et
                if os.path.exists(session_path):
                    file_size = os.path.getsize(session_path)
                    logger.info(f"[SESSION] Session dosyası oluşturuldu: {session_path} ({file_size} bytes)")
                    if file_size < 1024:
                        logger.warning(f"[SESSION] Session dosyası çok küçük, yeniden oluşturuluyor...")
                        await client.disconnect()
                        await asyncio.sleep(1.0)
                        await client.connect()
                else:
                    logger.error(f"[SESSION] Session dosyası oluşturulamadı: {session_path}")
            
            # Kullanıcı bilgilerini al
            me = await client.get_me()
            if me:
                logger.info(f"[SESSION] Giriş başarılı: {me.first_name} (@{me.username or me.id})")
                logger.info(f"[SESSION] Session dosyası kaydedildi: {session_path}")
                return client, me
            else:
                raise Exception("Kullanıcı bilgileri alınamadı")
                
        except Exception as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                logger.warning(f"[SESSION] Database kilitli, {wait_time} saniye bekleniyor... ({attempt + 1}/{max_retries})")
                
                if client:
                    try:
                        await client.disconnect()
                    except:
                        pass
                        
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"[SESSION] Giriş başarısız: {e}")
                
                # Sadece başarısız login durumunda session dosyasını sil
                if session_path and os.path.exists(session_path):
                    try:
                        file_size = os.path.getsize(session_path)
                        if file_size < 1024:  # 1KB'den küçükse bozuk
                            os.remove(session_path)
                            logger.warning(f"[SESSION] Bozuk session dosyası silindi: {session_path}")
                    except Exception as e2:
                        logger.error(f"[SESSION] Session dosyası kontrol edilemedi: {e2}")
                
                # Client'ı kapat
                if client:
                    try:
                        await client.disconnect()
                    except:
                        pass
                
                if attempt == max_retries - 1:
                    raise e
                
    return None, None

async def close_session(phone: str, api_id: int, api_hash: str):
    """Telefon için oturumu sonlandırıp dosyayı siler."""
    session_path = get_session_path(phone)
    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()
    try:
        await client.log_out()
    finally:
        await client.disconnect()
        if os.path.exists(session_path):
            os.remove(session_path)
            logger.info(f"[SESSION] Session dosyası silindi: {session_path}")

def list_sessions():
    """Tüm session dosyalarını listeler."""
    return [
        f for f in os.listdir(SESSIONS_DIR)
        if f.endswith(".session")
    ]

def is_session_active(phone: str):
    """Session dosyası ve bağlantısı var mı (dosya bazlı)."""
    session_path = get_session_path(phone)
    return os.path.exists(session_path)

async def test_session(phone: str, api_id: int, api_hash: str) -> bool:
    """Session'ı test et"""
    session_path = get_session_path(phone)
    try:
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            connection_retries=3,
            retry_delay=2,
            timeout=30
        )
        await client.connect()
        is_authorized = await client.is_user_authorized()
        await client.disconnect()
        return is_authorized
    except Exception as e:
        logger.error(f"Session test hatası ({session_path}): {e}")
        return False

async def notify_admin_dm(bot_client, admin_id, message):
    """Admini DM ile bilgilendir (oturum düştüğünde)."""
    try:
        await bot_client.send_message(admin_id, f"⚠️ [UYARI] Oturum kapandı: {message}")
    except Exception as e:
        logger.error(f"[NOTIFY] Admine DM gönderilemedi: {e}")

def session_phone_from_path(session_path: str) -> str:
    """Session dosyasından telefon numarasını geri çıkarır."""
    name = os.path.splitext(os.path.basename(session_path))[0]
    return name.replace("_", "+")

def get_session_info_list():
    """Session dosyalarından kısa bilgi listesi (future-proof)."""
    sessions = list_sessions()
    infos = []
    for s in sessions:
        phone = session_phone_from_path(s)
        infos.append({"phone": phone, "session_file": s})
    return infos

# ---- EKLENDİ ----
async def create_session_flow(phone_override: str = None):
    """
    CLI veya bot üzerinden yeni bir session açar ve .session dosyasını kaydeder.
    phone_override ile telefon manuel girilebilir.
    """
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
    phone = phone_override or input("Telefon numarasını gir (+90xxx): ")
    async def code_cb():
        return input("Telegram'dan gelen kod: ")
    async def pw_cb():
        return input("2FA şifresi (varsa): ")
    client, me = await open_session(
        phone=phone,
        api_id=TELEGRAM_API_ID,
        api_hash=TELEGRAM_API_HASH,
        code_cb=code_cb,
        password_cb=pw_cb
    )
    await client.disconnect()
    return get_session_path(phone)

async def terminate_session(phone: str):
    """
    Verilen telefon için oturumu kapatır ve session dosyasını siler.
    """
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
    await close_session(phone, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    return True

async def get_active_sessions():
    """Aktif session'ları sıralı şekilde yükler."""
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH
    sessions = {}
    
    # Personas dosyalarından telefon-username eşleştirmesi oluştur
    phone_to_username = {}
    personas_dir = "data/personas"
    
    if os.path.exists(personas_dir):
        for filename in os.listdir(personas_dir):
            if filename.endswith(".json") and not filename.startswith("test"):
                try:
                    with open(os.path.join(personas_dir, filename), 'r', encoding='utf-8') as f:
                        persona = json.load(f)
                        phone = persona.get("phone")
                        username = persona.get("username")
                        if phone and username:
                            phone_to_username[phone] = username
                            logger.info(f"📱 Persona eşleştirmesi: {phone} -> {username}")
                except Exception as e:
                    logger.error(f"Persona okuma hatası ({filename}): {e}")
    
    # Session dosyalarını listele
    session_files = list_sessions()
    
    for session_file in session_files:
        try:
            # Test/örnek dosyalarını atla
            if any(pattern in session_file.lower() for pattern in ["test", "example", "temp"]):
                continue
                
            # Session dosyasından telefon numarasını çıkar
            session_name = os.path.splitext(session_file)[0]
            
            # Eğer session dosyası telefon numarası formatındaysa (_905...)
            if session_name.startswith("_905"):
                phone = session_name.replace("_", "+")
            else:
                # Username formatındaysa, personas'dan telefon numarasını bul
                phone = None
                for p, u in phone_to_username.items():
                    if u == session_name:
                        phone = p
                        break
                
                if not phone:
                    logger.warning(f"⚠️ Session için telefon numarası bulunamadı: {session_file}")
                    continue
            
            # Username'i bul
            username = phone_to_username.get(phone)
            if not username:
                logger.warning(f"⚠️ Telefon için username bulunamadı: {phone}")
                continue
            
            session_path = os.path.join(SESSIONS_DIR, session_file)
            
            # Her session arasında 1.5 saniye bekle
            await asyncio.sleep(1.5)
            
            # Session'ı test et
            logger.info(f"Session test ediliyor: {session_file} ({username})")
            
            # SQLite lock'ları için retry mekanizması
            max_retries = 3
            retry_delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    if await test_session(phone, TELEGRAM_API_ID, TELEGRAM_API_HASH):
                        sessions[username] = {
                            "session_file": session_path,
                            "phone": phone,
                            "api_id": TELEGRAM_API_ID,
                            "api_hash": TELEGRAM_API_HASH
                        }
                        logger.info(f"✅ Aktif session bulundu: {username} ({phone})")
                        break
                    else:
                        logger.warning(f"Session yetkisiz: {session_file}")
                        break
                        
                except Exception as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.warning(f"Database kilitli, {wait_time} saniye bekleniyor... ({attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Session test hatası ({session_file}): {e}")
                        break
                        
        except Exception as e:
            logger.error(f"Session işleme hatası ({session_file}): {e}")
            continue
            
    if not sessions:
        logger.error("❌ Aktif session bulunamadı!")
    else:
        logger.info(f"🎯 Toplam {len(sessions)} aktif session yüklendi")
        
    return sessions

