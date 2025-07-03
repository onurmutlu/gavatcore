import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:responsive_builder/responsive_builder.dart';
import 'core/providers/auth_provider.dart';
import 'core/services/telegram_service.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SEFER Panel',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.black,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
        useMaterial3: true,
        navigationRailTheme: const NavigationRailThemeData(
          backgroundColor: Colors.black87,
          selectedIconTheme: IconThemeData(color: Colors.blue),
          selectedLabelTextStyle: TextStyle(color: Colors.blue),
        ),
      ),
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('tr', 'TR'),
      ],
      home: const DashboardScreen(),
    );
  }
}

class AuthWrapper extends ConsumerWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return authState.when(
      data: (user) => user != null ? const DashboardScreen() : const LoginScreen(),
      loading: () => const LoadingScreen(),
      error: (error, stack) => ErrorScreen(error: error.toString()),
    );
  }
}

class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

class ErrorScreen extends StatelessWidget {
  final String error;
  const ErrorScreen({super.key, required this.error});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text('Hata: $error'),
      ),
    );
  }
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Card(
          elevation: 4,
          child: Container(
            padding: const EdgeInsets.all(32),
            constraints: const BoxConstraints(maxWidth: 400),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'SEFER Panel',
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  'Yönetim Paneline Hoş Geldiniz',
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 32),
                Consumer(
                  builder: (context, ref, child) {
                    final authState = ref.watch(authProvider);
                    
                    return authState.when(
                      data: (_) => ElevatedButton.icon(
                        icon: const Icon(Icons.telegram),
                        label: const Text('Telegram ile Giriş Yap'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 32,
                            vertical: 16,
                          ),
                        ),
                        onPressed: () async {
                          try {
                            await ref.read(authProvider.notifier).login();
                          } catch (e) {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Giriş hatası: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          }
                        },
                      ),
                      loading: () => const CircularProgressIndicator(),
                      error: (error, _) => Column(
                        children: [
                          Text(
                            'Hata: $error',
                            style: const TextStyle(color: Colors.red),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              ref.invalidate(authProvider);
                            },
                            child: const Text('Tekrar Dene'),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, sizingInformation) {
        final isMobile = sizingInformation.isMobile;

        return Scaffold(
          appBar: isMobile ? AppBar(
            title: const Text('SEFER Panel'),
            actions: [
              IconButton(
                icon: const Icon(Icons.logout),
                onPressed: () {
                  // TODO: Implement logout
                },
              ),
            ],
          ) : null,
          drawer: isMobile ? _buildDrawer() : null,
          body: Row(
            children: [
              if (!isMobile) _buildNavigationRail(),
              Expanded(
                child: _pages[_selectedIndex],
              ),
            ],
          ),
          bottomNavigationBar: isMobile ? _buildBottomNav() : null,
        );
      },
    );
  }

  final List<Widget> _pages = [
    const OverviewPage(),
    const BotsPage(),
    const AnalyticsPage(),
    const SettingsPage(),
  ];

  Widget _buildNavigationRail() {
    return NavigationRail(
      extended: true,
      selectedIndex: _selectedIndex,
      backgroundColor: Colors.black87,
      onDestinationSelected: (int index) {
        setState(() {
          _selectedIndex = index;
        });
      },
      destinations: const [
        NavigationRailDestination(
          icon: Icon(Icons.dashboard),
          label: Text('Genel Bakış'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.smart_toy),
          label: Text('Botlar'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.analytics),
          label: Text('Analitik'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.settings),
          label: Text('Ayarlar'),
        ),
      ],
    );
  }

  Widget _buildBottomNav() {
    return NavigationBar(
      selectedIndex: _selectedIndex,
      onDestinationSelected: (int index) {
        setState(() {
          _selectedIndex = index;
        });
      },
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.dashboard),
          label: 'Genel',
        ),
        NavigationDestination(
          icon: Icon(Icons.smart_toy),
          label: 'Botlar',
        ),
        NavigationDestination(
          icon: Icon(Icons.analytics),
          label: 'Analitik',
        ),
        NavigationDestination(
          icon: Icon(Icons.settings),
          label: 'Ayarlar',
        ),
      ],
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      child: ListView(
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(
              color: Colors.black87,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 30,
                  child: Icon(Icons.person),
                ),
                SizedBox(height: 16),
                Text('SEFER Panel'),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard),
            title: const Text('Genel Bakış'),
            selected: _selectedIndex == 0,
            onTap: () {
              setState(() {
                _selectedIndex = 0;
              });
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.smart_toy),
            title: const Text('Botlar'),
            selected: _selectedIndex == 1,
            onTap: () {
              setState(() {
                _selectedIndex = 1;
              });
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.analytics),
            title: const Text('Analitik'),
            selected: _selectedIndex == 2,
            onTap: () {
              setState(() {
                _selectedIndex = 2;
              });
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings),
            title: const Text('Ayarlar'),
            selected: _selectedIndex == 3,
            onTap: () {
              setState(() {
                _selectedIndex = 3;
              });
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }
}

