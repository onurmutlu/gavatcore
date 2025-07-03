import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_web_plugins/url_strategy.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Remove # from URL in web
  usePathUrlStrategy();
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0A0A0F),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  
  runApp(
    const ProviderScope(
      child: GavatCoreApp(),
    ),
  );
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
        cardTheme: CardThemeData(
          color: AppColors.surface,
          elevation: 2,
          margin: const EdgeInsets.all(8),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const SimpleDashboard(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SimpleDashboard extends StatefulWidget {
  const SimpleDashboard({Key? key}) : super(key: key);

  @override
  State<SimpleDashboard> createState() => _SimpleDashboardState();
}

class _SimpleDashboardState extends State<SimpleDashboard> {
  int _selectedIndex = 0;

  final List<NavigationItem> _navigationItems = [
    NavigationItem(
      icon: Icons.dashboard,
      label: 'Dashboard',
      color: AppColors.primary,
    ),
    NavigationItem(
      icon: Icons.smart_toy,
      label: 'Karakterler',
      color: AppColors.success,
    ),
    NavigationItem(
      icon: Icons.analytics,
      label: 'Analitik',
      color: AppColors.warning,
    ),
    NavigationItem(
      icon: Icons.settings,
      label: 'Ayarlar',
      color: AppColors.textSecondary,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Row(
        children: [
          if (isDesktop)
            NavigationRail(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              extended: true,
              backgroundColor: AppColors.surface,
              destinations: _navigationItems.map((item) => NavigationRailDestination(
                icon: Icon(item.icon, color: AppColors.textSecondary),
                selectedIcon: Icon(item.icon, color: item.color),
                label: Text(item.label),
              )).toList(),
            ),
          
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                _buildDashboardContent(),
                const CharacterManagerScreen(),
                _buildAnalyticsContent(),
                _buildSettingsContent(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: !isDesktop ? NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: _navigationItems.map((item) => NavigationDestination(
          icon: Icon(item.icon),
          label: item.label,
        )).toList(),
      ) : null,
    );
  }

  Widget _buildDashboardContent() {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: const Text(
          '🚀 GavatCore Dashboard',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: GridView.count(
          crossAxisCount: MediaQuery.of(context).size.width > 1200 ? 4 : 2,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          children: [
            _buildStatCard(
              'Aktif Karakterler',
              '5',
              Icons.smart_toy,
              AppColors.primary,
            ),
            _buildStatCard(
              'Toplam Mesaj',
              '12,543',
              Icons.message,
              AppColors.success,
            ),
            _buildStatCard(
              'Sistem Durumu',
              'Çalışıyor',
              Icons.check_circle,
              AppColors.success,
            ),
            _buildStatCard(
              'API Yanıt Süresi',
              '120ms',
              Icons.speed,
              AppColors.warning,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsContent() {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: const Text('📊 Analitik'),
        elevation: 0,
      ),
      body: const Center(
        child: Text(
          'Analitik gösterimi burada olacak',
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  }

  Widget _buildSettingsContent() {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: const Text('⚙️ Ayarlar'),
        elevation: 0,
      ),
      body: const Center(
        child: Text(
          'Sistem ayarları burada olacak',
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class NavigationItem {
  final IconData icon;
  final String label;
  final Color color;

  NavigationItem({
    required this.icon,
    required this.label,
    required this.color,
  });
} 