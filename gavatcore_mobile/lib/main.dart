import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:universal_html/html.dart' as html;
import 'core/services/telegram_init.dart';

import 'core/storage/storage_service.dart';
import 'shared/themes/app_theme.dart';
import 'features/dashboard/presentation/pages/dashboard_page.dart';
import 'features/dashboard/presentation/pages/token_dashboard_page.dart';
import 'features/bots/presentation/pages/bot_management_page.dart';
import 'features/auth/presentation/pages/login_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive
  await Hive.initFlutter();
  await StorageService.init();
  
  // Shared Preferences başlat
  final prefs = await SharedPreferences.getInstance();
  
  // Telegram WebApp kontrolü
  final initDataString = Uri.base.queryParameters['tgWebAppData'];
  Map<String, dynamic> userData = {};
  
  if (initDataString != null) {
    final initData = await TelegramInitService.decodeAndVerifyInitData(initDataString);
    if (initData['is_valid']) {
      userData = initData['user'];
      await prefs.setString('user_data', initData['user'].toString());
    }
  }
  
  runApp(
    ProviderScope(
      child: GAVATCorePanel(userData: userData),
    ),
  );
}

class GAVATCorePanel extends StatelessWidget {
  final Map<String, dynamic> userData;
  
  const GAVATCorePanel({
    Key? key,
    required this.userData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SEFER Panel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.dark(
          primary: Color(0xFF007AFF),
          secondary: Color(0xFF0A84FF),
          background: Color(0xFF1A1A1A),
          surface: Color(0xFF2C2C2E),
        ),
        scaffoldBackgroundColor: Color(0xFF1A1A1A),
      ),
      home: MainDashboard(userData: userData),
    );
  }
}

class MainDashboard extends StatelessWidget {
  final Map<String, dynamic> userData;
  
  const MainDashboard({
    Key? key,
    required this.userData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text(
          'Hoş geldin ${userData['first_name'] ?? 'Misafir'}!',
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}

class MainNavigationPage extends StatefulWidget {
  const MainNavigationPage({super.key});

  @override
  State<MainNavigationPage> createState() => _MainNavigationPageState();
}

class _MainNavigationPageState extends State<MainNavigationPage> {
  int _selectedIndex = 0;
  final PageController _pageController = PageController();

  final List<Widget> _pages = [
    const TokenDashboardPage(),
    const BotManagementPage(),
    const DashboardPage(),
  ];

  final List<NavigationDestination> _destinations = [
    const NavigationDestination(
      icon: Icon(Icons.monetization_on),
      selectedIcon: Icon(Icons.monetization_on, color: Colors.amber),
      label: 'Token Economy',
    ),
    const NavigationDestination(
      icon: Icon(Icons.smart_toy),
      selectedIcon: Icon(Icons.smart_toy, color: Colors.deepPurple),
      label: 'Bot Management',
    ),
    const NavigationDestination(
      icon: Icon(Icons.dashboard),
      selectedIcon: Icon(Icons.dashboard, color: Colors.blue),
      label: 'General Dashboard',
    ),
  ];

  void _onDestinationSelected(int index) {
    setState(() {
      _selectedIndex = index;
    });
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: PageView(
        controller: _pageController,
        children: _pages,
        onPageChanged: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onDestinationSelected,
        backgroundColor: AppTheme.cardBg,
        indicatorColor: AppTheme.primaryColor.withOpacity(0.2),
        surfaceTintColor: Colors.transparent,
        destinations: _destinations,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      ),
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
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

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _animationController.forward();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    await Future.delayed(const Duration(seconds: 3));
    
    // Check if user is logged in
    final isLoggedIn = await StorageService.isLoggedIn();
    
    if (mounted) {
      if (isLoggedIn) {
        Navigator.pushReplacementNamed(context, '/dashboard');
      } else {
        Navigator.pushReplacementNamed(context, '/login');
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF2D3436),
      body: Center(
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // GavatCore Logo
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30),
                  gradient: const LinearGradient(
                    colors: [Colors.deepPurple, Colors.amber],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: const Icon(
                  Icons.smart_toy_rounded,
                  size: 60,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 24),
              
              // App Title
              const Text(
                'GavatCore',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  fontFamily: 'Poppins',
                ),
              ),
              const SizedBox(height: 8),
              
              // Subtitle
              const Text(
                'Delikanlı Gibi Yazılımcı',
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFF636E72),
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 8),
              
              // Version
              const Text(
                'Mobile Edition v3.0',
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF636E72),
                  fontFamily: 'Inter',
                ),
              ),
              const SizedBox(height: 48),
              
              // Loading Indicator
              CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.deepPurple),
              ),
              const SizedBox(height: 24),
              
              // Loading Text
              const Text(
                'YAŞASIN SPONSORLAR! 🔥',
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFFE17055),
                  fontWeight: FontWeight.w500,
                  fontFamily: 'Inter',
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 