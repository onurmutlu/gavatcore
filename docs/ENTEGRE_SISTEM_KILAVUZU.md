# 🚀 GavatCore Engine - Entegre Sistem Kılavuzu

Complete integrated system guide for GavatCore Auto-Messaging Engine with all modules working together.

## 🌟 Sistem Genel Bakış

GavatCore Engine artık tüm modüllerin entegre çalıştığı production-ready bir sistemdir:

### 🧩 **Entegre Modüller**
- **📱 Telegram Client**: Telethon tabanlı multi-bot yönetimi
- **📬 Message Pool**: Priority-based mesaj kuyruğu sistemi
- **⏰ Scheduler Engine**: Cron ve interval tabanlı görev zamanlama
- **🧠 AI Blending**: Intelligent mesaj geliştirme sistemi
- **👑 Admin Commands**: Comprehensive admin komut sistemi
- **📡 Redis State**: Centralized state management
- **🌐 FastAPI**: RESTful API interface

### 🔗 **Sistem Mimarisi**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Production      │    │  Integration    │
│   Web Server    │◄──►│  Launcher        │◄──►│  Test Suite     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REDIS STATE MANAGER                        │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│ Telegram Client │ Message Pool    │ Scheduler       │ AI System │
│ Pool Manager    │ Queue System    │ Engine          │ Blending  │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## 🚀 Hızlı Başlangıç

### 1. 📋 Ön Gereksinimler

```bash
# Python 3.11+ gerekli
python --version

# Redis server kurulu ve çalışıyor olmalı
redis-cli ping
# PONG döndürmeli

# Gerekli dependencies
pip install -r gavatcore_engine/requirements.txt
```

### 2. 🔧 Konfigürasyon

**config.py dosyanızda şunlar olmalı:**
```python
# Telegram API Credentials
TELEGRAM_API_ID = 12345678
TELEGRAM_API_HASH = "your_api_hash_here"

# Bot Phone Numbers (According to memory: yayincilara + xxxgeisha)
YAYINCILARA_PHONE = "+905382617727"
XXXGEISHA_PHONE = "+905486306226"

# Redis Configuration (optional)
REDIS_URL = "redis://localhost:6379/0"
```

### 3. 🚀 Sistem Başlatma

**Ana başlatma scripti:**
```bash
./start_gavatcore_engine.py
```

**Menü seçenekleri:**
1. **🚀 Complete Integrated System** (Önerilen)
2. **🌐 FastAPI Server Only**
3. **🧪 Test System Components**
4. **📊 Show System Status**
5. **🛑 Exit**

## 🔧 Detaylı Kurulum

### 1. Environment Setup

```bash
# Çalışma dizinini hazırla
cd /path/to/gavatcore

# Gerekli dizinleri oluştur
mkdir -p sessions data/profiles data/analytics logs reports

# Environment variables (opsiyonel)
export TELEGRAM_API_ID=12345678
export TELEGRAM_API_HASH=your_api_hash
export REDIS_URL=redis://localhost:6379/0
```

### 2. Redis Server

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### 3. Bot Session Dosyaları

Session dosyalarını `sessions/` dizinine koyun:
```
sessions/
├── yayincilara.session
├── xxxgeisha.session
└── [other_bots].session
```

## 🎯 Kullanım Senaryoları

### 1. 🚀 Production Launcher ile Başlatma

**Tüm sistem integrated olarak:**
```bash
./start_gavatcore_engine.py
# Option 1 seçin: Complete Integrated System
```

**Manuel launcher:**
```bash
python gavatcore_engine/integrations/production_launcher.py
```

### 2. 🌐 FastAPI Server ile API Kullanımı

**Server başlatma:**
```bash
./start_gavatcore_engine.py
# Option 2 seçin: FastAPI Server Only

# Veya direct:
uvicorn gavatcore_engine.main:app --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- **Docs**: http://localhost:8000/docs
- **Status**: http://localhost:8000/status
- **Health**: http://localhost:8000/health
- **Stats**: http://localhost:8000/statistics

### 3. 📤 Mesaj Gönderme

**API ile:**
```bash
curl -X POST "http://localhost:8000/send-message" \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "@username",
    "message": "Merhaba! 🤖",
    "priority": "high",
    "session_name": "yayincilara"
  }'
```

**Direct Python:**
```python
from gavatcore_engine.message_pool import message_pool, Message, MessageType

