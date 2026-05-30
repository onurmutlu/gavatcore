# 🚀 GAVATCore - Enterprise-Grade AI & Bot Management Platform

**Modern, AI-destekli Telegram bot yönetimi ve sosyal gaming platformu. Mikroservis mimarisi ile geliştirilmiş, ölçeklenebilir altyapı.**

**Modern AI-powered Telegram bot management and social gaming platform. Built with microservice architecture for scalable infrastructure.**

---

## 🎯 **TEK GİRİŞ NOKTASI - UNIFIED ENTRY POINT**

**✨ Yeni Özellik**: Tüm sistem bileşenleri artık tek bir `main.py` dosyası üzerinden yönetiliyor!

**✨ New Feature**: All system components are now managed through a single `main.py` file!

```bash
# 🌟 Tüm sistemi başlat / Start entire system
python3 start.py --all

# 🔍 Monitoring ile başlat / Start with monitoring
python3 launch_with_monitor.py --api

# 🤖 Sadece botları başlat / Start bots only
python3 start.py --bot

# 🔌 Sadece API'leri başlat / Start APIs only
python3 start.py --api

# 🎮 Özelleştirilmiş başlatma / Custom startup
python3 start.py --userbot --flask-api --token-api
```

---

## 📁 **PROJE YAPISI / PROJECT STRUCTURE**

```
gavatcore/
├── 🚀 start.py                 # 🎯 BAŞLATICI / STARTUP SCRIPT (recommended)
├── 🔍 launch_with_monitor.py   # Complete launcher with monitoring
├── 📊 monitor.py               # Real-time monitoring system
├── 🔧 main.py                  # Unified entry point system
├── 🔄 legacy_entry_points.py   # Legacy mapping reference
├── 🔌 apis/                    # API Servisleri / API Services
│   ├── production_bot_api.py   # Ana bot API (Port 5050)
│   ├── token_system/           # Token ekonomi sistemi
│   │   └── xp_token_api_sync.py # XP Token API (Port 5051)
│   ├── admin/                  # Admin dashboard APIs
│   ├── bot_management/         # Bot yönetim API'leri
│   └── reply_system_api.py     # Yanıt sistemi API'si
│
├── 🤖 services/                # Platform Servisleri / Platform Services
│   └── telegram/               # Telegram Bot Servisleri
│       └── bot_manager/        # Bot yönetim sistemi
│           ├── bot_system.py   # Unified bot kontrolcüsü
│           ├── bot_config.py   # Bot konfigürasyonları
│           └── spam_aware_system.py # Spam korumalı sistem
│
├── 🧠 character_engine/        # AI Karakter Sistemi / AI Character System
│   ├── character_manager.py    # Karakter yöneticisi
│   ├── gpt_reply_generator.py  # GPT yanıt üreteci
│   ├── personality_router.py   # Kişilik yönlendirici
│   └── memory_context_tracker.py # Hafıza takip sistemi
│
├── 🎮 core/                    # Çekirdek İş Modülleri / Core Business Modules
│   ├── coin_checker.py         # Coin kontrol sistemi
│   ├── reply_engine.py         # Yanıt motoru
│   ├── preset_manager.py       # Preset yöneticisi
│   ├── database_manager.py     # Veritabanı yöneticisi
│   ├── redis_manager.py        # Redis yöneticisi
│   ├── postgresql_manager.py   # PostgreSQL yöneticisi
│   └── mongodb_manager.py      # MongoDB yöneticisi
│
├── 🌐 gavatcore-api/           # FastAPI SaaS Platformu / FastAPI SaaS Platform
│   └── app/
│       ├── main.py             # FastAPI ana dosyası (Port 8000)
│       ├── core/               # Core ayarları
│       ├── routes/             # API rotaları
│       └── database/           # Veritabanı bağlantıları
│
├── 📱 gavatcore_panel/         # Flutter Admin Panel
│   ├── lib/                    # Flutter uygulaması
│   ├── web/                    # Web konfigürasyonları
│   └── assets/                 # Statik kaynaklar
│
├── 🏗️ infrastructure/          # DevOps & Infrastructure
│   ├── docker/                 # Docker konfigürasyonları
│   ├── kubernetes/             # K8s manifests
│   └── config/                 # Configuration (requirements, mypy, pytest, env template)
│
├── 📊 integrations/            # Entegrasyon Sistemleri / Integration Systems
│   └── reply_system_integration.py # Yanıt sistemi entegrasyonu
│
├── 🎭 modes/                   # Bot Modları / Bot Modes
│   └── manualplus_mode.py      # Manual+ modu
│
├── 🚀 launchers/               # Eski Başlatıcılar / Legacy Launchers (DEPRECATED)
├── 📊 scripts/                 # Otomation Scripts
├── 🧪 tests/                   # Test Dosyaları / Test Files
├── 📈 reports/                 # Raporlar / Reports
├── 📚 docs/                    # Dokümantasyon / Documentation
├── 🔧 utilities/               # Yardımcı Araçlar / Utility Tools
├── 📦 data/                    # Veri & Storage / Data & Storage
│   ├── personas/               # Bot kişilikleri
│   ├── reply_presets.json      # Yanıt preset'leri
│   └── ...
├── 📁 sessions/                # Telegram session dosyaları
└── 📂 logs/                    # Log dosyaları
```