class OverviewPage extends StatelessWidget {
  const OverviewPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, sizingInformation) {
        final isMobile = sizingInformation.isMobile;
        final padding = isMobile ? 8.0 : 16.0;
        final crossAxisCount = isMobile ? 1 : 3;

        return Padding(
          padding: EdgeInsets.all(padding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Genel Bakış',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 24),
              Expanded(
                child: GridView.count(
                  crossAxisCount: crossAxisCount,
                  crossAxisSpacing: padding,
                  mainAxisSpacing: padding,
                  children: [
                    _buildStatCard(
                      context,
                      'Aktif Botlar',
                      '12',
                      Icons.smart_toy,
                      Colors.green,
                    ),
                    _buildStatCard(
                      context,
                      'Toplam Mesaj',
                      '1,234',
                      Icons.message,
                      Colors.blue,
                    ),
                    _buildStatCard(
                      context,
                      'Aktif Kullanıcılar',
                      '89',
                      Icons.people,
                      Colors.orange,
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 0,
      color: Colors.black87,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 16),
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class BotsPage extends StatelessWidget {
  const BotsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Bot Yönetimi',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 24),
          Expanded(
            child: ListView(
              children: [
                _buildBotCard(
                  context,
                  'SEFER Bot',
                  'Ana yönetim botu',
                  true,
                ),
                _buildBotCard(
                  context,
                  'Lara Bot',
                  'Asistan bot',
                  true,
                ),
                _buildBotCard(
                  context,
                  'Admin Bot',
                  'Yönetici botu',
                  false,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBotCard(BuildContext context, String name, String description, bool isActive) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isActive ? Colors.green : Colors.grey,
          child: const Icon(Icons.smart_toy, color: Colors.white),
        ),
        title: Text(name),
        subtitle: Text(description),
        trailing: Switch(
          value: isActive,
          onChanged: (value) {
            // TODO: Implement bot activation/deactivation
          },
        ),
      ),
    );
  }
}

class AnalyticsPage extends StatelessWidget {
  const AnalyticsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Analitik',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 24),
          Expanded(
            child: ResponsiveBuilder(
              builder: (context, sizingInformation) {
                final isMobile = sizingInformation.isMobile;
                return GridView.count(
                  crossAxisCount: isMobile ? 1 : 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    _buildAnalyticCard(
                      context,
                      'Günlük Mesaj İstatistikleri',
                      Icons.message,
                    ),
                    _buildAnalyticCard(
                      context,
                      'Kullanıcı Aktivitesi',
                      Icons.people,
                    ),
                    _buildAnalyticCard(
                      context,
                      'Bot Performansı',
                      Icons.speed,
                    ),
                    _buildAnalyticCard(
                      context,
                      'Gelir Analizi',
                      Icons.monetization_on,
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticCard(BuildContext context, String title, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Expanded(
              child: Center(
                child: Text('Grafik burada olacak'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Ayarlar',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 24),
          Expanded(
            child: ListView(
              children: [
                _buildSettingSection(
                  context,
                  'Genel Ayarlar',
                  [
                    _buildSettingTile(
                      context,
                      'Bildirimler',
                      'Bildirim tercihlerini yönet',
                      Icons.notifications,
                    ),
                    _buildSettingTile(
                      context,
                      'Görünüm',
                      'Tema ve görünüm ayarları',
                      Icons.palette,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildSettingSection(
                  context,
                  'Bot Ayarları',
                  [
                    _buildSettingTile(
                      context,
                      'Otomatik Mesajlar',
                      'Bot yanıtlarını özelleştir',
                      Icons.message,
                    ),
                    _buildSettingTile(
                      context,
                      'AI Ayarları',
                      'Yapay zeka parametreleri',
                      Icons.psychology,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingSection(BuildContext context, String title, List<Widget> tiles) {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          const Divider(),
          ...tiles,
        ],
      ),
    );
  }

  Widget _buildSettingTile(BuildContext context, String title, String subtitle, IconData icon) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: () {
        // TODO: Implement settings navigation
      },
    );
  }
}
