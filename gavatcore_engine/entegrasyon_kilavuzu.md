# GavatCore Engine Entegrasyon Kılavuzu

## 🚀 GavatCore Engine Nedir?

GavatCore Engine, mevcut Telegram bot sisteminizi modern FastAPI backend ile güçlendiren production-grade bir entegrasyon katmanıdır.

### ✨ Özellikler

- **Legacy Bot Entegrasyonu**: Mevcut botlarınız (yayincilara, xxxgeisha) ile uyumlu
- **FastAPI Backend**: Modern REST API ile bot yönetimi
- **Redis State Management**: Tüm bot durumları Redis'te saklanır
- **AI Response Generation**: Akıllı mesaj yanıtları
- **Message Queue System**: Mesajlar öncelik sırasına göre işlenir
- **Scheduler Engine**: Zamanlanmış mesajlar ve recurring tasklar
- **Production Ready**: Async, scalable, monitoring ile

## 📁 Proje Yapısı

```
gavatcore_engine/
├── __init__.py                 # Ana modül
├── config.py                   # Konfigürasyon (legacy config entegreli)
├── logger.py                   # JSON structured logging
├── redis_state.py              # Redis state management
├── message_pool.py             # Message queue sistemi
├── telegram_client.py          # Telegram client wrapper
├── scheduler_engine.py         # Task scheduler
├── admin_commands.py           # Admin komutları
├── ai_blending.py              # AI response generation
├── main.py                     # FastAPI application
├── launcher.py                 # Production launcher
├── requirements.txt            # Dependencies
├── README.md                   # Dokumentasyon
└── integrations/               # Entegrasyon katmanı
    ├── __init__.py
    ├── legacy_bot_adapter.py   # Mevcut bot entegrasyonu
    ├── message_worker.py       # Enhanced message worker
    └── production_launcher.py  # Production launcher
```

## 🔧 Kurulum

### 1. Dependencies Kurulumu

```bash
cd gavatcore_engine
pip install -r requirements.txt
```

### 2. Redis Kurulumu

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server
```

### 3. Environment Konfigürasyonu

Mevcut `config.py` dosyanız otomatik olarak yüklenecek, ek olarak `.env` dosyası oluşturabilirsiniz:

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
LOG_LEVEL=INFO
ADMIN_USER_IDS=123456789,987654321
```

## 🚀 Çalıştırma

### Production Launcher ile Çalıştırma (Önerilen)

```bash
python gavatcore_engine/integrations/production_launcher.py
```

Bu launcher:
- Mevcut bot session'larınızı otomatik bulur
- FastAPI engine'i başlatır
- Legacy bot adapter ile entegre çalışır
- Graceful shutdown desteği

### FastAPI Server Çalıştırma

```bash
# Development
python -m gavatcore_engine.main

# Production
uvicorn gavatcore_engine.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## 🤖 Bot Entegrasyonu

### Mevcut Botlarınız

Engine otomatik olarak şu botları entegre eder:

1. **yayincilara** - `data/personas/yayincilara.json`
2. **xxxgeisha** - `data/personas/xxxgeisha.json`

### Session Dosyaları

Engine şu session dosyalarını arar:
- `sessions/yayincilara_conversation.session`
- `sessions/xxxgeisha_conversation.session`
- `sessions/_{phone_number}.session`

## 🌐 API Kullanımı

### Bot Status Kontrolü

```bash
curl http://localhost:8000/bots
```

### Mesaj Gönderme

```bash
curl -X POST http://localhost:8000/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "yayincilara",
    "content": "Merhaba! Bu FastAPI engine üzerinden gönderiliyor.",
    "target_chat_id": 123456789,
    "priority": "high"
  }'
```

### Mesaj Zamanlama

```bash
curl -X POST http://localhost:8000/schedule-message \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "xxxgeisha",
    "content": "Zamanlanmış mesaj",
    "target_chat_id": 123456789,
    "schedule_time": "2024-01-01T15:30:00",
    "recurring": true,
    "cron_expression": "0 15 * * *"
  }'
```

### AI Response Generation

```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "bot_username": "yayincilara",
    "user_message": "Nasılsın?",
    "conversation_context": {},
    "user_profile": {"user_id": 123456789}
  }'