---

## ✨ **ÖZELLİKLER / FEATURES**

### 🎯 **Unified Entry Point System**
- **Tek Komut**: Tüm sistem bileşenleri tek `main.py` ile yönetiliyor
- **Modüler Başlatma**: Sadece ihtiyacınız olan bileşenleri başlatın
- **CLI Kontrolü**: Zengin komut satırı seçenekleri
- **Sağlık Kontrolü**: Otomatik servis sağlık kontrolü
- **Graceful Shutdown**: Temiz sistem kapatma

### 🤖 **Gelişmiş Bot Yönetimi / Advanced Bot Management**
- **3 Ana Bot**: Lara (Flörtöz Yayıncı), BabaGavat (Sokak Zekası), Geisha (Gizemli Moderatör)
- **Unified Bot System**: Tüm botlar tek merkezden yönetim
- **Character Engine**: AI-powered kişilik sistemleri
- **GPT-4 Entegrasyonu**: Gelişmiş AI sohbet yetenekleri
- **Memory System**: Bağlamsal hafıza takibi
- **Spam-Aware Technology**: Akıllı spam koruması

### 🔌 **API Altyapısı / API Infrastructure**
- **Multi-Port Architecture**: 
  - Port 5050: Ana Flask API
  - Port 5051: XP Token API
  - Port 8000: FastAPI SaaS Platform
- **RESTful Design**: Modern API tasarımı
- **Health Endpoints**: Otomatik sağlık kontrolü
- **Structured Logging**: Production-ready log yönetimi

### 🎮 **Social Gaming & Token Economy**
- **GavatCoin System**: Dijital token ekonomisi
- **XP Management**: Kullanıcı deneyim puanlama
- **Reward System**: Ödül ve bonus mekanizmaları
- **Leaderboards**: Sıralama sistemleri

### 🧠 **AI & Machine Learning**
- **Character Personalities**: Benzersiz bot kişilikleri
- **Dynamic Responses**: Bağlam-aware yanıt sistemi
- **Conversation Memory**: Sohbet geçmişi takibi
- **Behavioral Analytics**: Davranış analizi

---

## 🚀 **HIZLI BAŞLANGIÇ / QUICK START**

### 1. **Kurulum / Installation**
```bash
# Repository'yi klonlayın / Clone repository
git clone https://github.com/username/gavatcore.git
cd gavatcore

# Bağımlılıkları yükleyin / Install dependencies
pip install -r infrastructure/config/requirements.txt

# Environment konfigürasyonu / Environment configuration
cp infrastructure/config/env.template .env
# .env dosyasını düzenleyin / Edit .env file
```

### 2. **Konfigürasyon / Configuration**
```bash
# Telegram API anahtarlarını ekleyin / Add Telegram API keys
# config.py dosyasında API_ID ve API_HASH'i ayarlayın
# Set API_ID and API_HASH in config.py

# Veritabanı bağlantılarını yapılandırın / Configure database connections
# Redis, PostgreSQL, MongoDB ayarlarını yapın
```

### 3. **🎯 Yeni Unified System ile Başlatma / New Unified System Startup**

#### **Basit Başlatma / Simple Startup**
```bash
# Varsayılan: Userbot + Flask API
# Default: Userbot + Flask API
python main.py

# Tüm sistemi başlat / Start entire system
python main.py --all

# Debug modu / Debug mode
python main.py --all --debug
```

#### **Bileşen Grupları / Component Groups**
```bash
# Sadece botları başlat / Start bots only
python main.py --bot

# Sadece API'leri başlat / Start APIs only
python main.py --api

# Botlar + API'ler / Bots + APIs
python main.py --bot --api
```

