# 📱 Telegram Client Modülü

Telethon tabanlı gelişmiş Telegram client yönetim sistemi. Production-ready, scalable ve güvenilir.

## 🌟 Özellikler

### 🔧 Temel Özellikler
- **Async/Await**: Tamamen asenkron yapı
- **Session Management**: SQLite ve String session desteği
- **Connection Pool**: Multiple client yönetimi
- **Auto-Reconnect**: Otomatik yeniden bağlanma
- **Rate Limiting**: Built-in rate limiting sistemi
- **Flood Protection**: Telegram flood wait yönetimi

### 🛡️ Güvenlik ve Hata Yönetimi
- **Retry Logic**: Exponential backoff ile retry
- **Error Handling**: Kapsamlı hata yönetimi
- **Session Security**: Güvenli session saklama
- **Auth Management**: Otomatik authorization

### 📊 Monitoring ve Logging
- **JSON Logging**: Structured logging desteği
- **Statistics**: Detaylı istatistik toplama
- **Redis Integration**: Redis state management
- **Health Checks**: Connection health monitoring

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
pip install -r requirements.txt
```

### 2. Basit Kullanım

```python
from gavatcore_engine.telegram_client import TelegramClientManager, ClientConfig

# Client konfigürasyonu
config = ClientConfig(
    session_name="my_bot",
    api_id=12345678,
    api_hash="your_api_hash",
    phone="+905551234567",
    device_model="GavatCore Bot"
)

# Client başlat
client_manager = TelegramClientManager(config)
await client_manager.initialize()

# Mesaj gönder
result = await client_manager.send_message(
    entity="@username",
    message="Merhaba! 🤖",
    parse_mode="html"
)

if result.success:
    print(f"✅ Mesaj gönderildi: {result.message_id}")
else:
    print(f"❌ Hata: {result.error}")

# Client kapat
await client_manager.disconnect()
```

## 📖 Detaylı Kullanım

### ClientConfig Sınıfı

```python
config = ClientConfig(
    session_name="bot_name",           # Unique session adı
    api_id=12345678,                   # Telegram API ID
    api_hash="api_hash_string",        # Telegram API Hash
    
    # İsteğe bağlı parametreler
    bot_token="bot_token",             # Bot token (bot için)
    phone="+905551234567",             # Telefon numarası (user için)
    session_string="session_string",   # String session
    
    # Device bilgileri
    device_model="Custom Bot",
    system_version="1.0.0",
    app_version="My App v1.0",
    lang_code="tr",
    
    # Connection ayarları
    connection_retries=5,              # Bağlantı denemesi
    retry_delay=5,                     # Retry arası bekleme (saniye)
    timeout=30,                        # Timeout (saniye)
    flood_sleep_threshold=60,          # Flood wait threshold
    auto_reconnect=True,               # Otomatik yeniden bağlanma
)
```

### Mesaj Gönderme

```python
# Basit mesaj
result = await client_manager.send_message(
    entity="me",  # Saved Messages
    message="Basit mesaj"
)

# HTML formatı
result = await client_manager.send_message(
    entity="@username",
    message="<b>Kalın</b> ve <i>eğik</i> yazı",
    parse_mode="html"
)

# Markdown formatı
result = await client_manager.send_message(
    entity=-1001234567890,  # Grup ID
    message="**Kalın** ve *eğik* yazı",
    parse_mode="markdown"
)

# Gelişmiş seçenekler
result = await client_manager.send_message(
    entity="@channel",
    message="Kanal mesajı",
    silent=True,                    # Sessiz gönderim
    link_preview=False,            # Link preview yok
    schedule=datetime.now() + timedelta(hours=1)  # Zamanlanmış
)
```

### Retry Konfigürasyonu

```python
from gavatcore_engine.telegram_client import RetryConfig

# Custom retry config
client_manager.retry_config = RetryConfig(
    max_retries=5,              # Maksimum deneme sayısı
    base_delay=1.0,             # Başlangıç gecikme (saniye)
    max_delay=60.0,             # Maksimum gecikme (saniye)
    exponential_base=2.0,       # Exponential çarpan
    jitter=True,                # Rastgele gecikme ekle
    retry_on_flood=True,        # Flood wait'te retry
    retry_on_server_error=True, # Server error'da retry
    retry_on_network_error=True # Network error'da retry
)
```

## 🏊 Client Pool Kullanımı

Multiple bot yönetimi için client pool kullanın:

```python
from gavatcore_engine.telegram_client import TelegramClientPool

