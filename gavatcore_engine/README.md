# GavatCore Auto-Messaging Engine

Production-grade FastAPI backend for automated Telegram messaging system with async architecture, Redis state management, and AI blending capabilities.

## 🚀 Features

- **Async Architecture**: Full async/await support with FastAPI
- **Redis State Management**: Scalable state management and caching
- **Message Pool**: Advanced message queuing with priority support
- **Scheduler Engine**: Cron-like scheduling for automated messages
- **Telegram Integration**: Robust Telegram client management
- **AI Blending**: Character personality management (placeholder)
- **Admin Commands**: Comprehensive admin interface
- **Worker-based**: Scalable worker architecture
- **JSON Logging**: Structured logging with structlog
- **Production Ready**: Best practices and error handling

## 📁 Architecture

```
gavatcore_engine/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── logger.py                # Structured logging
├── redis_state.py           # Redis state management
├── message_pool.py          # Message queuing system
├── scheduler_engine.py      # Task scheduling
├── telegram_client.py       # Telegram client wrapper
├── admin_commands.py        # Admin command handlers
├── ai_blending.py          # AI personality engine (placeholder)
├── main.py                 # FastAPI application
├── launcher.py             # Production launcher
├── requirements.txt        # Dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Installation

1. **Install Dependencies**:
```bash
cd gavatcore_engine
pip install -r requirements.txt
```

2. **Setup Environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start Redis**:
```bash
redis-server
```

4. **Run the Engine**:
```bash
python launcher.py
```

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# Telegram API
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key

# Admin Users
ADMIN_USER_IDS=123456789,987654321
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /stats` - System statistics

### Messaging
- `POST /messages/send` - Send immediate message
- `POST /messages/schedule` - Schedule message
- `GET /bots/status` - Bot status

### AI & Admin
- `POST /ai/generate` - Generate AI response
- `POST /admin/command` - Execute admin command

## 🎯 Usage Examples

### Send Immediate Message
```python
import httpx

response = httpx.post("http://localhost:8000/messages/send", json={
    "content": "Merhaba! Nasılsın?",
    "bot_id": "yayincilara",
    "target_username": "example_user",
    "message_type": "dm",
    "priority": "high"
})
```

### Schedule Message
```python
response = httpx.post("http://localhost:8000/messages/schedule", json={
    "content": "Zamanlanmış mesaj!",
    "bot_id": "xxxgeisha",
    "scheduled_at": "2024-01-01T12:00:00",
    "target_chat_id": 123456789,
    "recurring_interval": 3600  # Every hour
})
```

### Admin Commands
```python
response = httpx.post("http://localhost:8000/admin/command", json={
    "command": "status",
    "args": {},
    "admin_user_id": 123456789
})
```

## 🏗️ Architecture Components

### Message Pool
- Priority-based message queuing
- Retry logic with exponential backoff
- Message status tracking
- Redis-backed persistence

### Scheduler Engine
- Cron-like task scheduling
- Recurring task support
- Task status management
- Pluggable task handlers

### Redis State Management
- Connection pooling
- Automatic serialization
- Rate limiting support
- Session management

### Telegram Client
- Async Telegram integration
- Flood wait handling
- Session management
- Health monitoring

## 🔐 Security Features

- Admin user verification
- Rate limiting
- Secure configuration management
- Error handling and logging

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### System Stats
```bash
curl http://localhost:8000/stats
```

### Admin Status
```bash
curl -X POST http://localhost:8000/admin/command \
  -H "Content-Type: application/json" \
  -d '{"command": "status", "args": {}, "admin_user_id": 123456789}'
```

## 🚀 Production Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "launcher.py"]
```

### Systemd Service
```ini
[Unit]
Description=GavatCore Auto-Messaging Engine
After=network.target redis.service

[Service]
Type=simple
User=gavatcore
WorkingDirectory=/opt/gavatcore_engine
ExecStart=/usr/bin/python3 launcher.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 🔧 Development

### Running in Development
```bash
# With auto-reload
DEBUG=true python launcher.py

# Or use uvicorn directly
uvicorn gavatcore_engine.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run with pytest (when tests are added)
pytest tests/

# Manual API testing
curl -X GET http://localhost:8000/health
```

## 📝 Logging

The engine uses structured JSON logging:

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "info",
  "logger": "scheduler_engine",
  "event": "Task scheduled",
  "task_id": "abc123",
  "task_type": "scheduled_message"
}
```

## 🤝 Integration

### With Existing Bots
```python
from gavatcore_engine.telegram_client import TelegramClientManager

# Initialize client
client = TelegramClientManager("session_name", "bot_username")
await client.initialize()

# Add message handler
client.add_message_handler(your_message_handler)
```

### With AI Systems
```python
from gavatcore_engine.ai_blending import ai_blending

# Generate response
response = await ai_blending.generate_response(
    bot_username="yayincilara",
    user_message="Merhaba!",
    conversation_context={}
)
```

## 📈 Scalability

- **Horizontal Scaling**: Multiple worker instances
- **Redis Clustering**: For large deployments
- **Load Balancing**: Behind nginx/haproxy
- **Monitoring**: Prometheus metrics ready

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis status
   redis-cli ping
   ```

2. **Telegram API Errors**
   ```bash
   # Verify API credentials in .env
   # Check session file permissions
   ```

3. **High Memory Usage**
   ```bash
   # Monitor message queue sizes
   curl http://localhost:8000/stats
   ```

## 📄 License

This project is part of the GavatCore ecosystem.

## 🔗 Links

- **Documentation**: `/docs` (FastAPI auto-docs)
- **Health Check**: `/health`
- **API Stats**: `/stats` 