# Mesaj oluştur
message = Message(
    target_entity="@channel",
    content="🌹 Merhaba sevgili takipçiler!",
    message_type=MessageType.TEXT,
    session_name="yayincilara"
)

# Kuyruğa ekle
message_id = await message_pool.add_message(message)
```

### 4. ⏰ Görev Zamanlama

**API ile:**
```bash
curl -X POST "http://localhost:8000/schedule-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "SCHEDULED_MESSAGE",
    "target_entity": "@channel",
    "message_content": "⏰ Zamanlanmış mesaj!",
    "cron_expression": "0 */2 * * *",
    "session_name": "xxxgeisha"
  }'
```

**Direct Python:**
```python
from gavatcore_engine.scheduler_engine import scheduler_engine, ScheduledTask, TaskType

# Görev oluştur
task = ScheduledTask(
    task_type=TaskType.RECURRING_MESSAGE,
    target_entity="@vip_group",
    message_content="🎭 VIP üyeler için özel mesaj!",
    cron_expression="0 9,21 * * *",  # Günde 2 kez
    session_name="xxxgeisha"
)

# Scheduler'a ekle
task_id = await scheduler_engine.add_task(task)
```

### 5. 🤖 Bot Yönetimi

**Yeni bot ekleme:**
```bash
curl -X POST "http://localhost:8000/add-bot" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "new_bot",
    "api_id": 12345678,
    "api_hash": "api_hash",
    "phone": "+905551234567",
    "device_model": "GavatCore New Bot"
  }'
```

**Bot kaldırma:**
```bash
curl -X DELETE "http://localhost:8000/bot/bot_name"
```

## 📊 Monitoring ve İstatistikler

### 1. 📈 System Status

**API ile:**
```bash
curl http://localhost:8000/status
```

**CLI ile:**
```bash
./start_gavatcore_engine.py
# Option 4 seçin: Show System Status
```

### 2. 📊 Detailed Statistics

```bash
curl http://localhost:8000/statistics
```

**Örnek çıktı:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "counters": {
    "messages_sent": 1250,
    "messages_failed": 23
  },
  "telegram_pool": {
    "total_clients": 2,
    "connected_clients": 2
  },
  "message_pool": {
    "pending_messages": 5,
    "processing_messages": 1
  },
  "scheduler": {
    "active_tasks": 8,
    "completed_tasks": 142
  }
}
```

### 3. 🏥 Health Checks

```bash
curl http://localhost:8000/health
```

**Monitoring Redis:**
```bash
redis-cli
> KEYS system_*
> HGETALL system_stats
> HGETALL system_health
```

## 🧪 Testing ve Debugging

### 1. 🧪 Integration Tests

**Tam sistem testi:**
```bash
./test_full_integration.py
```

**Component testleri:**
```bash
# Telegram client test
python test_telegram_client.py

# Scheduler test
python test_scheduler_engine.py

# Specific module tests
./start_gavatcore_engine.py
# Option 3 seçin: Test System Components
```

### 2. 🔍 Debug Mode

**Verbose logging:**
```bash
export LOG_LEVEL=DEBUG
./start_gavatcore_engine.py
```

**Manual component testing:**
```python
# Redis test
from gavatcore_engine.redis_state import redis_state
await redis_state.connect()
await redis_state.ping()

# Message pool test
from gavatcore_engine.message_pool import message_pool
await message_pool.initialize()
stats = await message_pool.get_statistics()
print(stats)
```

### 3. 📋 Log Monitoring

**Log dosyaları:**
```bash
tail -f logs/gavatcore_engine.log
tail -f logs/telegram_client.log
tail -f logs/scheduler_engine.log
```

**Redis logs:**
```bash
redis-cli MONITOR
```

## 🛡️ Production Deployment

### 1. 🐳 Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_gavatcore_engine.py"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  gavatcore:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./sessions:/app/sessions
      - ./data:/app/data
      - ./logs:/app/logs

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 2. 🔧 Systemd Service

```ini
[Unit]
Description=GavatCore Engine
After=network.target redis.service

[Service]
Type=simple
User=gavatcore
WorkingDirectory=/opt/gavatcore
ExecStart=/opt/gavatcore/venv/bin/python start_gavatcore_engine.py
Restart=always
RestartSec=10

Environment=REDIS_URL=redis://localhost:6379/0
Environment=LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
```

### 3. 📊 Production Monitoring

