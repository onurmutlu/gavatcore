## 🤖 GavatCore AdminBot

Telegram üzerinden GavatCore sistemini yönetmek için geliştirilmiş yönetim botudur. Lisans, profil, session, log, onboarding ve akış kontrolü gibi kritik operasyonları uzaktan komutlarla güvenli biçimde yönetmenizi sağlar.

### Öne Çıkanlar
- Sistem yönetimi: lisans aç/kapat, durum/istatistik, sağlık kontrolü, yedek alma
- Profil/bot yönetimi: profil görüntüle/güncelle, bot/showcu ekle/klonla
- Oturum yönetimi: session aç/kapat, session durumu
- Akış kontrolü: autospam başlat/durdur, hız ayarları (inline panel)
- Loglar: son loglar, arama, istatistikler
- Onboarding: butonlu akışlar, SMS kodu/2FA, Papara/IBAN bilgisi güncelleme

### Dizin Yapısı
- `adminbot/main.py`: Temel AdminBot sınıfı; `/start`, `/status`, `/health`, `/help` komutları, metrikler ve structured logging
- `adminbot/dispatcher.py`: Bot başlatımı, ortam değişkenleri okuma, tüm event/komut handler’larının bağlanması (sync ve async başlatıcılar)
- `adminbot/commands.py`: Rol bazlı komutlar (admin / producer / client) ve ileri seviye yönetim akışları

### Gereksinimler (ENV)
Aşağıdaki değişkenlerin tanımlı olması gerekir:
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `ADMIN_BOT_TOKEN`
- (Opsiyonel) `GAVATCORE_ADMIN_ID`, `AUTHORIZED_USERS`

### Hızlı Başlangıç
1) Ortam değişkenlerini yükle (.env önerilir)
2) Aşağıdaki seçeneklerden biriyle başlat:

```bash
# Seçenek 1: Ana giriş
python adminbot/main.py

# Seçenek 2: Dispatcher (senkron)
python -c "from adminbot.dispatcher import start_dispatcher; start_dispatcher()"

# Seçenek 3: Dispatcher (asenkron kullanım için)
python -c "import asyncio; from adminbot.dispatcher import start_dispatcher_async; asyncio.run(start_dispatcher_async())"
```

### Komut Özeti (Rol Bazlı)
- Admin: `/lisans`, `/kapat`, `/durum`, `/mod`, `/profil`, `/panel`, `/session_ac`, `/force_dur`, `/force_devam`, `/logs`, `/logara`, `/log_stats`, `/backup`, `/terminate_session`, `/show_menu_*`, `/musteri_*`
- Producer/Client: `/start`, `/menü`, `/fiyat`, `/iban`, `/yardım`

Not: Erişim kontrolü rol bazlıdır. Admin dışı kullanıcılar yalnızca kendi rolüne açık komutlara erişebilir.

### Log ve İzleme
- Tüm kritik aksiyonlar yapılandırılmış log olarak kaydedilir (structlog)
- Komut/mesaj sayaçları ve uptime gibi metrikler tutulur
- Örnek komutlar: `/status`, `/health`, `/logs @username 50`, `/logara @username keyword`

### Güvenlik
- Admin erişimini sınırlayın: `GAVATCORE_ADMIN_ID` ve/veya `AUTHORIZED_USERS` değerlerini zorunlu tutun
- Bot token’larını ve API kimliklerini .env içinde saklayın
- Production’da telemetri/log dosyalarının yetkilerini sınırlandırın

### Sorun Giderme
- “ENV ERROR: … bulunamadı”
  - `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `ADMIN_BOT_TOKEN` tanımlı mı kontrol edin
- 2FA/OTP akışında takılma
  - Onboarding adımlarını inline butonlarla tekrar başlatın (`/basla`), kod/şifreyi doğru formatta gönderin
- Erişim reddi
  - `GAVATCORE_ADMIN_ID` veya `AUTHORIZED_USERS` içinde kullanıcıyı tanımlayın

### Notlar
- Bu bot yalnızca yetkilendirilmiş hesaplarla kullanılmalıdır
- Üretim ortamında rate limit ve floodwait uyarılarına dikkat edin
