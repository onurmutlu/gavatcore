import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../admin/admin_dashboard_screen.dart';
import '../admin/bot_management_screen.dart';
import '../admin/message_monitor_screen.dart';
import '../admin/revenue_screen.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _selectedIndex = 0;

  final List<Widget> _pages = const [
    AdminDashboardScreen(),
    BotManagementScreen(),
    MessageMonitorScreen(),
    RevenueScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sol Menü
          NavigationRail(
            extended: MediaQuery.of(context).size.width > 800,
            selectedIndex: _selectedIndex,
            backgroundColor: Colors.black87,
            onDestinationSelected: (index) {
              setState(() => _selectedIndex = index);
            },
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.dashboard),
                label: Text('Yönetim Paneli'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.smart_toy),
                label: Text('Bot Yönetimi'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.message),
                label: Text('Mesaj İzleme'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.monetization_on),
                label: Text('Gelir Takibi'),
              ),
            ],
          ),

          // Dikey Çizgi
          const VerticalDivider(thickness: 1, width: 1),

          // Ana İçerik
          Expanded(
            child: _selectedIndex < _pages.length
                ? _pages[_selectedIndex]
                : const Center(
                    child: Text('Sayfa bulunamadı'),
                  ),
          ),
        ],
      ),
    );
  }
} 