**Prometheus Metrics:**
```python
# Custom metrics endpoint
from prometheus_client import Counter, Histogram, Gauge

messages_sent = Counter('gavatcore_messages_sent_total')
message_duration = Histogram('gavatcore_message_duration_seconds')
active_clients = Gauge('gavatcore_active_clients')
```

**Health Check Script:**
```bash
#!/bin/bash
# health_check.sh

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ $response -eq 200 ]; then
    echo "✅ GavatCore Engine healthy"
    exit 0
else
    echo "❌ GavatCore Engine unhealthy (HTTP $response)"
    exit 1
fi
```

## 🔧 Konfigürasyon Referansı

### 1. 📋 Environment Variables

```bash
# Core settings
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
MESSAGE_POOL_SIZE=1000
SCHEDULER_CHECK_INTERVAL=1
RATE_LIMIT_DELAY=1.0

# Security
ADMIN_USER_IDS=123456789,987654321
```

### 2. 🤖 Bot Profiles

**data/profiles/bot_name.json:**
```json
{
  "name": "Bot Name",
  "phone": "+905551234567",
  "active": true,
  "description": "Bot description",
  "personality": "friendly",
  "target_groups": ["@group1", "@group2"],
  "schedule": {
    "active_hours": "09:00-22:00",
    "timezone": "Europe/Istanbul"
  }
}
```

### 3. ⚙️ Advanced Settings

**gavatcore_engine/config.py:**
```python
class Settings(BaseSettings):
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10

    # Message pool settings
    message_pool_size: int = 1000
    message_retention_hours: int = 24

    # Scheduler settings
    scheduler_check_interval: int = 1
    max_concurrent_tasks: int = 10

    # Telegram settings
    rate_limit_delay: float = 1.0
    flood_wait_threshold: int = 60
    connection_retries: int = 5

    # AI settings
    ai_enhancement_enabled: bool = True
    ai_response_timeout: int = 30
```

## ❓ Troubleshooting

### 1. 🔧 Common Issues

**Redis Connection Failed:**
```bash
# Check Redis status
redis-cli ping
# If not running:
brew services start redis  # macOS
sudo systemctl start redis-server  # Linux
```

**Bot Authentication Failed:**
```bash
# Check session files
ls -la sessions/
# Re-authenticate if needed
rm sessions/bot_name.session
# Restart system to trigger re-auth
```

**High Memory Usage:**
```bash
# Check Redis memory
redis-cli INFO memory
# Clear old data
redis-cli FLUSHDB
```

### 2. 📋 Debug Commands

```bash
# System status
curl http://localhost:8000/status | jq

# Redis inspection
redis-cli
> KEYS *
> HGETALL system_stats
> LLEN message_queue

# Process monitoring
ps aux | grep python
netstat -tulpn | grep :8000
```

### 3. 🚨 Error Recovery

**Graceful restart:**
```bash
# Send SIGTERM for graceful shutdown
pkill -TERM -f "gavatcore"

# Wait for cleanup, then restart
./start_gavatcore_engine.py
```

**Emergency reset:**
```bash
# Clear Redis (BE CAREFUL!)
redis-cli FLUSHALL

# Remove lock files
rm -f *.pid *.lock

# Restart system
./start_gavatcore_engine.py
```

## 📈 Performance Optimization

### 1. ⚡ Redis Optimization

```bash
# Redis configuration adjustments
echo "maxmemory 1gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
sudo systemctl restart redis
```

### 2. 🚀 Python Performance

```bash
# Use uvloop for better async performance
pip install uvloop

# In code:
import uvloop
uvloop.install()
```

### 3. 📊 Monitoring Metrics

**Key metrics to monitor:**
- Message throughput (messages/minute)
- Redis memory usage
- Active Telegram connections
- Task completion rate
- Error rate percentage

---

## 🎉 Sonuç

GavatCore Engine artık tamamen entegre, production-ready bir sistem olarak çalışıyor!

**✅ Tamamlanan Özellikler:**
- Tüm modüller entegre ve çalışıyor
- Production launcher hazır
- Comprehensive test suite
- API interface aktif
- Monitoring ve logging sistemi
- Error handling ve resilience
- Documentation complete

**🚀 Kullanıma Hazır:**
```bash
# Single command to start everything:
./start_gavatcore_engine.py
```

Sistem artık gerçek bot'larınızla production ortamında kullanıma hazır! 🎯
