# 🚀 GavatCore SaaS API

**Bot-as-a-Service platform with Telegram userbot automation**

## 📋 Features

- 🤖 **Multi-Bot Management**: Create and manage multiple Telegram userbot instances
- 💳 **Payment Integration**: Stripe, Telegram Stars, and TON cryptocurrency payments
- 🎯 **AI-Powered**: GPT integration with character personalities
- 📊 **Analytics**: User behavior tracking and insights
- 🔄 **Auto-Scaling**: Cloud-ready architecture with Docker support
- 🛡️ **Security**: JWT authentication and role-based access

## 🏗️ Architecture

```
gavatcore-api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   └── exceptions.py    # Custom exception classes
│   ├── database/
│   │   └── connection.py    # Database setup and connections
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── subscription.py  # Subscription model
│   │   ├── bot_instance.py  # Bot instance model
│   │   └── payment.py       # Payment model
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── payment.py       # Payment processing
│   │   ├── bots.py          # Bot management
│   │   └── users.py         # User management
│   └── services/           # Business logic (TODO)
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker setup
├── Dockerfile             # Container definition
└── setup.py              # Development setup script
```

## 💰 Pricing Plans

| Plan | Price | Duration | Features |
|------|-------|----------|----------|
| **Deneme** | Ücretsiz | 1 gün | 1 bot, 100 coin |
| **Başlangıç** | ₺499 | 30 gün | 1 bot, 500 coin, GPT |
| **Pro** | ₺799 | 30 gün | 3 bot, 2000 coin, Scheduler |
| **Deluxe** | ₺1499 | 30 gün | 5 bot, Sınırsız coin, Analytics |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and start with Docker
cd gavatcore-api
docker-compose up -d

# API will be available at http://localhost:8000
# PgAdmin at http://localhost:5050 (admin@gavatcore.com / admin123)
```

### Option 2: Local Development

```bash
# 1. Setup environment
python3 setup.py

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# 3. Start the API
uvicorn app.main:app --reload

# 4. Test the API
python test_api.py
```

## 📖 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Pricing Plans**: http://localhost:8000/api/payment/plans

## 🔧 Configuration

Create `.env` file with your settings:

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://gavatcore:password123@localhost:5432/gavatcore_saas

# Payments
STRIPE_SECRET_KEY=sk_test_...
TELEGRAM_BOT_TOKEN=123456:ABC...
TON_WALLET_ADDRESS=UQA...

# OpenAI
OPENAI_API_KEY=sk-proj-...
```

## 🤖 Bot Personalities

- **@gawatbaba**: System administrator with coin checking abilities
- **@yayincilara**: Gaming-focused AI with Turkish-Russian personality
- **@xxxgeisha**: Entertainment-focused sophisticated AI

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- [x] API structure and endpoints
- [x] Database models
- [x] Payment integration setup
- [ ] Stripe webhook implementation
- [ ] Basic bot instance creation

### Phase 2: Core Features
- [ ] User authentication system
- [ ] Telegram Stars integration
- [ ] TON payment processing
- [ ] Bot management dashboard

### Phase 3: Advanced Features
- [ ] React frontend panel
- [ ] Analytics dashboard
- [ ] Auto-scaling bot instances
- [ ] Custom AI personality creation

## 🧪 Testing

```bash
# Test imports and basic functionality
python test_api.py

# Test specific endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/payment/plans
```

## 📊 Database Schema

```sql
-- Users table
users (id, telegram_user_id, username, email, ...)

-- Subscriptions table  
subscriptions (id, user_id, plan_name, expires_at, ...)

-- Bot instances table
bot_instances (id, user_id, bot_name, personality, ...)

-- Payments table
payments (id, user_id, amount, payment_method, ...)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary and confidential.

---

**Built with 🔥 by GavatCore Team** 