# Pool oluştur
pool = TelegramClientPool()

# Client'ları ekle
configs = [
    ClientConfig(session_name="bot1", ...),
    ClientConfig(session_name="bot2", ...),
    ClientConfig(session_name="bot3", ...)
]

for config in configs:
    await pool.add_client(config)

# Round-robin mesaj gönderimi
result = await pool.send_message(
    entity="@channel",
    message="Pool'dan gönderilen mesaj"
)

# Belirli client ile gönderim
result = await pool.send_message(
    entity="@channel",
    message="Belirli bot'tan mesaj",
    session_name="bot1"  # Specific client
)

# Pool istatistikleri
stats = await pool.get_pool_stats()
print(f"Toplam client: {stats['total_clients']}")
print(f"Bağlı client: {stats['connected_clients']}")

# Pool'u kapat
await pool.shutdown()
```

## 📥 Mesaj Alma ve Event Handling

### Mesaj Alma

```python
# Son mesajları al
messages = await client_manager.get_messages(
    entity="@channel",
    limit=100,
    search="arama_terimi"  # İsteğe bağlı arama
)

for message in messages:
    print(f"{message.date}: {message.message}")

# Entity bilgisi al
entity = await client_manager.get_entity("@username")
print(f"User ID: {entity.id}")
```

### Event Handlers

```python
# Mesaj event handler
async def on_new_message(event):
    sender = await event.get_sender()
    print(f"Yeni mesaj: {event.raw_text}")
    print(f"Gönderen: {sender.username}")

# Disconnect handler
async def on_disconnect():
    print("Bağlantı kesildi!")

# Handler'ları ekle
client_manager.add_message_handler(on_new_message)
client_manager.add_disconnect_handler(on_disconnect)
```

## 📊 İstatistikler ve Monitoring

### Client İstatistikleri

```python
stats = await client_manager.get_stats()

print(f"Session: {stats['session_name']}")
print(f"Durum: {stats['connection_status']}")
print(f"Gönderilen mesaj: {stats['messages_sent']}")
print(f"Başarısız mesaj: {stats['messages_failed']}")
print(f"Flood wait'ler: {stats['flood_waits']}")
print(f"Yeniden bağlanma: {stats['reconnections']}")
print(f"Uptime: {stats['uptime_seconds']} saniye")
print(f"Son aktivite: {stats['last_activity']}")
```

### Health Check

```python
# Bağlantı durumu kontrol
is_connected = await client_manager.is_connected()

if not is_connected:
    # Yeniden bağlan
    success = await client_manager.reconnect()
    if success:
        print("✅ Yeniden bağlandı")
    else:
        print("❌ Yeniden bağlanma başarısız")
```

## 🔧 Hata Yönetimi

### Hata Türleri

```python
from gavatcore_engine.telegram_client import MessageResult

result = await client_manager.send_message(entity, message)

if result.result == MessageResult.SUCCESS:
    print("✅ Başarılı")
elif result.result == MessageResult.FLOOD_WAIT:
    print(f"🚫 Flood wait: {result.flood_wait_time}s")
elif result.result == MessageResult.FORBIDDEN:
    print("❌ İzin yok")
elif result.result == MessageResult.NOT_FOUND:
    print("❌ Entity bulunamadı")
elif result.result == MessageResult.TOO_LONG:
    print("❌ Mesaj çok uzun")
elif result.result == MessageResult.FAILED:
    print(f"❌ Hata: {result.error}")
```

### Custom Error Handling

```python
try:
    result = await client_manager.send_message(entity, message)
    
    if not result.success:
        # Hata detayları
        print(f"Hata: {result.error}")
        if result.retry_after:
            print(f"Tekrar dene: {result.retry_after}s sonra")
        if result.flood_wait_time:
            print(f"Flood wait: {result.flood_wait_time}s")
            
except Exception as e:
    print(f"Beklenmeyen hata: {e}")
```

## 🛡️ Güvenlik ve Best Practices

### Session Güvenliği

```python
# String session kullanımı (önerilen)
config = ClientConfig(
    session_name="secure_bot",
    session_string="your_secure_session_string",
    api_id=api_id,
    api_hash=api_hash
)

