# 🚀 GAVATCore - Enterprise-Grade AI & Bot Management Platform

Modern, AI-destekli Telegram bot yönetimi ve sosyal gaming platformu. Mikroservis mimarisi ile geliştirilmiş, ölçeklenebilir altyapı.

![GAVATCore Banner](assets/images/banner.png)

## 📁 Proje Yapısı

```
gavatcore/
├── 🔌 apis/                    # Tüm API Servisleri
│   ├── production_bot_api.py   # Ana bot API (Port 5050)
│   ├── xp_token_api_sync.py    # Token ekonomi API (Port 5051)
│   └── ...                     # Diğer API'ler
│
├── 🤖 services/                # Platform Servisleri
│   ├── telegram/               # Telegram Bot Servisleri
│   │   ├── bot_manager/        # Bot yönetim sistemi
│   │   │   ├── bot_system.py   # Ana bot kontrolcüsü
│   │   │   ├── spam_aware_system.py # Spam korumalı sistem
│   │   │   └── bot_config.py   # Bot konfigürasyonları
│   │   ├── monitors/           # Bot monitoring
│   │   └── handlers/           # Mesaj handler'ları
│   ├── discord/                # Discord entegrasyonu (gelecek)
│   └── whatsapp/               # WhatsApp Business API (gelecek)
│
├── 📊 modules/                 # Core Business Modülleri
│   ├── auth/                   # Kimlik doğrulama
│   ├── analytics/              # Analitik & monitoring
│   └── payments/               # Ödeme işlemleri
│
├── 🏗️ infrastructure/          # DevOps & Infrastructure
│   ├── docker/                 # Docker konfigürasyonları
│   ├── kubernetes/             # K8s manifests
│   └── terraform/              # Infrastructure as Code
│
├── 📱 gavatcore_panel/         # Unified Admin Panel
│   ├── lib/                    # Flutter uygulaması
│   ├── web/                    # Web konfigürasyonları
│   └── assets/                 # Statik kaynaklar
│
├── ⚙️ config/                  # Konfigürasyon
│   ├── environments/           # Environment dosyaları
│   └── requirements.txt        # Python bağımlılıkları
│
├── 🚀 launchers/               # Sistem Başlatıcıları
├── 📊 scripts/                 # Otomation Scripts
├── 🧪 tests/                   # Test Dosyaları
├── 📈 reports/                 # Raporlar
├── 📚 docs/                    # Dokümantasyon
├── 🔧 utilities/               # Yardımcı Araçlar
└── 📦 data/                    # Veri & Storage
    ├── databases/              # SQLite veritabanları
    ├── personas/               # Bot kişilikleri
    └── templates/              # Mesaj şablonları
```

## ✨ Özellikler

### 🤖 Gelişmiş Bot Yönetimi
- **Unified Bot System**: Tüm botlar tek merkezden yönetim
- **3 Ana Bot**: Lara, BabaGavat, Geisha
- **Spam-Aware Teknoloji**: Akıllı spam koruması
- **Auto-Contact Management**: Otomatik contact ekleme
- **GPT-4 Entegrasyonu**: AI-powered sohbet

### 🔌 API Altyapısı
- **RESTful API**: Flask/FastAPI hibrit mimari
- **XP Token Economy**: Blockchain-inspired token sistemi
- **Real-time Monitoring**: Live sistem durumu takibi
- **Health Checks**: Otomatik servis sağlık kontrolü

### 📊 Analytics & Monitoring
- **Performance Dashboard**: Real-time performans metrikleri
- **Bot Activity Tracking**: Bot aktivite takibi
- **Advanced Caching**: Redis-based cache optimizasyonu
- **Structured Logging**: Production-ready log management

### 🎮 Social Gaming
- **GavatCoin Economy**: Dijital token sistemi
- **XP System**: Kullanıcı deneyim puanlama
- **Gamification**: Oyunlaştırma mekanizmaları
- **Leaderboards**: Sıralama sistemleri

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
# Repository'yi klonlayın
git clone https://github.com/username/gavatcore.git
cd gavatcore

# Bağımlılıkları yükleyin
pip install -r config/requirements.txt

# Environment konfigürasyonu
cp config/env.template .env
# .env dosyasını düzenleyin
```

### 2. Konfigürasyon
```bash
# Telegram API anahtarlarını config/environments/ klasörüne ekleyin
# Database bağlantı ayarlarını yapın
# Redis ve MongoDB servislerini başlatın
```

### 3. Sistem Başlatma

#### Basit Başlatma (API'ler + 1 Bot)
```bash
# Ana sistem başlatma (API'ler + Lara bot)
python run.py
```

#### Tüm Botları Başlatma
```bash
# Master bot automation ile 3 bot birden
python -m services.telegram.bot_manager.bot_system

# Ya da eski launcher (hala çalışır)
python launchers/gavatcore_ultimate_launcher.py
```

#### Production Deployment
```bash
# Full production deployment
bash scripts/deployment/deploy_production.sh
```

## 🤖 Bot Sistemi

### Bot Konfigürasyonları
```python
# services/telegram/bot_manager/bot_config.py

