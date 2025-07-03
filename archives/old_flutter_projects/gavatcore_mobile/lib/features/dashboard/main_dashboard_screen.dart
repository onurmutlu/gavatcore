import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../../shared/themes/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../core/storage/storage_service.dart';
import '../../shared/widgets/loading_overlay.dart';
import '../admin/character_manager_screen.dart';
import '../admin/behavioral_tracker_screen.dart';
import '../settings/system_settings_screen.dart';
import '../onboarding/showcu_onboarding_screen.dart';

// Dashboard stats provider
final dashboardStatsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getDashboardStats();
});

// System status provider
final systemStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getSystemStatus();
});

// Campaign stats provider
final campaignStatsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getCampaignStats();
});

// Auto refresh provider
final autoRefreshProvider = StateProvider<bool>((ref) => true);

class MainDashboardScreen extends ConsumerStatefulWidget {
  const MainDashboardScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<MainDashboardScreen> createState() => _MainDashboardScreenState();
}

class _MainDashboardScreenState extends ConsumerState<MainDashboardScreen> {
  Timer? _refreshTimer;
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
      label: 'Behavioral',
      color: AppColors.warning,
    ),
    NavigationItem(
      icon: Icons.group_add,
      label: 'Showcu',
      color: AppColors.info,
    ),
    NavigationItem(
      icon: Icons.settings,
      label: 'Ayarlar',
      color: AppColors.textSecondary,
    ),
  ];
  
  @override
  void initState() {
    super.initState();
    _startAutoRefresh();
  }
  
  void _startAutoRefresh() {
    final storage = ref.read(storageServiceProvider);
    final interval = storage.getInt('refresh_interval') ?? 30;
    
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(Duration(seconds: interval), (_) {
      if (ref.read(autoRefreshProvider)) {
        ref.invalidate(dashboardStatsProvider);
        ref.invalidate(systemStatusProvider);
        ref.invalidate(campaignStatsProvider);
      }
    });
  }
  
  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;
    
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Row(
        children: [
          // Sidebar Navigation
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
          
          // Main Content
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                _buildDashboard(),
                const CharacterManagerScreen(),
                const BehavioralTrackerScreen(),
                const ShowcuOnboardingScreen(),
                const SystemSettingsScreen(),
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
  
  Widget _buildDashboard() {
    final dashboardAsync = ref.watch(dashboardStatsProvider);
    final systemAsync = ref.watch(systemStatusProvider);
    final campaignAsync = ref.watch(campaignStatsProvider);
    final autoRefresh = ref.watch(autoRefreshProvider);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: Row(
          children: [
            const Text(
              '🚀 GavatCore Dashboard',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const Spacer(),
            // Auto refresh toggle
            Row(
              children: [
                const Text('Otomatik Yenileme', style: TextStyle(fontSize: 14)),
                const SizedBox(width: 8),
                Switch(
                  value: autoRefresh,
                  onChanged: (value) {
                    ref.read(autoRefreshProvider.notifier).state = value;
                  },
                  activeColor: AppColors.success,
                ),
              ],
            ),
            const SizedBox(width: 16),
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () {
                ref.invalidate(dashboardStatsProvider);
                ref.invalidate(systemStatusProvider);
                ref.invalidate(campaignStatsProvider);
              },
              tooltip: 'Yenile',
            ),
          ],
        ),
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(dashboardStatsProvider);
          ref.invalidate(systemStatusProvider);
          ref.invalidate(campaignStatsProvider);
          await Future.delayed(const Duration(seconds: 1));
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // System Status Row
              systemAsync.when(
                loading: () => const _LoadingCard(height: 120),
                error: (_, __) => const _ErrorCard(message: 'Sistem durumu yüklenemedi'),
                data: (status) => _SystemStatusCard(status: status),
              ),
              
              const SizedBox(height: 16),
              
              // Quick Stats Grid
              dashboardAsync.when(
                loading: () => const _LoadingCard(height: 200),
                error: (_, __) => const _ErrorCard(message: 'İstatistikler yüklenemedi'),
                data: (stats) => _QuickStatsGrid(stats: stats),
              ),
              
              const SizedBox(height: 16),
              
              // Bot Performance Cards
              systemAsync.when(
                loading: () => const _LoadingCard(height: 300),
                error: (_, __) => const SizedBox.shrink(),
                data: (status) => _BotPerformanceSection(bots: status['bots'] ?? []),
              ),
              
              const SizedBox(height: 16),
              
              // Campaign Stats
              campaignAsync.when(
                loading: () => const _LoadingCard(height: 200),
                error: (_, __) => const SizedBox.shrink(),
                data: (campaign) => _CampaignStatsCard(campaign: campaign),
              ),
              
              const SizedBox(height: 32),
            ],
          ),
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

class _SystemStatusCard extends StatelessWidget {
  final Map<String, dynamic> status;
  
  const _SystemStatusCard({required this.status});
  
  @override
  Widget build(BuildContext context) {
    final systemStats = status['system_stats'] ?? {};
    final healthStatus = systemStats['health_status'] ?? 'unknown';
    final processInfo = status['process_info'];
    
    Color statusColor;
    IconData statusIcon;
    String statusText;
    
    switch (healthStatus) {
      case 'healthy':
        statusColor = AppColors.success;
        statusIcon = Icons.check_circle;
        statusText = 'Sistem Sağlıklı';
        break;
      case 'degraded':
        statusColor = AppColors.warning;
        statusIcon = Icons.warning;
        statusText = 'Kısmi Sorun';
        break;
      case 'critical':
        statusColor = AppColors.error;
        statusIcon = Icons.error;
        statusText = 'Kritik Durum';
        break;
      default:
        statusColor = AppColors.textSecondary;
        statusIcon = Icons.help;
        statusText = 'Bilinmiyor';
    }
    
    return Card(
      color: statusColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(statusIcon, size: 48, color: statusColor),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    statusText,
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    processInfo != null
                        ? 'PID: ${processInfo['pid']} | Uptime: ${processInfo['uptime_human']}'
                        : 'Process durumu bilinmiyor',
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            // Quick actions
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.bug_report),
                  onPressed: () {
                    // Show logs
                  },
                  tooltip: 'Logları Göster',
                ),
                IconButton(
                  icon: const Icon(Icons.restart_alt),
                  onPressed: () {
                    // Restart system
                  },
                  tooltip: 'Sistemi Yeniden Başlat',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _QuickStatsGrid extends StatelessWidget {
  final Map<String, dynamic> stats;
  
  const _QuickStatsGrid({required this.stats});
  
  @override
  Widget build(BuildContext context) {
    final items = [
      _StatItem(
        title: 'Toplam Kullanıcı',
        value: stats['total_users']?.toString() ?? '0',
        icon: Icons.people,
        color: AppColors.primary,
        trend: stats['user_trend'],
      ),
      _StatItem(
        title: 'Aktif Session',
        value: stats['active_sessions']?.toString() ?? '0',
        icon: Icons.online_prediction,
        color: AppColors.success,
      ),
      _StatItem(
        title: 'Bugünkü Mesaj',
        value: stats['messages_today']?.toString() ?? '0',
        icon: Icons.message,
        color: AppColors.info,
        trend: stats['message_trend'],
      ),
      _StatItem(
        title: 'VIP Adayı',
        value: stats['vip_candidates']?.toString() ?? '0',
        icon: Icons.star,
        color: Colors.amber,
      ),
    ];
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: MediaQuery.of(context).size.width > 600 ? 4 : 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 1.5,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return _StatCard(item: item);
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  final _StatItem item;
  
  const _StatCard({required this.item});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(item.icon, color: item.color, size: 24),
                if (item.trend != null)
                  _TrendIndicator(trend: item.trend!),
              ],
            ),
            const Spacer(),
            Text(
              item.value,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: item.color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              item.title,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _BotPerformanceSection extends StatelessWidget {
  final List<dynamic> bots;
  
  const _BotPerformanceSection({required this.bots});
  
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '🤖 Bot Performansı',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...bots.map((bot) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _BotPerformanceCard(bot: bot),
        )).toList(),
      ],
    );
  }
}