#### **Özel Bileşenler / Individual Components**
```bash
# Telegram userbot sistemi / Telegram userbot system
python main.py --userbot

# Bot yönetim sistemi / Bot management system
python main.py --bot-manager

# Flask API sunucusu / Flask API server
python main.py --flask-api

# XP Token API / XP Token API
python main.py --token-api

# FastAPI SaaS platformu / FastAPI SaaS platform
python main.py --saas-api

# GavatCore Engine
python main.py --engine
```

#### **Sistem Seçenekleri / System Options**
```bash
# Debug logging aktif / Enable debug logging
python main.py --userbot --debug

# Başlık banner'ı gizle / Hide startup banner
python main.py --all --no-banner

# Yardım menüsü / Help menu
python main.py --help
```

### 4. **🔄 Legacy System Desteği / Legacy System Support**

Eski entry point'ler hala çalışıyor ancak **deprecated** durumda:

```bash
# ❌ ESKİ / OLD (Still works but deprecated)
python run.py
python gavatcore_ultimate_run.py
python launchers/gavatcore_ultimate_launcher.py

# ✅ YENİ / NEW (Recommended)
python main.py --flask-api --token-api --userbot
python main.py --all
python main.py --userbot
```

Migration kılavuzu için:
```bash
python legacy_entry_points.py
```

---

## 📚 **DOKÜMANTASYON / DOCUMENTATION**

Daha fazla rehber, mimari doküman ve optimizasyon ipuçları için [docs/README.md](docs/README.md) dosyasına bakın.

**Logging Standardization**: Tüm loglama işlemleri için `infrastructure/config/logger.py` içindeki `get_logger()` fonksiyonunu kullanın.

---

## 🤖 **BOT SİSTEMİ / BOT SYSTEM**

### **Bot Karakterleri / Bot Characters**

#### **🎮 Lara - Flörtöz Yayıncı**
- **Kişilik**: Enerjik, eğlenceli, flörtöz yayıncı kız
- **Tarzı**: Genç, dinamik dil, gaming terimleri
- **Özellik**: Streaming odaklı, trend takipçisi
- **Telefon**: +905382617727

#### **🦁 BabaGavat - Sokak Zekası**
- **Kişilik**: Sokak zekası yüksek, güvenilir abi
- **Tarzı**: Abi tavrı, öğüt verici, bazen ironik
- **Özellik**: Grup lideri, yönlendirici
- **Telefon**: +905513272355

#### **🌸 Geisha - Gizemli Moderatör**
- **Kişilik**: Zarif, gizemli, çekici moderatör
- **Tarzı**: Sofistike, akıllı dil, metaforik
- **Özellik**: Derin konuşmalar, sanatsal yaklaşım
- **Telefon**: +905486306226

### **Bot Yönetimi / Bot Management**

```python
# Bot sistemi import
from services.telegram.bot_manager import bot_system
from services.telegram.bot_manager.bot_config import get_active_bots

# Aktif botları listele / List active bots
active_bots = get_active_bots()

# Tek bot başlat / Start single bot
bot_system.start_bot("lara")

# Tüm botları başlat / Start all bots
bot_system.run_all_bots()

# Bot durumunu kontrol et / Check bot status
status = bot_system.get_bot_status("lara")
```

---

## 🔌 **API ENDPOINTLERİ / API ENDPOINTS**

### **Ana API (Port 5050) / Main API**
```bash
# Sistem durumu / System status
GET /api/system/status

# Bot yönetimi / Bot management
POST /api/bots/start
GET /api/bots/{bot_name}/status
GET /api/bots/list

# Analytics
GET /api/analytics/dashboard
GET /api/analytics/performance
```

### **XP Token API (Port 5051)**
```bash
# Token yönetimi / Token management
GET /api/tokens/balance/{user_id}
POST /api/tokens/spend
POST /api/tokens/transfer

# Sistem / System
GET /health
GET /api/system/status

# İstatistikler / Statistics
GET /api/stats/{user_id}
GET /api/leaderboard
```

### **FastAPI SaaS Platform (Port 8000)**
```bash
# SaaS platformu / SaaS platform
GET /health
GET /docs                    # API documentation
GET /redoc                   # Alternative API docs

# Kullanıcı yönetimi / User management
POST /api/auth/login
POST /api/auth/register
GET /api/users/profile

# Bot servisleri / Bot services
GET /api/bots/status
POST /api/bots/deploy
```

### **Sağlık Kontrolü / Health Checks**
```bash
# Tüm servislerin durumunu kontrol et / Check all services
curl http://localhost:5050/api/system/status
curl http://localhost:5051/health
curl http://localhost:8000/health
```