BOT_CONFIGS = {
    "lara": {
        "display_name": "Lara - Flörtöz Yayıncı",
        "phone": "+905382617727",
        "personality": "Enerjik, eğlenceli, flörtöz yayıncı kız"
    },
    "babagavat": {
        "display_name": "BabaGavat - Pavyon Lideri",
        "phone": "+905513272355",
        "personality": "Sokak zekası yüksek, güvenilir abi"
    },
    "geisha": {
        "display_name": "Geisha - Vamp Moderatör",
        "phone": "+905486306226",
        "personality": "Zarif, gizemli, çekici moderatör"
    }
}
```

### Bot Yönetimi
```python
# Bot sistemi import
from services.telegram.bot_manager import bot_system
from services.telegram.bot_manager.bot_config import get_active_bots

# Aktif botları listele
active_bots = get_active_bots()

# Tek bot başlat
bot_system.start_bot("lara")

# Tüm botları başlat
bot_system.run_all_bots()

# Bot durumunu kontrol et
status = bot_system.get_bot_status("lara")
```

## 🔧 Geliştirme

### Test Çalıştırma
```bash
# Tüm testler
pytest tests/ -v

# Coverage ile
pytest tests/ --cov=. --cov-report=html

# Bot testleri
pytest tests/test_bot_system.py -v
```

### Performans Profiling
```bash
# Sistem performansı analizi
python scripts/performance/performance_profiler.py

# Bot performans metrikleri
python -m services.telegram.monitors.bot_monitor
```

### Linting & Formatting
```bash
# Code formatting
black .

# Type checking
mypy . --config-file config/mypy.ini

# Linting
flake8 .
```

## 📊 API Endpoints

### Ana API (Port 5050)
- `GET /api/system/status` - Sistem durumu
- `POST /api/bots/start` - Bot başlatma
- `GET /api/bots/{bot_name}/status` - Bot durumu
- `GET /api/analytics/dashboard` - Analytics data

### XP Token API (Port 5051)
- `GET /api/tokens/balance/{user_id}` - Token bakiyesi
- `POST /api/tokens/spend` - Token harcama
- `GET /api/leaderboard` - Sıralama listesi

### Bot Monitoring API (Port 5005)
- `GET /api/bots/status` - Tüm bot durumları
- `GET /api/bots/{bot_name}/messages` - Bot mesajları
- `GET /api/system/health` - Sistem sağlığı

## 🐳 Docker Deployment

```bash
# Development
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Production
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

## 📈 Monitoring & Observability

### Metrics
- **System Health**: `/health` endpoint'leri
- **Bot Metrics**: Bot aktivite metrikleri
- **Performance Metrics**: Prometheus/Grafana entegrasyonu
- **Error Tracking**: Structured logging ile hata takibi

### Logs
```bash
# Live log takibi
tail -f logs/gavatcore_bot_*.log

# Error logs
grep "ERROR" logs/*.log

# Bot aktivite logları
tail -f logs/bot_activity.log
```

## 🔒 Güvenlik

- **API Authentication**: Token-based kimlik doğrulama
- **Rate Limiting**: API çağrı limitleri
- **Secure Sessions**: Şifreli session yönetimi
- **Spam Protection**: Gelişmiş spam koruması
- **Input Validation**: Comprehensive girdi doğrulaması

## 🌍 Üretim Ortamı

### Desteklenen Platformlar
- **AWS ECS**: Container orchestration
- **Kubernetes**: Mikro-servis deployment
- **Traditional VPS**: Tek makine deployment

### Ölçeklendirme
- **Horizontal Scaling**: Multi-instance bot desteği
- **Database Sharding**: MongoDB cluster desteği
- **Load Balancing**: Nginx reverse proxy
- **Caching Strategy**: Redis cluster

## 📚 Dokümantasyon

Detaylı dokümantasyon için:
- [Bot Sistemi Dokümantasyonu](docs/guides/BOT_SYSTEM_GUIDE.md)
- [API Referansı](docs/api-reference.md)
- [Flutter Panel Entegrasyonu](docs/guides/FLUTTER_PANEL_GUIDE.md)
- [Deployment Guide](docs/guides/PRODUCTION_DEPLOYMENT_GUIDE.md)

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### Geliştirme Standartları
- **Code Style**: Black formatter
- **Type Hints**: Full type annotation
- **Testing**: 90%+ code coverage
- **Documentation**: Comprehensive docstrings

## 📊 İstatistikler

- **Bot Sayısı**: 3 aktif bot (Lara, BabaGavat, Geisha)
- **API Endpoint**: 50+ endpoint
- **Test Coverage**: 95%+
- **Uptime**: 99.9%
- **Kod Optimizasyonu**: %80 daha az tekrar kod

## 🗺️ Yol Haritası

### Q1 2025
- [x] Unified bot management system
- [x] Enterprise-grade klasör yapısı
- [ ] GraphQL API entegrasyonu
- [ ] Advanced AI chat features

### Q2 2025
- [ ] Discord bot entegrasyonu
- [ ] WhatsApp Business API
- [ ] Blockchain integration
- [ ] Enterprise features

## 📄 Lisans

MIT License - bkz. [LICENSE](LICENSE)

## 👨‍💻 Geliştirici

**SiyahKare Development Team**
- 🌐 Website: [siyahkare.com](https://siyahkare.com)
- 📧 Email: dev@siyahkare.com
- 🐦 Twitter: [@siyahkare_dev](https://twitter.com/siyahkare_dev)

---

Made with 💙 by [SiyahKare](https://siyahkare.com) | ⭐ Star us on GitHub! 