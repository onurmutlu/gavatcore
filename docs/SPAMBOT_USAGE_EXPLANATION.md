# @SpamBot Kullanımı ve Amacı

## 🤖 @SpamBot Nedir?

**@SpamBot**, Telegram'ın **resmi native sistem botlarından biridir**. Bu bot bizim projemizle hiçbir alakası olmayan, Telegram tarafından sağlanan bir hizmettir.

### 📋 @SpamBot'un Özellikleri:
- **Resmi Telegram Botu**: Telegram Inc. tarafından işletilir
- **User ID**: `178220800` (sabit)
- **Amaç**: Hesap spam durumu kontrolü
- **Komut**: `/start` komutu ile hesap durumu raporu verir

## 🎯 Neden @SpamBot'a Start Komutu Atıyoruz?

GAVATCORE sisteminde @SpamBot'a `/start` komutu gönderme sebebi **hesap güvenlik kontrolüdür**.

### 🔍 Kontrol Mekanizması:

```python
# core/account_monitor.py - _check_spambot_status fonksiyonu
async def _check_spambot_status(self, client: TelegramClient, username: str):
    """@SpamBot'tan durum kontrolü"""
    
    # SpamBot'a mesaj gönder
    spambot = await client.get_entity("@SpamBot")
    await client.send_message(spambot, "/start")
    
    # Yanıt bekle ve analiz et
    messages = await client.get_messages(spambot, limit=3)
    
    # Spam uyarı kelimelerini kontrol et
    warning_keywords = [
        "spam", "flood", "limit", "restricted", 
        "warning", "violation", "abuse", "banned"
    ]
```

### ⏰ Kontrol Sıklığı:
- **6 saatte bir** otomatik kontrol
- Manuel kontrol komutu: `/session_durum [username]`
- Monitoring loop içinde sürekli çalışır

## 🛡️ Güvenlik Amaçları

### 1. **Erken Uyarı Sistemi**
@SpamBot'tan gelen yanıtlar analiz edilerek hesabın spam durumu tespit edilir:

```python
if spam_detected:
    log_event(username, f"⚠️ SPAM UYARISI TESPİT EDİLDİ: {warning_message}")
    
    # Anti-spam guard'a uyarı ekle
    anti_spam_guard.add_spam_warning(username, "spambot_warning")
    
    # Acil müdahale
    await self._emergency_response(username, "spambot_warning")
```

### 2. **Otomatik Güvenlik Modu**
Spam uyarısı tespit edildiğinde sistem otomatik olarak:
- ✅ Spam'i durdurur (`autospam: false`)
- ✅ Manuel moda geçer (`reply_mode: manual`)
- ✅ Güvenli mod aktifleştirir (`safe_mode: true`)

### 3. **Hesap Sağlığı İzleme**
@SpamBot kontrolü hesap sağlığı izlemenin bir parçasıdır:

```python
# Monitoring döngüsü
while self.monitoring_active.get(username, False):
    # SpamBot kontrolü
    await self._check_spambot_status(client, username)
    
    # Genel sağlık kontrolü  
    await self._check_account_health(client, username)
    
    # 1 saat bekle
    await asyncio.sleep(self.HEALTH_CHECK_INTERVAL)
```

## 📊 @SpamBot Yanıt Örnekleri

### ✅ Temiz Hesap Yanıtı:
```
"Good news — no limits are currently applied to your account. 
You're free to use Telegram!"
```

### ⚠️ Spam Uyarısı Yanıtı:
```
"Your account has been limited due to spam-like activity. 
Please reduce your messaging frequency."
```

### 🚫 Kısıtlı Hesap Yanıtı:
```
"Your account is currently restricted due to violations 
of Telegram's Terms of Service."
```

## 🔄 İşleyiş Akışı

```mermaid
graph TD
    A[Hesap İzleme Başlar] --> B[6 Saat Bekle]
    B --> C[@SpamBot'a /start Gönder]
    C --> D[Yanıt Bekle - 5 saniye]
    D --> E[Son 3 Mesajı Al]
    E --> F{Spam Kelimesi Var mı?}
    F -->|Evet| G[🚨 SPAM UYARISI]
    F -->|Hayır| H[✅ Temiz Durum]
    G --> I[Acil Müdahale]
    I --> J[Spam Durdur]
    J --> K[Güvenli Mod]
    H --> L[Normal İşleyiş]
    K --> B
    L --> B
```

## 🎛️ Yönetici Komutları

### Manuel Kontrol:
```bash
/session_durum @username
```

### Uyarıları Sıfırla:
```bash
/reset_warnings @username  
```

### Hesap Durumu Raporu:
```bash
/durum_ozet
```

## ⚠️ Önemli Notlar

### 🔒 Gizlilik:
- @SpamBot sadece hesap durumu kontrolü yapar
- Hiçbir kişisel veri paylaşılmaz
- Sadece `/start` komutu gönderilir

### 🤖 Otomatik İşlem:
- Bu kontrol tamamen otomatiktir
- Kullanıcı müdahalesi gerektirmez
- Arka planda sessizce çalışır

### 🛡️ Güvenlik:
- Telegram'ın resmi botudur
- %100 güvenli ve yasal
- Telegram ToS'a uygun kullanım

## 📈 İstatistikler

GAVATCORE sisteminde @SpamBot kontrolü:
- ✅ **6 saatte bir** otomatik kontrol
- ✅ **Erken uyarı** sistemi
- ✅ **Otomatik güvenlik** modu
- ✅ **%100 yasal** kullanım
- ✅ **Telegram native** entegrasyon

---

**Sonuç**: @SpamBot kullanımı, hesap güvenliğini sağlamak ve Telegram'ın spam politikalarına uyum göstermek için kritik bir güvenlik önlemidir. Bu sistem sayesinde hesaplar spam uyarısı almadan önce otomatik olarak güvenli moda geçer.

**Durum**: ✅ Doğru kullanım - Telegram ToS uyumlu 