---

## 🧪 **TEST VE GELİŞTİRME / TESTING & DEVELOPMENT**

### **Test Çalıştırma / Running Tests**
```bash
# Tüm testler / All tests
pytest tests/ -v

# Coverage ile / With coverage
pytest tests/ --cov=. --cov-report=html

# Belirli test kategorileri / Specific test categories
pytest -m unit              # Unit tests
pytest -m integration       # Integration tests
pytest -m api               # API tests
pytest -m slow              # Slow tests

# Bot testleri / Bot tests
pytest tests/test_bot_system.py -v
pytest tests/test_reply_system.py -v
```

### **Code Quality**
```bash
# Code formatting
black .

# Type checking
mypy .

# Linting
flake8 .

# Tüm kalite kontrolleri / All quality checks
pytest && mypy . && black . && flake8 .
```

### **Performans Profiling**
```bash
# Sistem performansı / System performance
python scripts/performance/performance_profiler.py

# Bot performans metrikleri / Bot performance metrics
python -m services.telegram.monitors.bot_monitor
```

---

## 🐳 **DOCKER & DEPLOYMENT**

### **Docker Kullanımı / Docker Usage**
```bash
# Development ortamı / Development environment
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Production ortamı / Production environment
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Telegram bot özel deployment / Telegram bot specific deployment
docker-compose -f docker-compose.telegram.yml up -d
```

### **Kubernetes Deployment**
```bash
# Kubernetes deployment
kubectl apply -f infrastructure/kubernetes/

# Namespace oluştur / Create namespace
kubectl create namespace gavatcore

# Deployment durumunu kontrol et / Check deployment status
kubectl get pods -n gavatcore
```

### **Production Scripts**
```bash
# Production deployment
bash scripts/deploy_production.sh

# Telegram bot deployment
bash scripts/deploy_telegram_bot.sh

# Flutter web build
bash scripts/build_flutter_web.sh
```

---

## 📊 **MONİTORİNG & OBSERVABILITY**

### **Sistem Metrikleri / System Metrics**
- **Uptime Monitoring**: Sürekli çalışma süresi takibi
- **Performance Metrics**: Performans metrikleri
- **Error Tracking**: Hata takip sistemi
- **Resource Usage**: Kaynak kullanım analizi

### **Log Takibi / Log Monitoring**
```bash
# Canlı log takibi / Live log monitoring
tail -f logs/gavatcore_*.log

# Hata logları / Error logs
grep "ERROR" logs/*.log

# Bot aktivite logları / Bot activity logs
tail -f logs/bot_activity.log

# Sistem durumu logları / System status logs
tail -f logs/system_status.log
```

### **Health Endpoints**
```bash
# Sistem sağlığı kontrolü / System health check
curl -X GET http://localhost:5050/api/system/status | jq
curl -X GET http://localhost:5051/health | jq
curl -X GET http://localhost:8000/health | jq
```

---

## 🔒 **GÜVENLİK / SECURITY**

### **Güvenlik Özellikleri / Security Features**
- **API Authentication**: Token-based kimlik doğrulama
- **Rate Limiting**: API çağrı limitleri
- **Secure Sessions**: Şifreli session yönetimi
- **Spam Protection**: Gelişmiş spam koruması
- **Input Validation**: Kapsamlı girdi doğrulaması
- **Data Encryption**: Veri şifreleme

### **Güvenlik Yapılandırması / Security Configuration**
```python
# config.py örneği / config.py example
SECURITY_CONFIG = {
    "api_rate_limit": "100/minute",
    "session_timeout": 3600,
    "token_expiry": 86400,
    "spam_threshold": 10,
    "encryption_enabled": True
}
```

---

## 🌍 **DEPLOYMENT & SCALING**

### **Desteklenen Platformlar / Supported Platforms**
- **AWS ECS**: Container orchestration
- **Google Cloud Run**: Serverless deployment
- **Kubernetes**: Mikro-servis deployment
- **Traditional VPS**: Tek makine deployment
- **Docker Swarm**: Docker cluster management

### **Ölçeklendirme / Scaling**
- **Horizontal Scaling**: Multi-instance bot desteği
- **Database Sharding**: MongoDB/PostgreSQL cluster
- **Load Balancing**: Nginx reverse proxy
- **Caching Strategy**: Redis cluster
- **Auto-scaling**: Kubernetes HPA

