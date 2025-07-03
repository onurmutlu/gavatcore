import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:universal_html/html.dart' as html;
import 'package:google_fonts/google_fonts.dart';
import 'core/services/telegram_init_service.dart';
import 'core/storage/storage_service.dart';
import 'shared/themes/app_colors.dart';
import 'features/auth/login_screen.dart';
import 'features/dashboard/main_dashboard_screen.dart';
import 'features/onboarding/showcu_onboarding_screen.dart';

import 'core/storage/storage_service.dart';
import 'shared/themes/app_theme.dart';
import 'features/dashboard/presentation/pages/dashboard_page.dart';
import 'features/dashboard/presentation/pages/token_dashboard_page.dart';
import 'features/bots/presentation/pages/bot_management_page.dart';
import 'features/auth/admin_login_screen.dart';
import 'core/providers/auth_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize StorageService
  await StorageService.init();
  
  // Shared Preferences başlat
  final prefs = await SharedPreferences.getInstance();
  
  // Telegram WebApp kontrolü
  String? initDataString;
  try {
    final uri = Uri.parse(html.window.location.href);
    initDataString = uri.queryParameters['tgWebAppData'];
  } catch (e) {
    print('Error parsing URL: $e');
  }
  
  bool isTelegramWebApp = false;
  if (initDataString != null && initDataString.isNotEmpty) {
    try {
      final initData = await TelegramInitService.decodeAndVerifyInitData(initDataString);
      isTelegramWebApp = true;
      print('Telegram Web App Init Data: $initData');
      await prefs.setString('user_data', initData['user'].toString());
    } catch (e) {
      print('Error verifying Telegram init data: $e');
    }
  }
  
  runApp(const ProviderScope(child: GavatCoreApp()));
}

class GavatCoreApp extends StatelessWidget {
  const GavatCoreApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GavatCore Admin Panel',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          brightness: Brightness.dark,
        ),
        cardTheme: CardTheme(
          color: AppColors.surface,
          elevation: 2,
          margin: const EdgeInsets.all(8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.surface,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: AppColors.border),
          ),
        ),
      ),
      home: const MainDashboardScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AuthCheckScreen extends ConsumerWidget {
  const AuthCheckScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return FutureBuilder<bool>(
      future: _checkAuth(ref),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
        
        if (snapshot.data == true) {
          // Check if onboarding is completed
          return FutureBuilder<bool>(
            future: _checkOnboarding(ref),
            builder: (context, onboardingSnapshot) {
              if (onboardingSnapshot.connectionState == ConnectionState.waiting) {
                return const Scaffold(
                  body: Center(
                    child: CircularProgressIndicator(),
                  ),
                );
              }
              
              if (onboardingSnapshot.data == true) {
                // Go to dashboard
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  Navigator.pushReplacementNamed(context, '/dashboard');
                });
              } else {
                // Go to onboarding
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  Navigator.pushReplacementNamed(context, '/onboarding');
                });
              }
              
              return const Scaffold(
                body: Center(
                  child: CircularProgressIndicator(),
                ),
              );
            },
          );
        } else {
          // Go to login
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacementNamed(context, '/login');
          });
          
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
      },
    );
  }
  
  Future<bool> _checkAuth(WidgetRef ref) async {
    final storage = ref.read(storageServiceProvider);
    final token = await storage.getString('auth_token');
    return token != null;
  }
  
  Future<bool> _checkOnboarding(WidgetRef ref) async {
    final storage = ref.read(storageServiceProvider);
    final completed = await storage.getBool('onboarding_completed') ?? false;
    return completed;
  }
}

class AdminWrapper extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return authState.when(
      data: (user) => user != null ? DashboardPage() : AdminLoginScreen(),
      loading: () => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(color: AppTheme.primaryColor),
              SizedBox(height: 16),
              Text('GavatCore yükleniyor...'),
            ],
          ),
        ),
      ),
      error: (error, stack) => Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, color: AppTheme.errorColor, size: 64),
              SizedBox(height: 16),
              Text('Sistem başlatılamadı'),
              Text('$error'),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.refresh(authProvider),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                ),
                child: Text('Tekrar Dene'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoading = true;
  bool _isAuthenticated = false;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    try {
      final storage = StorageService.instance;
      final token = await storage.getString('auth_token');
      final isAuthenticated = token != null && token.isNotEmpty;
      setState(() {
        _isAuthenticated = isAuthenticated;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isAuthenticated = false;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.darkBg,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.admin_panel_settings,
                size: 64,
                color: AppTheme.primaryColor,
              ),
              SizedBox(height: 16),
              Text(
                'GavatCore Admin',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColor,
                ),
              ),
              SizedBox(height: 24),
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
              ),
            ],
          ),
        ),
      );
    }

    return _isAuthenticated
        ? const DashboardPage()
        : const AdminLoginScreen();
  }
}

