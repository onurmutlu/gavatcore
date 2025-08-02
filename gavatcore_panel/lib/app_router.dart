import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/auth/telegram_auth_screen.dart';
import 'features/messaging/messaging_screen.dart';
import 'features/dashboard/dashboard_screen.dart';
import 'features/auth/login_screen.dart';
import 'core/providers/auth_provider.dart';

class AppRouter {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/':
        return MaterialPageRoute(
          builder: (_) => const AuthWrapper(),
        );
      case '/telegram-auth':
        return MaterialPageRoute(
          builder: (_) => const TelegramAuthScreen(),
        );
      case '/messaging':
        return MaterialPageRoute(
          builder: (_) => const MessagingScreen(),
        );
      case '/dashboard':
        return MaterialPageRoute(
          builder: (_) => const DashboardScreen(),
        );
      case '/login':
        return MaterialPageRoute(
          builder: (_) => const LoginScreen(),
        );
      default:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Route not found'),
            ),
          ),
        );
    }
  }
}

class AuthWrapper extends ConsumerWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return authState.when(
      loading: () => const Scaffold(
        backgroundColor: Color(0xFF0A0A0F),
        body: Center(
          child: CircularProgressIndicator(color: Colors.purple),
        ),
      ),
      error: (error, stackTrace) => const TelegramAuthScreen(),
      data: (user) {
        if (user != null) {
          return const MainAppScreen();
        } else {
          return const TelegramAuthScreen();
        }
      },
    );
  }
}

class MainAppScreen extends StatefulWidget {
  const MainAppScreen({super.key});

  @override
  State<MainAppScreen> createState() => _MainAppScreenState();
}

class _MainAppScreenState extends State<MainAppScreen> {
  int _selectedIndex = 0;

  final List<NavigationItem> _navigationItems = [
    NavigationItem(
      icon: Icons.dashboard,
      label: 'Dashboard',
      color: const Color(0xFF4CAF50),
    ),
    NavigationItem(
      icon: Icons.telegram,
      label: 'Messaging',
      color: const Color(0xFF2196F3),
    ),
    NavigationItem(
      icon: Icons.smart_toy,
      label: 'Bots',
      color: const Color(0xFF9C27B0),
    ),
    NavigationItem(
      icon: Icons.analytics,
      label: 'Analytics',
      color: const Color(0xFFFF9800),
    ),
    NavigationItem(
      icon: Icons.settings,
      label: 'Settings',
      color: const Color(0xFF757575),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
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
              backgroundColor: const Color(0xFF1A1A1F),
              destinations: _navigationItems
                  .map((item) => NavigationRailDestination(
                        icon: Icon(item.icon, color: const Color(0xFF757575)),
                        selectedIcon: Icon(item.icon, color: item.color),
                        label: Text(
                          item.label,
                          style: const TextStyle(color: Colors.white),
                        ),
                      ))
                  .toList(),
            ),
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                const DashboardScreen(),
                const MessagingScreen(),
                _buildBotsContent(),
                _buildAnalyticsContent(),
                _buildSettingsContent(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: !isDesktop
          ? NavigationBar(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
              backgroundColor: const Color(0xFF1A1A1F),
              indicatorColor: Colors.purple,
              destinations: _navigationItems
                  .map((item) => NavigationDestination(
                        icon: Icon(item.icon),
                        selectedIcon: Icon(item.icon, color: item.color),
                        label: item.label,
                      ))
                  .toList(),
            )
          : null,
    );
  }

  Widget _buildBotsContent() {
    return const Scaffold(
      backgroundColor: Color(0xFF0A0A0F),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.smart_toy,
              size: 64,
              color: Colors.purple,
            ),
            SizedBox(height: 16),
            Text(
              'Bot Management',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Coming Soon',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnalyticsContent() {
    return const Scaffold(
      backgroundColor: Color(0xFF0A0A0F),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.analytics,
              size: 64,
              color: Colors.orange,
            ),
            SizedBox(height: 16),
            Text(
              'Analytics',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Coming Soon',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 16,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingsContent() {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        title: const Text(
          'Settings',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1A1A2E),
        elevation: 0,
      ),
      body: Consumer(
        builder: (context, ref, child) {
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ListTile(
                leading: const Icon(Icons.logout, color: Colors.red),
                title: const Text(
                  'Logout',
                  style: TextStyle(color: Colors.white),
                ),
                subtitle: const Text(
                  'Sign out of your account',
                  style: TextStyle(color: Colors.grey),
                ),
                onTap: () async {
                  await ref.read(authProvider.notifier).logout();
                  if (context.mounted) {
                    Navigator.of(context).pushReplacementNamed('/');
                  }
                },
              ),
            ],
          );
        },
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