# Session dosyası kullanımı
config = ClientConfig(
    session_name="file_bot",  # sessions/file_bot.session oluşturur
    phone="+905551234567",
    api_id=api_id,
    api_hash=api_hash
)
```

### Rate Limiting

```python
# Client level rate limiting
client_manager.rate_limit_delay = 1.0  # 1 saniye minimum gecikme

# Message bazlı rate limiting otomatik olarak uygulanır
# Flood protection da otomatik aktiftir
```

### Redis Integration

```python
from gavatcore_engine.redis_state import redis_state

# Session bilgilerini Redis'te sakla (otomatik)
# İstatistikleri Redis'e kaydet (otomatik)

# Manuel Redis kullanımı
await redis_state.connect()
await redis_state.set("custom_key", "value")
value = await redis_state.get("custom_key")
```

## 🧪 Test Etme

### Test Script Çalıştırma

```bash
# Tüm testleri çalıştır
python test_telegram_client.py

# Örnekleri çalıştır
python gavatcore_engine/telegram_client_ornek.py
```

### Unit Test

```python
import pytest
from gavatcore_engine.telegram_client import ClientConfig, TelegramClientManager

@pytest.mark.asyncio
async def test_client_config():
    config = ClientConfig(
        session_name="test",
        api_id=12345678,
        api_hash="test_hash"
    )
    
    assert config.session_name == "test"
    assert config.device_model == "GavatCore Bot"
    assert config.connection_retries == 5

@pytest.mark.asyncio
async def test_client_initialization():
    config = ClientConfig(
        session_name="test_init",
        api_id=12345678,
        api_hash="test_hash"
    )
    
    client_manager = TelegramClientManager(config)
    assert client_manager.connection_status.value == "disconnected"
```

## 📋 Konfigürasyon Referansı

### Environment Variables

```bash
# .env dosyası
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Config.py Integration

```python
# Mevcut config.py ile entegrasyon
try:
    import config
    api_id = config.TELEGRAM_API_ID
    api_hash = config.TELEGRAM_API_HASH
except ImportError:
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
```

## 🚀 Production Deployment

### Docker ile Çalıştırma

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "gavatcore_engine.telegram_client"]
```

### Systemd Service

```ini
[Unit]
Description=GavatCore Telegram Client
After=network.target

[Service]
Type=simple
User=gavatcore
WorkingDirectory=/opt/gavatcore
ExecStart=/opt/gavatcore/venv/bin/python -m gavatcore_engine.telegram_client
Restart=always

[Install]
WantedBy=multi-user.target
```

### Monitoring

```python
# Prometheus metrics (opsiyonel)
from prometheus_client import Counter, Histogram, Gauge

messages_sent = Counter('telegram_messages_sent_total')
messages_failed = Counter('telegram_messages_failed_total') 
connection_status = Gauge('telegram_connection_status')
message_send_duration = Histogram('telegram_message_send_duration_seconds')
```

## ❓ Sık Sorulan Sorular

### Q: Session dosyası nerede saklanır?
A: `sessions/` klasöründe `{session_name}.session` olarak saklanır.

### Q: Flood wait nasıl yönetilir?
A: Otomatik olarak yönetilir. Flood wait durumunda client bekler ve sonra tekrar dener.

### Q: Multiple bot nasıl kullanılır?
A: `TelegramClientPool` sınıfını kullanın. Her bot için ayrı session gereklidir.

### Q: 2FA (Two-Factor Authentication) destekleniyor mu?
A: Hayır, şu anda 2FA desteklenmiyor. Session string kullanmanız önerilir.

### Q: Rate limiting nasıl çalışır?
A: Her chat için otomatik rate limiting uygulanır. Default 1 saniye minimum gecikme vardır.

## 📞 Destek

Sorun yaşadığınızda:

1. Log dosyalarını kontrol edin
2. Test scriptlerini çalıştırın
3. Redis bağlantısını kontrol edin
4. API credentials'ını doğrulayın

## 📝 Changelog

### v1.0.0
- ✅ İlk stable release
- ✅ Telethon integration
- ✅ Redis state management
- ✅ Client pool support
- ✅ Comprehensive error handling
- ✅ Production-ready logging

---

**💡 Not**: Bu modül production ortamında kullanıma hazırdır. Gerçek API credentials ile test edilmesi önerilir. 