class _BotPerformanceCard extends StatelessWidget {
  final Map<String, dynamic> bot;
  
  const _BotPerformanceCard({required this.bot});
  
  @override
  Widget build(BuildContext context) {
    final isActive = bot['status'] == 'active';
    final performanceScore = bot['performance_score'] ?? 0;
    
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: isActive ? AppColors.success : AppColors.error,
                  radius: 24,
                  child: Text(
                    bot['display_name']?.split(' ').last ?? '?',
                    style: const TextStyle(fontSize: 20),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        bot['display_name'] ?? 'Unknown Bot',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        bot['telegram_handle'] ?? '',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                // Status and Score
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: isActive ? AppColors.success.withOpacity(0.2) : AppColors.error.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        isActive ? 'Aktif' : 'Pasif',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: isActive ? AppColors.success : AppColors.error,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Skor: $performanceScore',
                      style: TextStyle(
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Stats Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _BotStatItem(
                  label: 'Mesaj',
                  value: bot['messages_sent']?.toString() ?? '0',
                  icon: Icons.message,
                ),
                _BotStatItem(
                  label: 'Davet',
                  value: bot['invites_sent']?.toString() ?? '0',
                  icon: Icons.group_add,
                ),
                _BotStatItem(
                  label: 'Uptime',
                  value: bot['uptime'] ?? 'Offline',
                  icon: Icons.access_time,
                ),
                _BotStatItem(
                  label: 'Hata',
                  value: bot['errors']?.toString() ?? '0',
                  icon: Icons.error_outline,
                  color: AppColors.error,
                ),
              ],
            ),
            if (isActive) ...[
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: performanceScore / 100,
                backgroundColor: AppColors.surface,
                valueColor: AlwaysStoppedAnimation<Color>(
                  performanceScore > 80 ? AppColors.success :
                  performanceScore > 50 ? AppColors.warning : AppColors.error,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _CampaignStatsCard extends StatelessWidget {
  final Map<String, dynamic> campaign;
  
  const _CampaignStatsCard({required this.campaign});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.campaign, color: AppColors.primary),
                const SizedBox(width: 8),
                const Text(
                  '📢 Kampanya Durumu',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                if (campaign['is_active'] == true)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text(
                      'Aktif',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: AppColors.success,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _CampaignStatItem(
                  label: 'Hedef',
                  value: campaign['total_targets']?.toString() ?? '0',
                  icon: Icons.track_changes,
                ),
                _CampaignStatItem(
                  label: 'Ulaşılan',
                  value: campaign['reached_targets']?.toString() ?? '0',
                  icon: Icons.check_circle,
                  color: AppColors.success,
                ),
                _CampaignStatItem(
                  label: 'Başarı Oranı',
                  value: '${campaign['success_rate'] ?? 0}%',
                  icon: Icons.trending_up,
                  color: AppColors.info,
                ),
                _CampaignStatItem(
                  label: 'Kalan Süre',
                  value: campaign['remaining_time'] ?? 'N/A',
                  icon: Icons.timer,
                  color: AppColors.warning,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// Helper Widgets
class _StatItem {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final double? trend;
  
  _StatItem({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    this.trend,
  });
}

class _TrendIndicator extends StatelessWidget {
  final double trend;
  
  const _TrendIndicator({required this.trend});
  
  @override
  Widget build(BuildContext context) {
    final isPositive = trend > 0;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          isPositive ? Icons.trending_up : Icons.trending_down,
          size: 16,
          color: isPositive ? AppColors.success : AppColors.error,
        ),
        Text(
          '${trend.abs().toStringAsFixed(1)}%',
          style: TextStyle(
            fontSize: 12,
            color: isPositive ? AppColors.success : AppColors.error,
          ),
        ),
      ],
    );
  }
}

class _BotStatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? color;
  
  const _BotStatItem({
    required this.label,
    required this.value,
    required this.icon,
    this.color,
  });
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 16, color: color ?? AppColors.textSecondary),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}

class _CampaignStatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? color;
  
  const _CampaignStatItem({
    required this.label,
    required this.value,
    required this.icon,
    this.color,
  });
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 20, color: color ?? AppColors.primary),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}

class _LoadingCard extends StatelessWidget {
  final double height;
  
  const _LoadingCard({required this.height});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      child: SizedBox(
        height: height,
        child: const Center(
          child: CircularProgressIndicator(),
        ),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  final String message;
  
  const _ErrorCard({required this.message});
  
  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.error.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.error_outline, color: AppColors.error),
            const SizedBox(width: 12),
            Text(
              message,
              style: TextStyle(color: AppColors.error),
            ),
          ],
        ),
      ),
    );
  }
} 