### **Environment Configurations**
```bash
# Development
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=debug

# Production
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=info
```

---

## 📚 **DOKÜMANTASYON / DOCUMENTATION**

### **Detaylı Kılavuzlar / Detailed Guides**
- [🔄 **Main.py Migration Guide**](docs/MAIN_PY_MIGRATION.md) - Yeni sisteme geçiş kılavuzu
- [🏗️ **Architecture Overview**](docs/ARCHITECTURE.md) - Sistem mimarisi
- [🤖 **Bot System Guide**](docs/guides/BOT_SYSTEM_GUIDE.md) - Bot sistemi detayları
- [🔌 **API Reference**](docs/api-reference.md) - API dokümantasyonu
- [📱 **Flutter Panel Guide**](docs/guides/FLUTTER_PANEL_GUIDE.md) - Flutter entegrasyonu
- [🚀 **Deployment Guide**](docs/guides/PRODUCTION_DEPLOYMENT_GUIDE.md) - Production deployment

### **Teknik Dokümantasyon / Technical Documentation**
- [📊 **Performance Optimization**](docs/performance/OPTIMIZATION_GUIDE.md)
- [🔒 **Security Guidelines**](docs/security/SECURITY_GUIDE.md)
- [🐳 **Docker Guide**](docs/guides/DOCKER_GUIDE.md)
- [☸️ **Kubernetes Guide**](docs/guides/KUBERNETES_GUIDE.md)

---

## 🤝 **KATKI / CONTRIBUTION**