```

### System Stats

```bash
curl http://localhost:8000/stats
```

## 🔧 Admin Komutları

### API ile Admin Komutları

```bash
curl -X POST http://localhost:8000/admin/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "status",
    "args": [],
    "user_id": 123456789
  }'
```

### Mevcut Admin Komutları

- `status` - Sistem durumu
- `stats` - İstatistikler
- `bot_status` - Bot durumları
- `list_tasks` - Zamanlanmış tasklar
- `cancel_task <task_id>` - Task iptal etme
- `clear_queue` - Message queue temizleme
- `emergency_stop` - Acil durdurma

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Message Queue Status

```bash
curl http://localhost:8000/admin/messages
```

### Scheduled Tasks

```bash
curl http://localhost:8000/admin/tasks
```

## 🔄 Workflow

### 1. Incoming Message Flow

```
Telegram Message → Legacy Bot → Legacy Adapter → AI Generation → Message Pool → Worker → Send
```

### 2. API Message Flow

```
API Request → Message Pool → Worker → Legacy Bot → Telegram
```

### 3. Scheduled Message Flow

```
Scheduler → Task Execution → Message Pool → Worker → Legacy Bot → Telegram
```

## 🛠️ Geliştirme

### Log Monitoring

```bash
# JSON logs
tail -f logs/gavatcore_engine.log | jq .

# Redis monitoring
redis-cli monitor
```

### Custom Bot Ekleme

`legacy_bot_adapter.py` dosyasında `_load_bot_configs` fonksiyonunu güncelleyin:

```python
bot_files = {
    "yayincilara": "yayincilara.json",
    "xxxgeisha": "xxxgeisha.json",
    "yeni_bot": "yeni_bot.json",  # Yeni bot ekle
}
```

### Custom AI Personalities

`ai_blending.py` dosyasında personality tanımları:

```python
personalities = {
    "yayincilara": {
        "style": "flirty",
        "tone": "playful",
        "response_length": "medium",
    },
    "xxxgeisha": {
        "style": "mysterious",
        "tone": "seductive", 
        "response_length": "short",
    },
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Bot Session Not Found**
   ```
   ❌ No session files found for bot_name
   ```
   - Session dosyalarının `sessions/` klasöründe olduğunu kontrol edin
   - Persona JSON dosyalarında telefon numaralarını kontrol edin

2. **Redis Connection Error**
   ```
   ❌ Redis connection failed
   ```
   - Redis servisinin çalıştığını kontrol edin: `redis-cli ping`
   - Redis konfigürasyonunu kontrol edin

3. **Bot Not Authorized**
   ```
   ❌ Client not authorized
   ```
   - Session dosyalarının corrupt olmadığını kontrol edin
   - Telegram'da bot hesabının banned olmadığını kontrol edin

### Debug Mode

```bash
LOG_LEVEL=DEBUG python gavatcore_engine/integrations/production_launcher.py
```

## 📈 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY gavatcore_engine/ ./gavatcore_engine/
COPY requirements.txt .
COPY sessions/ ./sessions/
COPY data/ ./data/

RUN pip install -r gavatcore_engine/requirements.txt

CMD ["python", "gavatcore_engine/integrations/production_launcher.py"]
```

### Systemd Service

```ini
[Unit]
Description=GavatCore Engine
After=network.target redis.service

[Service]
Type=simple
User=gavatcore
WorkingDirectory=/opt/gavatcore
ExecStart=/opt/gavatcore/venv/bin/python gavatcore_engine/integrations/production_launcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 🔐 Security

- Admin user ID'leri environment variable ile ayarlayın
- Redis password kullanın production'da
- Session dosyalarını güvenli tutun
- API endpoint'lerini firewall ile koruyun

## 📞 Support

Bu entegrasyon sistemi mevcut GavatCore altyapınızı bozmadan modern FastAPI backend ekler. Herhangi bir sorun durumunda:

1. Log dosyalarını kontrol edin
2. Health check endpoint'ini test edin
3. Redis connection'ını kontrol edin
4. Bot session durumlarını kontrol edin

**🎯 Sonuç**: Artık mevcut botlarınız modern FastAPI backend ile güçlendirildi ve REST API üzerinden yönetilebilir! 