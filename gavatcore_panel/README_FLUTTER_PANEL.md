# 🚀 GavatCore Management Panel

Modern, neon glassmorphic tasarımlı Flutter web uygulaması. GavatCore sistemini yönetmek için geliştirilmiş kapsamlı yönetim paneli.

## ✨ Özellikler

### 🎨 Modern UI/UX
- **Neon Glassmorphic Design**: Cam efektli, parlayan neon renkler
- **Dark Theme**: Göz dostu karanlık tema
- **Smooth Animations**: Flutter Animate ile akıcı animasyonlar
- **Responsive Design**: Mobil ve masaüstü uyumlu

### 🛠️ Teknik Özellikler
- **Flutter 3.1+**: Modern Flutter framework
- **Riverpod State Management**: Tip güvenli state yönetimi
- **Freezed Models**: Immutable data classes
- **Retrofit API**: Type-safe HTTP client
- **WebSocket Support**: Real-time updates

### 📱 Ekranlar

#### 1. 📊 Dashboard
- Real-time istatistikler
- Interactive charts (Line & Pie)
- System status göstergeleri
- Son aktivite feed'i
- Quick action buttons

#### 2. 💬 Message Pools
- Mesaj CRUD operasyonları
- AI enhancement badges
- Search ve filtering
- Modal dialogs
- Message status tracking

#### 3. ⏰ Scheduler Config
- Cron job yönetimi
- Zamanlama konfigürasyonu

#### 4. 🧠 AI Prompt Blending
- AI prompt yönetimi
- Enhancement types

#### 5. 📋 Logs & Stats
- System logs görüntüleme
- İstatistik analizi

#### 6. 💳 Account & Billing
- Hesap yönetimi
- Fatura ve ödeme

#### 7. ⚙️ Admin Override Panel
- System yönetimi
- Bot kontrolü

#### 8. 🚨 Fail-Safe Reset
- Emergency controls
- System reset

## 🚀 Kurulum

### Gereksinimler
- Flutter 3.1+
- Dart 3.0+
- VS Code / Android Studio

### 1. Proje Klonlama
```bash
git clone <repository-url>
cd gavatcore_panel
```

### 2. Dependencies Kurulum
```bash
flutter pub get
```

### 3. Code Generation
```bash
# Build runner ile model ve provider'ları generate et
dart run build_runner build --delete-conflicting-outputs

# Veya otomatik watch için
dart run build_runner watch
```

### 4. Web için Çalıştırma
```bash
flutter run -d chrome
```

## 📁 Proje Yapısı

```
lib/
├── app.dart                    # Ana uygulama
├── main.dart                   # Entry point
├── core/                       # Core fonksiyonalite
│   ├── models/                 # Data models
│   │   └── app_state.dart      # Freezed models
│   ├── providers/              # Riverpod providers
│   │   └── app_providers.dart  # State management
│   ├── services/               # API & WebSocket
│   │   ├── api_service.dart    # Retrofit API client
│   │   └── websocket_service.dart
│   ├── theme/                  # Theme & styling
│   │   └── app_theme.dart      # Neon glassmorphic theme
│   └── widgets/                # Reusable widgets
│       └── glass_container.dart # Glassmorphic containers
└── features/                   # Feature modules
    ├── dashboard/              # Dashboard feature
    │   ├── presentation/
    │   │   ├── dashboard_screen.dart
    │   │   └── main_layout.dart
    │   └── providers/
    │       └── dashboard_providers.dart
    ├── message_pools/          # Message management
    ├── scheduler/              # Scheduler config
    ├── ai_prompts/            # AI prompt management
    ├── logs/                  # Logs & stats
    ├── billing/               # Account & billing
    ├── admin/                 # Admin panel
    └── failsafe/              # Fail-safe controls
```

## 🎨 Design System

### Neon Colors
- **Purple**: `#9C27B0` (Primary)
- **Blue**: `#2196F3`
- **Green**: `#4CAF50`
- **Orange**: `#FF9800`
- **Red**: `#F44336`
- **Yellow**: `#FFEB3B`
- **Pink**: `#E91E63`
- **Cyan**: `#00BCD4`

### Glassmorphic Components
- `GlassContainer`: Basic glass effect
- `NeonGlassContainer`: Glass + neon border
- `AnimatedGlassContainer`: Interactive glass

### Typography
- Inter font family
- Neon glow text effects
- Responsive font sizes

## 🔌 API Integration

### Retrofit Service
```dart
@RestApi(baseUrl: "http://localhost:8000/api/")
abstract class ApiService {
  @GET("/dashboard/stats")
  Future<DashboardStats> getDashboardStats();
  
  @POST("/messages")
  Future<MessageData> createMessage(@Body() Map<String, dynamic> message);
}
```

### WebSocket Service
```dart
final webSocketService = ref.read(webSocketServiceProvider);
await webSocketService.connect();
webSocketService.subscribeToChannel('dashboard');
```

## 📊 State Management

### Riverpod Providers
```dart
// Dashboard stats
@riverpod
Future<DashboardStats> dashboardStats(DashboardStatsRef ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getDashboardStats();
}

// App state
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppStateData>(
  (ref) => AppStateNotifier(),
);
```

### Freezed Models
```dart
@freezed
class DashboardStats with _$DashboardStats {
  const factory DashboardStats({
    @Default(0) int totalMessages,
    @Default(0) int activeBots,
    @Default([]) List<ChartData> messageChart,
  }) = _DashboardStats;
}
```

## 🧪 Development

### Hot Reload
```bash
# Flutter web hot reload
flutter run -d chrome --hot

# Code generation watch
dart run build_runner watch
```

### Mock Data
Development sırasında mock data kullanılıyor:
- Dashboard stats
- Message lists
- User accounts
- System logs

Production'da gerçek API endpoint'leri kullanılacak.

### Build Script
```bash
# Otomatik code generation
./build_runner.sh
```

## 🌐 Web Deployment

### Build
```bash
flutter build web --release
```

### Deploy
```bash
# GitHub Pages, Firebase, Vercel, vb.
firebase deploy --only hosting
```

## 🔧 Configuration

### Environment Variables
```dart
// config/environments/
const String API_BASE_URL = 'http://localhost:8000';
const String WS_URL = 'ws://localhost:8000/ws';
```

### Theme Customization
```dart
// core/theme/app_theme.dart
class AppTheme {
  static const neonColors = NeonColors(
    purple: Color(0xFF9C27B0),
    blue: Color(0xFF2196F3),
    // ...
  );
}
```

## 📱 Mobile Support

Panel mobil cihazlarda da çalışacak şekilde tasarlanmış:
- Responsive layout
- Touch-friendly interactions
- Mobile navigation

## 🐛 Troubleshooting

### Common Issues

1. **Build Runner Errors**
```bash
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs
```

2. **WebSocket Connection**
```dart
// Check WebSocket URL
const wsUrl = 'ws://localhost:8000/ws';
```

3. **API Connection**
```dart
// Verify API endpoint
const apiUrl = 'http://localhost:8000/api';
```

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **GavatCore Team** - *Initial work*

## 🙏 Acknowledgments

- Flutter team for amazing framework
- Riverpod for state management
- Community packages used in project

---

**GavatCore Management Panel** - Modern web yönetim paneli 🚀 