### **Katkıda Bulunma Süreci / Contribution Process**
1. **Fork** edin projeyi
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** yapın (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** oluşturun

### **Geliştirme Standartları / Development Standards**
- **Code Style**: Black formatter kullanımı
- **Type Hints**: Tam type annotation zorunlu
- **Testing**: %90+ code coverage hedefi
- **Documentation**: Kapsamlı docstring'ler
- **Security**: Güvenlik standartlarına uyum

### **Development Workflow**
```bash
# Geliştirme ortamı kurulumu / Development environment setup
git clone https://github.com/your-username/gavatcore.git
cd gavatcore

# Virtual environment oluştur / Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependencies yükle / Install dependencies
pip install -r infrastructure/config/requirements.txt

# Pre-commit hooks yükle / Install pre-commit hooks
pre-commit install

# Test çalıştır / Run tests
pytest tests/ -v

# Geliştirme sunucusunu başlat / Start development server
python main.py --userbot --debug
```

---

## 📊 **PROJE İSTATİSTİKLERİ / PROJECT STATISTICS**

### **Sistem Metrikleri / System Metrics**
- **🤖 Bot Sayısı**: 3 aktif bot (Lara, BabaGavat, Geisha)
- **🔌 API Endpoint**: 75+ endpoint
- **📊 Test Coverage**: 95%+
- **⚡ Uptime**: 99.9%
- **🔧 Kod Optimizasyonu**: %85 daha az tekrar kod
- **🚀 Startup Time**: <30 saniye (tüm bileşenler)

### **Performans Benchmarks**
- **API Response Time**: <100ms average
- **Bot Response Time**: <2 saniye
- **Memory Usage**: <512MB (tüm sistem)
- **CPU Usage**: <5% idle, <50% peak

### **Kod Kalitesi / Code Quality**
- **Lines of Code**: 50,000+
- **Functions**: 800+
- **Classes**: 150+
- **Modules**: 100+
- **Documentation**: 90%+ covered

---

## 🗺️ **YOL HARİTASI / ROADMAP**

### **Q1 2025**
- [x] ✅ Unified entry point system (`main.py`)
- [x] ✅ Consolidated project structure
- [x] ✅ Character engine improvements
- [ ] 🔄 GraphQL API integration
- [ ] 🔄 Advanced AI chat features
- [ ] 🔄 Real-time dashboard

### **Q2 2025**
- [ ] 📱 Discord bot integration
- [ ] 💬 WhatsApp Business API
- [ ] 🔗 Blockchain integration
- [ ] 🏢 Enterprise features
- [ ] 🌐 Multi-language support

### **Q3 2025**
- [ ] 🎮 Advanced gaming features
- [ ] 📊 Analytics dashboard v2
- [ ] 🤖 AI model training
- [ ] 🔐 Advanced security features
- [ ] ☸️ Kubernetes native deployment

### **Q4 2025**
- [ ] 🌍 Global scaling
- [ ] 📈 Business intelligence
- [ ] 🎯 Marketing automation
- [ ] 🔬 Research & development
- [ ] 🏆 Community features

---

## 🆘 **TROUBLESHOOTING**

### **Sık Karşılaşılan Sorunlar / Common Issues**

#### **🔧 Sistem Başlatma / System Startup**
```bash
# Bileşen başlatılamıyor / Component won't start
python main.py --debug --userbot

# Port kullanımda / Port in use
lsof -i :5050  # Check port usage
kill -9 <PID>  # Kill process

# Dependency eksik / Missing dependencies
pip install -r infrastructure/config/requirements.txt
```

#### **🤖 Bot Sorunları / Bot Issues**
```bash
# Session geçersiz / Invalid session
# Session dosyalarını kontrol et / Check session files
ls -la sessions/

# Telegram API problemi / Telegram API issue
# API anahtarlarını kontrol et / Check API keys
python -c "from config import TELEGRAM_API_ID, TELEGRAM_API_HASH; print(f'API_ID: {TELEGRAM_API_ID}, API_HASH: {TELEGRAM_API_HASH[:10]}...')"
```

#### **🔌 API Sorunları / API Issues**
```bash
# API yanıt vermiyor / API not responding
curl -X GET http://localhost:5050/api/system/status

# Database bağlantı hatası / Database connection error
# Database servislerini kontrol et / Check database services
systemctl status redis
systemctl status postgresql
```

### **Debug Komutları / Debug Commands**
```bash
# Sistem durumu kontrolü / System status check
python main.py --all --debug

# Log analizi / Log analysis
tail -f logs/*.log | grep ERROR

# Performans profiling
python -m cProfile -o profile.stats main.py --userbot
```

---

## 📞 **DESTEK & İLETİŞİM / SUPPORT & CONTACT**

### **Teknik Destek / Technical Support**
- 📧 **Email**: dev@siyahkare.com
- 💬 **Discord**: [GavatCore Community](https://discord.gg/gavatcore)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/username/gavatcore/issues)
- 📖 **Documentation**: [GitBook](https://gavatcore.gitbook.io)

### **Topluluk / Community**
- 🌐 **Website**: [gavatcore.com](https://gavatcore.com)
- 🐦 **Twitter**: [@gavatcore](https://twitter.com/gavatcore)
- 📺 **YouTube**: [GavatCore Channel](https://youtube.com/gavatcore)
- 📱 **Telegram**: [@gavatcore_updates](https://t.me/gavatcore_updates)

### **Ticari Lisans / Commercial License**
Kurumsal kullanım için özel lisans seçenekleri mevcuttur.
Custom enterprise licenses available for commercial use.

📧 **Contact**: enterprise@siyahkare.com

---

## 📄 **LİSANS / LICENSE**

MIT License - Detaylar için [LICENSE](LICENSE) dosyasını inceleyin.

MIT License - See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 **GELİŞTİRİCİLER / DEVELOPERS**

**SiyahKare Development Team**
- 🌐 **Website**: [siyahkare.com](https://siyahkare.com)
- 📧 **Email**: dev@siyahkare.com
- 🐦 **Twitter**: [@siyahkare_dev](https://twitter.com/siyahkare_dev)
- 🔗 **LinkedIn**: [SiyahKare](https://linkedin.com/company/siyahkare)

---

## 🎯 **ÖZET / SUMMARY**

**GAVATCore**, modern AI teknolojileri ile güçlendirilmiş, enterprise-grade Telegram bot yönetim platformudur. Yeni **unified entry point** sistemi ile tüm bileşenler tek `main.py` dosyası üzerinden yönetilir.

**GAVATCore** is an enterprise-grade Telegram bot management platform powered by modern AI technologies. With the new **unified entry point** system, all components are managed through a single `main.py` file.

### **Ana Özellikler / Key Features:**
- 🎯 **Tek Giriş Noktası**: Unified `main.py` entry point
- 🤖 **3 AI Bot**: Lara, BabaGavat, Geisha
- 🔌 **Multi-Port API**: 3 farklı API servisi
- 🧠 **Character Engine**: AI-powered personalities
- 🎮 **Token Economy**: XP/Coin sistemi
- 🔒 **Enterprise Security**: Güvenlik odaklı tasarım
- 📊 **Real-time Analytics**: Canlı izleme
- 🐳 **Docker Ready**: Kolay deployment

---

**Made with 💙 by [SiyahKare](https://siyahkare.com)**

**⭐ Star us on GitHub! | 🍴 Fork & Contribute | 📢 Share with Community**

---

*Son güncelleme / Last updated: 2025-07-18*
