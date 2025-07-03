# 🚀 GAVATCORE FLUTTER ADMIN PANEL

## 📱 Tam Fonksiyonel Admin Panel

GavatCore için geliştirilmiş, **responsive** ve **real-time** Flutter web/mobile admin paneli.

## ✨ Özellikler

### 1. 🎭 **Karakter Yönetimi**
- Tüm karakterleri listele (Lara, BabaGavat, Geisha, Balkız)
- Reply mode değiştir (manual/gpt/hybrid/manualplus)
- Ton ayarları (flirty/soft/dark/mystic/aggressive/dominant/sadık)
- System prompt düzenleme
- GPT model seçimi
- Humanizer ayarları
- **Canlı test paneli** - Anında yanıt testi

### 2. 🧠 **Behavioral Tracker**
- Kullanıcı davranış analizi
- Trust Index ve VIP olasılık göstergeleri
- Duygusal profil grafikleri
- Manipülasyon direnci
- Sessizlik eşiği
- AI strateji önerileri
- Manuel kullanıcı ID ile arama

### 3. 📊 **Ana Dashboard**
- Sistem durumu (healthy/degraded/critical)
- Bot performans kartları
- Gerçek zamanlı istatistikler
- Kampanya durumu
- Otomatik yenileme (30s default)

### 4. 🎓 **Showcu Onboarding**
- 5 adımlı wizard
- Showcu bilgileri (isim, IBAN)
- Karakter seçimi ve özelleştirme
- Davranış ayarları
- Otomatik kayıt

### 5. ⚙️ **Sistem Ayarları**
- API URL konfigürasyonu
- Dark/Light mode
- Otomatik yenileme ayarları
- Bot başlat/durdur kontrolleri
- Sistem sağlık durumu
- Versiyon bilgileri

## 🛠️ Kurulum

### 1. Gereksinimler
```bash
# Flutter SDK (3.0+)
flutter --version

# Dart SDK
dart --version
```

### 2. Bağımlılıkları Yükle
```bash
cd gavatcore_mobile
flutter pub get
```

### 3. Backend API'yi Başlat

#### Option A: Production API
```bash
python production_bot_api.py
# http://localhost:8000
```

#### Option B: Flutter Test API
```bash
python api/flutter_endpoints.py
# http://localhost:8001
```

### 4. Flutter Panel'i Başlat

#### Web için:
```bash
flutter run -d chrome --web-port=3000
```

#### Mobile için:
```bash
# iOS
flutter run -d iphone

# Android
flutter run -d android
```

## 🔧 Konfigürasyon

### API URL Değiştirme
1. Ayarlar sekmesine git
2. API URL alanına yeni URL gir
3. Kaydet butonuna tıkla

### Varsayılan API Endpoints
```dart
// lib/core/services/api_service.dart
baseUrl: 'http://localhost:8000'
```

## 📱 Kullanım

### Karakter Test Etme
1. Karakterler sekmesine git
2. Test etmek istediğin karakteri seç
3. Test sekmesine geç
4. Mesaj yaz ve "Test Et" butonuna tıkla
5. Yanıt anında görüntülenir

### Behavioral Analiz
1. Behavioral sekmesine git
2. Kullanıcı ID gir veya listeden seç
3. Detaylı analizi incele
4. AI önerilerini uygula

### Bot Kontrolü
1. Ayarlar sekmesine git
2. Bot Kontrolü bölümüne in
3. Başlat/Durdur butonlarını kullan

## 🎨 Tema Özelleştirme

### Dark Mode
```dart
// Ayarlar > Görünüm Ayarları > Dark Mode
```

### Renk Şeması
```dart
// lib/shared/themes/app_colors.dart
primary: Color(0xFF6366F1)    // Indigo
success: Color(0xFF10B981)    // Green
warning: Color(0xFFF59E0B)    // Amber
error: Color(0xFFEF4444)      // Red
```

## 🚀 Production Build

### Web Build
```bash
flutter build web --release

# Output: build/web/
# Deploy to: Vercel, Netlify, Firebase Hosting
```

### Mobile Build
```bash
# Android APK
flutter build apk --release

# iOS
flutter build ios --release
```

## 📊 Performans

- **Initial Load**: < 2s
- **API Response**: < 500ms
- **Auto Refresh**: 30s (ayarlanabilir)
- **Memory Usage**: < 100MB

## 🐛 Troubleshooting

### CORS Hatası
```python
# Backend'de CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused
1. Backend API'nin çalıştığını kontrol et
2. Doğru port kullanıldığını kontrol et
3. Firewall ayarlarını kontrol et

### State Management
- Riverpod kullanılıyor
- Provider'lar `ref.invalidate()` ile yenilenir

## 🔒 Güvenlik

- JWT token authentication ready
- Secure storage for credentials
- API key management
- Role-based access control ready

## 📱 Responsive Design

### Breakpoints
- Mobile: < 600px
- Tablet: 600px - 1200px
- Desktop: > 1200px

### Navigation
- Desktop: NavigationRail (sidebar)
- Mobile: NavigationBar (bottom)

## 🎯 Roadmap

- [ ] Real-time WebSocket updates
- [ ] Push notifications
- [ ] Multi-language support
- [ ] Export reports (PDF/Excel)
- [ ] Advanced analytics dashboard
- [ ] Voice command integration

## 📞 Destek

- GitHub Issues: `github.com/gavatcore/issues`
- Discord: `discord.gg/gavatcore`
- Email: `support@gavatcore.com`

---

**🎉 GavatCore Flutter Admin Panel v1.0**
*Where bots become human, where code meets emotion* 