import os

from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto

# ------------------ Wizard Başlangıcı ------------------ #
print("📱 Telegram Media Scraper'a hoş geldin!\n")

api_id = int(input("🔑 API ID: "))
api_hash = input("🔐 API Hash: ")
phone = input("📞 Telefon numaran (örn. +905xxxxxxxxx): ")

session_name = "session_" + phone.replace("+", "").replace(" ", "")
client = TelegramClient(session_name, api_id, api_hash)


def main():
    client.start(phone)
    if not client.is_user_authorized():
        print("🔐 Giriş yapılıyor...")
        client.send_code_request(phone)  # type: ignore
        code = input("💬 Telegram'dan gelen kodu gir: ")
        try:
            client.sign_in(phone, code)  # type: ignore
        except SessionPasswordNeededError:
            pw = input("🧱 2FA şifren: ")
            client.sign_in(password=pw)  # type: ignore

    print("\n✅ Giriş başarılı!")

    # Grup seçimi
    dialogs = client.get_dialogs()  # type: ignore
    print("\n📂 Katıldığın gruplar:")
    groups = [d for d in list(dialogs) if d.is_group or d.is_channel]  # type: ignore

    for i, g in enumerate(groups):
        print(f"[{i}] {g.name}")

    selected = int(input("\n🎯 Hangi grubun medyasını indirmek istiyorsun? (numara gir): "))
    target = groups[selected].entity

    # Klasör oluştur
    os.makedirs("downloads", exist_ok=True)

    count = 0
    print("\n📥 Medyalar indiriliyor...")
    for msg in client.iter_messages(target):
        if msg.photo or (
            msg.document
            and msg.file
            and msg.file.mime_type
            and msg.file.mime_type.startswith(("image/", "video/"))
        ):
            try:
                file_path = msg.download_media(file="downloads/")
                count += 1
                print(f"✅ İndirildi: {file_path}")
            except Exception as e:
                print(f"❌ Hata: {e}")

    print(
        f"\n🎉 İşlem tamamlandı. Toplam {count} medya dosyası indirildi. 📁 [downloads/] klasörüne bak."
    )


with client:
    main()
