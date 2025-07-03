import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/services/dashboard_api_service.dart';
import '../../core/providers/auth_provider.dart';
import '../../shared/themes/app_theme.dart';
import 'admin_dashboard_screen.dart';
import 'token_dashboard_page.dart';

class DashboardPage extends ConsumerStatefulWidget {
  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends ConsumerState<DashboardPage>
    with TickerProviderStateMixin {
  late TabController _tabController;
  
  Map<String, dynamic>? _systemStatus;
  Map<String, dynamic>? _campaignStats;
  List<dynamic>? _recentLogs;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadDashboardData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _isLoading = true);
    
    try {
      final apiService = DashboardApiService();
      final results = await Future.wait([
        apiService.getSystemStatus(),
        apiService.getCampaignStats(),
        apiService.getRecentLogs(),
      ]);
      
      setState(() {
        _systemStatus = results[0] as Map<String, dynamic>?;
        _campaignStats = results[1] as Map<String, dynamic>?;
        _recentLogs = results[2] as List<dynamic>?;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Veri yüklenirken hata: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('🎮 GavatCore Panel'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Ana Panel'),
            Tab(icon: Icon(Icons.admin_panel_settings), text: 'Admin'),
            Tab(icon: Icon(Icons.monetization_on), text: 'Token'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.account_circle),
            onSelected: (value) async {
              if (value == 'logout') {
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) {
                  Navigator.of(context).pushReplacementNamed('/login');
                }
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: [
                    const Icon(Icons.person),
                    const SizedBox(width: 8),
                    Text(authState.when(
                      data: (user) => user?.email ?? 'Admin',
                      loading: () => 'Yükleniyor...',
                      error: (_, __) => 'Admin',
                    )),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: [
                    Icon(Icons.logout, color: Colors.red),
                    SizedBox(width: 8),
                    Text('Çıkış'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildMainDashboard(),
          AdminDashboardScreen(),
          const TokenDashboardPage(),
        ],
      ),
    );
  }

  Widget _buildMainDashboard() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '📊 Sistem Durumu',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildSystemStatusCards(),
            const SizedBox(height: 24),
            const Text(
              '📈 Kampanya İstatistikleri',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildCampaignStats(),
            const SizedBox(height: 24),
            const Text(
              '📝 Son Aktiviteler',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildRecentLogs(),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemStatusCards() {
    if (_systemStatus == null) return const SizedBox();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildStatusCard(
                    'API Server',
                    _systemStatus!['api_status'] ?? 'Unknown',
                    Icons.api,
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildStatusCard(
                    'Database',
                    _systemStatus!['db_status'] ?? 'Unknown',
                    Icons.storage,
                    Colors.blue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatusCard(
                    'Aktif Botlar',
                    _systemStatus!['active_bots']?.toString() ?? '0',
                    Icons.smart_toy,
                    Colors.purple,
                  ),
                ),
                Expanded(
                  child: _buildStatusCard(
                    'Kullanıcılar',
                    _systemStatus!['total_users']?.toString() ?? '0',
                    Icons.people,
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCampaignStats() {
    if (_campaignStats == null) return const SizedBox();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: _buildStatItem(
                'Toplam Mesaj',
                _campaignStats!['total_messages']?.toString() ?? '0',
                Icons.message,
              ),
            ),
            Expanded(
              child: _buildStatItem(
                'Gelir',
                '${_campaignStats!['revenue']?.toString() ?? '0'} ₺',
                Icons.attach_money,
              ),
            ),
            Expanded(
              child: _buildStatItem(
                'Token',
                _campaignStats!['tokens']?.toString() ?? '0',
                Icons.monetization_on,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 24, color: AppTheme.primaryColor),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildRecentLogs() {
    if (_recentLogs == null || _recentLogs!.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('Henüz log bulunmuyor'),
        ),
      );
    }

    return Card(
      child: ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _recentLogs!.length,
        itemBuilder: (context, index) {
          final log = _recentLogs![index];
          return ListTile(
            leading: CircleAvatar(
              backgroundColor: _getLogColor(log['level'] ?? 'info'),
              child: Text(
                _getLogIcon(log['level'] ?? 'info'),
                style: const TextStyle(color: Colors.white),
              ),
            ),
            title: Text(log['message'] ?? ''),
            subtitle: Text(log['timestamp'] ?? ''),
            dense: true,
          );
        },
      ),
    );
  }

  Color _getLogColor(String level) {
    switch (level.toLowerCase()) {
      case 'error':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      case 'success':
        return Colors.green;
      default:
        return Colors.blue;
    }
  }

  String _getLogIcon(String level) {
    switch (level.toLowerCase()) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  }
}