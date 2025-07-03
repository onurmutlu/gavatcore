# GAVATCore Unified Panel

## 🚀 Genel Bakış

GAVATCore Unified Panel, hem mobil uygulama hem de Telegram Mini App olarak çalışabilen enterprise-grade yönetim panelidir.

### ✨ Özellikler

- **📱 Çoklu Platform**: iOS, Android, Web, Telegram Mini App
- **🎨 Modern UI/UX**: Material 3, Dark Theme, Responsive Design
- **🔐 Güvenli**: Telegram OAuth, JWT Token, Şifreli İletişim
- **📊 Gerçek Zamanlı**: WebSocket, Push Notifications
- **🌐 Çok Dilli**: Türkçe, İngilizce

### 🏗️ Mimari

```
gavatcore_panel/
├── lib/
│   ├── core/              # Çekirdek modüller
│   │   ├── models/        # Data modelleri
│   │   ├── providers/     # Riverpod providers
│   │   ├── repositories/  # Data repositories
│   │   ├── services/      # API servisleri
│   │   │   ├── api_service.dart
│   │   │   ├── telegram_service.dart
│   │   │   └── websocket_service.dart
│   │   ├── storage/       # Local storage
│   │   └── utils/         # Utility fonksiyonları
│   │
│   ├── features/          # Özellik modülleri
│   │   ├── auth/          # Kimlik doğrulama
│   │   ├── dashboard/     # Ana panel
│   │   ├── bots/          # Bot yönetimi
│   │   ├── admin/         # Admin özellikleri
│   │   ├── analytics/     # Analitik
│   │   ├── settings/      # Ayarlar
│   │   └── performer/     # Performer yönetimi
│   │
│   ├── shared/            # Paylaşılan bileşenler
│   │   ├── themes/        # Tema tanımları
│   │   └── widgets/       # Ortak widgetlar
│   │
│   └── main.dart          # Uygulama giriş noktası
│
├── assets/                # Statik dosyalar
│   ├── images/
│   ├── icons/
│   ├── animations/
│   ├── fonts/
│   ├── tokens/
│   ├── nfts/
│   └── sounds/
│
├── web/                   # Web konfigürasyonu
└── test/                  # Test dosyaları
```

## 🚀 Kurulum

### Gereksinimler
- Flutter SDK 3.0+
- Dart SDK 3.0+
- Android Studio / VS Code
- Xcode (iOS için)

### Adımlar

1. **Bağımlılıkları yükleyin**
```bash
flutter pub get
```

2. **Code generation çalıştırın**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

3. **Uygulamayı çalıştırın**
```bash
# Web
flutter run -d chrome

# iOS
flutter run -d ios

# Android
flutter run -d android
```

## 📱 Telegram Mini App Olarak Çalıştırma

1. **Web build oluşturun**
```bash
flutter build web --release --web-renderer html
```

2. **Telegram Bot ayarları**
- BotFather'da Mini App URL'ini ayarlayın
- Menu butonunu konfigüre edin

## 🔧 Konfigürasyon

### API Endpoints
`lib/core/services/api_service.dart` dosyasında:
```dart
static const String baseUrl = 'https://api.gavatcore.com';
```

### Telegram Config
`lib/core/services/telegram_service.dart` dosyasında:
```dart
static const String botToken = 'YOUR_BOT_TOKEN';
```

## 🧪 Test

```bash
# Unit testler
flutter test

# Integration testler
flutter test integration_test
```

## 📦 Deployment

### Web Deployment
```bash
flutter build web --release
# build/web klasörünü sunucuya yükleyin
```

### Mobile Deployment
```bash
# Android
flutter build apk --release
flutter build appbundle --release

# iOS
flutter build ios --release
```

## 🛠️ Geliştirme

### State Management
Riverpod kullanıyoruz. Örnek provider:
```dart
@riverpod
class BotList extends _$BotList {
  @override
  Future<List<Bot>> build() async {
    final api = ref.watch(apiServiceProvider);
    return api.getBots();
  }
}
```

### API Integration
Dio + Retrofit kullanıyoruz:
```dart
@RestApi(baseUrl: "https://api.gavatcore.com")
abstract class ApiClient {
  @GET("/bots")
  Future<List<Bot>> getBots();
}
```

## 📊 Performans

- **Başlangıç Süresi**: < 2 saniye
- **API Yanıt**: < 200ms
- **Frame Rate**: 60 FPS
- **Bundle Size**: ~15MB (Android), ~20MB (iOS)

## 🔒 Güvenlik

- HTTPS zorunlu
- JWT token authentication
- Telegram OAuth integration
- Rate limiting
- Input validation

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📄 Lisans

Bu proje özel lisanslıdır. Tüm hakları GAVATCore'a aittir. 