class MainNavigationPage extends StatefulWidget {
  const MainNavigationPage({super.key});

  @override
  State<MainNavigationPage> createState() => _MainNavigationPageState();
}

class _MainNavigationPageState extends State<MainNavigationPage> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
    const TokenDashboardPage(),
    const BotManagementPage(),
    const DashboardPage(),
    AdminDashboardScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Row(
        children: [
          NavigationRail(
            backgroundColor: AppTheme.cardBg,
            indicatorColor: AppTheme.primaryColor.withOpacity(0.2),
            selectedIndex: _selectedIndex,
            onDestinationSelected: (int index) {
              setState(() {
                _selectedIndex = index;
              });
            },
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.token),
                label: Text('Token'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.smart_toy),
                label: Text('Botlar'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.dashboard),
                label: Text('Panel'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.admin_panel_settings),
                label: Text('Admin'),
              ),
            ],
          ),
          const VerticalDivider(thickness: 1, width: 1),
          Expanded(
            child: _pages[_selectedIndex],
          ),
        ],
      ),
    );
  }
}

// Keep the old API Test Page for debugging
class ApiTestPage extends StatefulWidget {
  const ApiTestPage({super.key});

  @override
  State<ApiTestPage> createState() => _ApiTestPageState();
}

class _ApiTestPageState extends State<ApiTestPage> {
  bool _isLoading = false;
  String _connectionStatus = "Henüz test edilmedi";
  Color _statusColor = Colors.grey;
  final Dio _dio = Dio();

  @override
  void initState() {
    super.initState();
    // Configure Dio
    _dio.options.connectTimeout = const Duration(seconds: 10);
    _dio.options.receiveTimeout = const Duration(seconds: 10);
  }

  Future<void> _testApiConnection() async {
    setState(() {
      _isLoading = true;
      _connectionStatus = "Bağlantı test ediliyor...";
      _statusColor = Colors.orange;
    });

    try {
      // Test Token API instead
      final response = await _dio.get('http://localhost:5051/health');
      
      if (response.statusCode == 200) {
        setState(() {
          _connectionStatus = "Token API bağlantısı başarılı! ✅";
          _statusColor = Colors.green;
        });
        
        // Success SnackBar
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                "🎉 Token API bağlantısı başarılı!",
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }
      } else {
        throw Exception('HTTP ${response.statusCode}');
      }
      
    } catch (e) {
      setState(() {
        _connectionStatus = "Bağlantı başarısız: ${e.toString()}";
        _statusColor = Colors.red;
      });
      
      // Error SnackBar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              "❌ Bağlantı hatası: ${e.toString()}",
              style: const TextStyle(color: Colors.white),
            ),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2D3436),
      appBar: AppBar(
        title: const Text(
          'OnlyVips v6.0 Token API Test',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        backgroundColor: AppTheme.primaryColor,
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.dashboard, color: Colors.white),
            onPressed: () => Navigator.pushReplacementNamed(context, '/main'),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo & Title
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: const LinearGradient(
                  colors: [Colors.deepPurple, Colors.amber],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: const Icon(
                Icons.monetization_on,
                size: 50,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 32),
            
            const Text(
              'Token API Backend Bağlantı Testi',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            
            const Text(
              'http://localhost:5051/health',
              style: TextStyle(
                fontSize: 16,
                color: Color(0xFF636E72),
                fontFamily: 'monospace',
              ),
            ),
            const SizedBox(height: 48),
            
            // Connection Status Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.amber.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _statusColor.withOpacity(0.3),
                  width: 2,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    _statusColor == Colors.green
                        ? Icons.check_circle
                        : _statusColor == Colors.red
                            ? Icons.error
                            : Icons.info,
                    color: _statusColor,
                    size: 48,
                  ),
                  const SizedBox(height: 16),
                  
                  Text(
                    _connectionStatus,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 16,
                      color: _statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 48),
            
            // Test Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _testApiConnection,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 4,
                ),
                child: _isLoading
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          ),
                          SizedBox(width: 12),
                          Text(
                            'Test Ediliyor...',
                            style: TextStyle(fontSize: 16),
                          ),
                        ],
                      )
                    : const Text(
                        'API Bağlantısını Test Et',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
            const SizedBox(height: 24),
            
            // Go to Dashboard Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: OutlinedButton(
                onPressed: () => Navigator.pushReplacementNamed(context, '/main'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.amber,
                  side: const BorderSide(color: Colors.amber),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  '🚀 Admin Panel\'e Geç',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _dio.close();
    super.dispose();
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;

    final isLoggedIn = await StorageService.isLoggedIn();
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) =>
              isLoggedIn ? const MainNavigationPage() : const LoginPage(),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const FlutterLogo(size: 100),
            const SizedBox(height: 24),
            Text(
              'GavatCore Mobile',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 24),
            const CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
} 