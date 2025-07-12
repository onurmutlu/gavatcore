import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'package:fl_chart/fl_chart.dart';
import '../telegram/telegram_miniapp_integration.dart';

// Models
class SystemOverview {
  final int totalUsers;
  final int activeBots;
  final int totalBots;
  final int totalMessagesToday;
  final double totalRevenueToday;
  final double totalRevenueMonth;
  final int activeSubscriptions;
  final double systemUptime;
  final String serverStatus;

  SystemOverview({
    required this.totalUsers,
    required this.activeBots,
    required this.totalBots,
    required this.totalMessagesToday,
    required this.totalRevenueToday,
    required this.totalRevenueMonth,
    required this.activeSubscriptions,
    required this.systemUptime,
    required this.serverStatus,
  });

  factory SystemOverview.fromJson(Map<String, dynamic> json) {
    return SystemOverview(
      totalUsers: json['total_users'] ?? 0,
      activeBots: json['active_bots'] ?? 0,
      totalBots: json['total_bots'] ?? 0,
      totalMessagesToday: json['total_messages_today'] ?? 0,
      totalRevenueToday: (json['total_revenue_today'] ?? 0.0).toDouble(),
      totalRevenueMonth: (json['total_revenue_month'] ?? 0.0).toDouble(),
      activeSubscriptions: json['active_subscriptions'] ?? 0,
      systemUptime: (json['system_uptime'] ?? 0.0).toDouble(),
      serverStatus: json['server_status'] ?? 'unknown',
    );
  }
}

class PerformerStats {
  final String performerName;
  final String status;
  final int totalMessages;
  final int messagesToday;
  final double responseTimeAvg;
  final double onlineTimeHours;
  final double earningsToday;
  final double earningsMonth;
  final double engagementRate;
  final String lastActive;

  PerformerStats({
    required this.performerName,
    required this.status,
    required this.totalMessages,
    required this.messagesToday,
    required this.responseTimeAvg,
    required this.onlineTimeHours,
    required this.earningsToday,
    required this.earningsMonth,
    required this.engagementRate,
    required this.lastActive,
  });

  factory PerformerStats.fromJson(Map<String, dynamic> json) {
    return PerformerStats(
      performerName: json['performer_name'] ?? '',
      status: json['status'] ?? 'unknown',
      totalMessages: json['total_messages'] ?? 0,
      messagesToday: json['messages_today'] ?? 0,
      responseTimeAvg: (json['response_time_avg'] ?? 0.0).toDouble(),
      onlineTimeHours: (json['online_time_hours'] ?? 0.0).toDouble(),
      earningsToday: (json['earnings_today'] ?? 0.0).toDouble(),
      earningsMonth: (json['earnings_month'] ?? 0.0).toDouble(),
      engagementRate: (json['engagement_rate'] ?? 0.0).toDouble(),
      lastActive: json['last_active'] ?? '',
    );
  }
}

class AnalyticsData {
  final String date;
  final int totalMessages;
  final int uniqueUsers;
  final double revenue;
  final int newSubscriptions;
  final double botUptime;

  AnalyticsData({
    required this.date,
    required this.totalMessages,
    required this.uniqueUsers,
    required this.revenue,
    required this.newSubscriptions,
    required this.botUptime,
  });

  factory AnalyticsData.fromJson(Map<String, dynamic> json) {
    return AnalyticsData(
      date: json['date'] ?? '',
      totalMessages: json['total_messages'] ?? 0,
      uniqueUsers: json['unique_users'] ?? 0,
      revenue: (json['revenue'] ?? 0.0).toDouble(),
      newSubscriptions: json['new_subscriptions'] ?? 0,
      botUptime: (json['bot_uptime'] ?? 0.0).toDouble(),
    );
  }
}

class RealtimeStats {
  final int activeUsers;
  final int messagesPerMinute;
  final double cpuUsage;
  final double memoryUsage;
  final double diskUsage;
  final Map<String, double> networkIO;
  final int activeSessions;
  final double errorRate;
  final double responseTime;
  final String uptime;

  RealtimeStats({
    required this.activeUsers,
    required this.messagesPerMinute,
    required this.cpuUsage,
    required this.memoryUsage,
    required this.diskUsage,
    required this.networkIO,
    required this.activeSessions,
    required this.errorRate,
    required this.responseTime,
    required this.uptime,
  });

  factory RealtimeStats.fromJson(Map<String, dynamic> json) {
    return RealtimeStats(
      activeUsers: json['active_users'] ?? 0,
      messagesPerMinute: json['messages_per_minute'] ?? 0,
      cpuUsage: (json['cpu_usage'] ?? 0.0).toDouble(),
      memoryUsage: (json['memory_usage'] ?? 0.0).toDouble(),
      diskUsage: (json['disk_usage'] ?? 0.0).toDouble(),
      networkIO: Map<String, double>.from(json['network_io'] ?? {'in': 0.0, 'out': 0.0}),
      activeSessions: json['active_sessions'] ?? 0,
      errorRate: (json['error_rate'] ?? 0.0).toDouble(),
      responseTime: (json['response_time'] ?? 0.0).toDouble(),
      uptime: json['uptime'] ?? '',
    );
  }
}

// API Service
class DashboardAPIService {
  static const String baseUrl = 'http://localhost:5050/api/dashboard';

  static Future<SystemOverview> getSystemOverview() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/overview'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return SystemOverview.fromJson(data);
      }
    } catch (e) {
      print('Failed to get system overview: $e');
    }

    // Mock data if API unavailable
    return SystemOverview(
      totalUsers: 127,
      activeBots: 2,
      totalBots: 3,
      totalMessagesToday: 345,
      totalRevenueToday: 1250.0,
      totalRevenueMonth: 18750.0,
      activeSubscriptions: 89,
      systemUptime: 99.8,
      serverStatus: 'healthy',
    );
  }

  static Future<List<PerformerStats>> getPerformerStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/performers'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => PerformerStats.fromJson(json)).toList();
      }
    } catch (e) {
      print('Failed to get performer stats: $e');
    }

    // Mock data if API unavailable
    return [
      PerformerStats(
        performerName: 'Yayıncı Lara',
        status: 'active',
        totalMessages: 1247,
        messagesToday: 89,
        responseTimeAvg: 2.3,
        onlineTimeHours: 8.5,
        earningsToday: 445.0,
        earningsMonth: 13350.0,
        engagementRate: 92.4,
        lastActive: DateTime.now().toIso8601String(),
      ),
      PerformerStats(
        performerName: 'XXX Geisha',
        status: 'active',
        totalMessages: 856,
        messagesToday: 67,
        responseTimeAvg: 1.8,
        onlineTimeHours: 6.2,
        earningsToday: 335.0,
        earningsMonth: 10050.0,
        engagementRate: 88.7,
        lastActive: DateTime.now().toIso8601String(),
      ),
      PerformerStats(
        performerName: 'Gavat Baba',
        status: 'banned',
        totalMessages: 0,
        messagesToday: 0,
        responseTimeAvg: 0.0,
        onlineTimeHours: 0.0,
        earningsToday: 0.0,
        earningsMonth: 0.0,
        engagementRate: 0.0,
        lastActive: DateTime.now().subtract(const Duration(days: 5)).toIso8601String(),
      ),
    ];
  }

  static Future<List<AnalyticsData>> getAnalytics({int days = 7}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/analytics?days=$days'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => AnalyticsData.fromJson(json)).toList();
      }
    } catch (e) {
      print('Failed to get analytics: $e');
    }

    // Mock data if API unavailable
    return List.generate(days, (index) {
      final date = DateTime.now().subtract(Duration(days: index));
      return AnalyticsData(
        date: date.toIso8601String().split('T')[0],
        totalMessages: 100 + (index * 20),
        uniqueUsers: 50 + (index * 5),
        revenue: 500.0 + (index * 100),
        newSubscriptions: 5 + index,
        botUptime: 95.0 + (index % 5),
      );
    });
  }

  static Future<RealtimeStats> getRealtimeStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/realtime/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return RealtimeStats.fromJson(data);
      }
    } catch (e) {
      print('Failed to get real-time stats: $e');
    }

    // Mock data if API unavailable
    return RealtimeStats(
      activeUsers: 45,
      messagesPerMinute: 12,
      cpuUsage: 35.2,
      memoryUsage: 68.1,
      diskUsage: 42.3,
      networkIO: {'in': 1.2, 'out': 0.8},
      activeSessions: 23,
      errorRate: 0.02,
      responseTime: 1.8,
      uptime: '15d 4h 32m',
    );
  }
}

// Providers
final systemOverviewProvider = FutureProvider<SystemOverview>((ref) async {
  return await DashboardAPIService.getSystemOverview();
});

final performerStatsProvider = FutureProvider<List<PerformerStats>>((ref) async {
  return await DashboardAPIService.getPerformerStats();
});

final analyticsProvider = FutureProvider<List<AnalyticsData>>((ref) async {
  return await DashboardAPIService.getAnalytics();
});

final realtimeStatsProvider = FutureProvider<RealtimeStats>((ref) async {
  return await DashboardAPIService.getRealtimeStats();
});

// Main Dashboard Screen
class ComprehensiveDashboard extends ConsumerStatefulWidget {
  const ComprehensiveDashboard({super.key});

  @override
  ConsumerState<ComprehensiveDashboard> createState() => _ComprehensiveDashboardState();
}

class _ComprehensiveDashboardState extends ConsumerState<ComprehensiveDashboard> {
  Timer? _refreshTimer;
  int _selectedNavIndex = 0;

  @override
  void initState() {
    super.initState();
    _startAutoRefresh();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  void _startAutoRefresh() {
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        ref.invalidate(systemOverviewProvider);
        ref.invalidate(performerStatsProvider);
        ref.invalidate(realtimeStatsProvider);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A2E),
        title: const Row(
          children: [
            Icon(Icons.dashboard, color: Colors.white),
            SizedBox(width: 10),
            Text(
              'GavatCore Yönetim Paneli',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        actions: [
          // Telegram user info
          if (TelegramMiniApp.instance.isTelegramWebApp && TelegramMiniApp.instance.currentUser != null)
            Padding(
              padding: const EdgeInsets.only(right: 10),
              child: TelegramUserWidget(user: TelegramMiniApp.instance.currentUser!),
            ),
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: () {
              ref.invalidate(systemOverviewProvider);
              ref.invalidate(performerStatsProvider);
              ref.invalidate(analyticsProvider);
              ref.invalidate(realtimeStatsProvider);
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings, color: Colors.white),
            onPressed: () {
              // Settings action
            },
          ),
        ],
      ),
      body: Row(
        children: [
          // Sidebar Navigation
          Container(
            width: 250,
            color: const Color(0xFF1A1A2E),
            child: Column(
              children: [
                const SizedBox(height: 20),
                _buildNavItem(0, Icons.dashboard, 'Dashboard'),
                _buildNavItem(1, Icons.people, 'Şovcular'),
                _buildNavItem(2, Icons.bar_chart, 'Analitik'),
                _buildNavItem(3, Icons.payment, 'Ödemeler'),
                _buildNavItem(4, Icons.card_membership, 'Lisanslar'),
                _buildNavItem(5, Icons.settings, 'Ayarlar'),
                const Spacer(),
                _buildRealtimeWidget(),
                const SizedBox(height: 20),
              ],
            ),
          ),
          // Main Content
          Expanded(
            child: _buildMainContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String title) {
    final isSelected = _selectedNavIndex == index;
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: isSelected ? const Color(0xFF7B68EE) : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
      ),
      child: ListTile(
        leading: Icon(icon, color: Colors.white),
        title: Text(
          title,
          style: const TextStyle(color: Colors.white),
        ),
        onTap: () {
          setState(() {
            _selectedNavIndex = index;
          });
        },
      ),
    );
  }

  Widget _buildRealtimeWidget() {
    return Consumer(
      builder: (context, ref, child) {
        final realtimeAsync = ref.watch(realtimeStatsProvider);
        return realtimeAsync.when(
          data: (stats) => Container(
            margin: const EdgeInsets.all(10),
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: const Color(0xFF2A2A3E),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Sistem Durumu',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 10),
                _buildRealtimeItem('Aktif Kullanıcı', '${stats.activeUsers}'),
                _buildRealtimeItem('CPU', '${stats.cpuUsage.toStringAsFixed(1)}%'),
                _buildRealtimeItem('RAM', '${stats.memoryUsage.toStringAsFixed(1)}%'),
                _buildRealtimeItem('Uptime', stats.uptime),
              ],
            ),
          ),
          loading: () => Container(
            margin: const EdgeInsets.all(10),
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: const Color(0xFF2A2A3E),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          ),
          error: (error, stack) => Container(
            margin: const EdgeInsets.all(10),
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: const Color(0xFF2A2A3E),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Text(
              'Sistem durumu alınamadı',
              style: TextStyle(color: Colors.red),
            ),
          ),
        );
      },
    );
  }

  Widget _buildRealtimeItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildMainContent() {
    switch (_selectedNavIndex) {
      case 0:
        return _buildDashboardContent();
      case 1:
        return _buildPerformersContent();
      case 2:
        return _buildAnalyticsContent();
      case 3:
        return _buildPaymentsContent();
      case 4:
        return _buildLicensesContent();
      case 5:
        return _buildSettingsContent();
      default:
        return _buildDashboardContent();
    }
  }

  Widget _buildDashboardContent() {
    return Consumer(
      builder: (context, ref, child) {
        final overviewAsync = ref.watch(systemOverviewProvider);
        final performersAsync = ref.watch(performerStatsProvider);

        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Sistem Genel Bakış',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              overviewAsync.when(
                data: (overview) => _buildOverviewCards(overview),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => const Center(
                  child: Text('Veri yüklenemedi', style: TextStyle(color: Colors.red)),
                ),
              ),
              const SizedBox(height: 30),
              const Text(
                'Şovcu Performansı',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              performersAsync.when(
                data: (performers) => _buildPerformersGrid(performers),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => const Center(
                  child: Text('Şovcu verileri yüklenemedi', style: TextStyle(color: Colors.red)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildOverviewCards(SystemOverview overview) {
    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.5,
      crossAxisSpacing: 15,
      mainAxisSpacing: 15,
      children: [
        _buildStatCard(
          'Toplam Kullanıcı',
          '${overview.totalUsers}',
          Icons.people,
          Colors.blue,
        ),
        _buildStatCard(
          'Aktif Botlar',
          '${overview.activeBots}/${overview.totalBots}',
          Icons.smart_toy,
          Colors.green,
        ),
        _buildStatCard(
          'Günlük Gelir',
          '${overview.totalRevenueToday.toStringAsFixed(0)} ₺',
          Icons.attach_money,
          Colors.orange,
        ),
        _buildStatCard(
          'Aylık Gelir',
          '${overview.totalRevenueMonth.toStringAsFixed(0)} ₺',
          Icons.trending_up,
          Colors.purple,
        ),
        _buildStatCard(
          'Günlük Mesaj',
          '${overview.totalMessagesToday}',
          Icons.message,
          Colors.teal,
        ),
        _buildStatCard(
          'Aktif Abonelik',
          '${overview.activeSubscriptions}',
          Icons.card_membership,
          Colors.indigo,
        ),
        _buildStatCard(
          'Sistem Uptime',
          '${overview.systemUptime}%',
          Icons.health_and_safety,
          overview.systemUptime > 99 ? Colors.green : Colors.red,
        ),
        _buildStatCard(
          'Sunucu Durumu',
          overview.serverStatus,
          Icons.dns,
          overview.serverStatus == 'healthy' ? Colors.green : Colors.red,
        ),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 30),
            const SizedBox(height: 10),
            Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              title,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformersGrid(List<PerformerStats> performers) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        childAspectRatio: 1.2,
        crossAxisSpacing: 15,
        mainAxisSpacing: 15,
      ),
      itemCount: performers.length,
      itemBuilder: (context, index) {
        final performer = performers[index];
        return _buildPerformerCard(performer);
      },
    );
  }

  Widget _buildPerformerCard(PerformerStats performer) {
    Color statusColor;
    switch (performer.status) {
      case 'active':
        statusColor = Colors.green;
        break;
      case 'banned':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    performer.performerName,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    performer.status.toUpperCase(),
                    style: TextStyle(
                      color: statusColor,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 15),
            _buildPerformerStat('Günlük Mesaj', '${performer.messagesToday}'),
            _buildPerformerStat('Toplam Mesaj', '${performer.totalMessages}'),
            _buildPerformerStat('Yanıt Süresi', '${performer.responseTimeAvg.toStringAsFixed(1)}s'),
            _buildPerformerStat('Günlük Kazanç', '${performer.earningsToday.toStringAsFixed(0)} ₺'),
            _buildPerformerStat('Engagement', '${performer.engagementRate.toStringAsFixed(1)}%'),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformerStat(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformersContent() {
    return Consumer(
      builder: (context, ref, child) {
        final performersAsync = ref.watch(performerStatsProvider);
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Şovcu Yönetimi',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              performersAsync.when(
                data: (performers) => _buildDetailedPerformersTable(performers),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => const Center(
                  child: Text('Şovcu verileri yüklenemedi', style: TextStyle(color: Colors.red)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDetailedPerformersTable(List<PerformerStats> performers) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(15),
            decoration: const BoxDecoration(
              color: Color(0xFF2A2A3E),
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(15),
                topRight: Radius.circular(15),
              ),
            ),
            child: const Row(
              children: [
                Expanded(flex: 2, child: Text('Şovcu', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Durum', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Günlük Mesaj', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Toplam Mesaj', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Yanıt Süresi', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Günlük Kazanç', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('Engagement', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
                Expanded(child: Text('İşlemler', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold))),
              ],
            ),
          ),
          // Data rows
          ...performers.map((performer) => _buildPerformerRow(performer)),
        ],
      ),
    );
  }

  Widget _buildPerformerRow(PerformerStats performer) {
    Color statusColor;
    switch (performer.status) {
      case 'active':
        statusColor = Colors.green;
        break;
      case 'banned':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.all(15),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.grey, width: 0.2)),
      ),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              performer.performerName,
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                performer.status.toUpperCase(),
                style: TextStyle(
                  color: statusColor,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          Expanded(
            child: Text(
              '${performer.messagesToday}',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Text(
              '${performer.totalMessages}',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Text(
              '${performer.responseTimeAvg.toStringAsFixed(1)}s',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Text(
              '${performer.earningsToday.toStringAsFixed(0)} ₺',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Text(
              '${performer.engagementRate.toStringAsFixed(1)}%',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          Expanded(
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, color: Colors.blue, size: 18),
                  onPressed: () {
                    // Edit performer
                  },
                ),
                IconButton(
                  icon: Icon(
                    performer.status == 'active' ? Icons.pause : Icons.play_arrow,
                    color: performer.status == 'active' ? Colors.orange : Colors.green,
                    size: 18,
                  ),
                  onPressed: () {
                    // Toggle performer status
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.analytics, color: Colors.purple, size: 18),
                  onPressed: () {
                    // View detailed analytics
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsContent() {
    return Consumer(
      builder: (context, ref, child) {
        final analyticsAsync = ref.watch(analyticsProvider);
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Analitik Dashboard',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              analyticsAsync.when(
                data: (analytics) => _buildAnalyticsCharts(analytics),
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, stack) => const Center(
                  child: Text('Analitik verileri yüklenemedi', style: TextStyle(color: Colors.red)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAnalyticsCharts(List<AnalyticsData> analytics) {
    return Column(
      children: [
        // Revenue Chart
        Container(
          height: 300,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF1A1A2E),
            borderRadius: BorderRadius.circular(15),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Günlük Gelir Trendi',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Expanded(
                child: LineChart(
                  LineChartData(
                    gridData: FlGridData(show: false),
                    titlesData: FlTitlesData(show: false),
                    borderData: FlBorderData(show: false),
                    lineBarsData: [
                      LineChartBarData(
                        spots: analytics.asMap().entries.map((entry) {
                          return FlSpot(entry.key.toDouble(), entry.value.revenue);
                        }).toList(),
                        isCurved: true,
                        color: Colors.blue,
                        barWidth: 3,
                        belowBarData: BarAreaData(
                          show: true,
                          color: Colors.blue.withOpacity(0.1),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        // Messages Chart
        Container(
          height: 300,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF1A1A2E),
            borderRadius: BorderRadius.circular(15),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Günlük Mesaj Sayısı',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Expanded(
                child: BarChart(
                  BarChartData(
                    gridData: FlGridData(show: false),
                    titlesData: FlTitlesData(show: false),
                    borderData: FlBorderData(show: false),
                    barGroups: analytics.asMap().entries.map((entry) {
                      return BarChartGroupData(
                        x: entry.key,
                        barRods: [
                          BarChartRodData(
                            toY: entry.value.totalMessages.toDouble(),
                            color: Colors.green,
                            width: 15,
                            borderRadius: BorderRadius.circular(5),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPaymentsContent() {
    return const Center(
      child: Text(
        'Ödeme takip sistemi yakında...',
        style: TextStyle(color: Colors.white, fontSize: 18),
      ),
    );
  }

  Widget _buildLicensesContent() {
    return const Center(
      child: Text(
        'Lisans yönetimi yakında...',
        style: TextStyle(color: Colors.white, fontSize: 18),
      ),
    );
  }

  Widget _buildSettingsContent() {
    return const Center(
      child: Text(
        'Ayarlar yakında...',
        style: TextStyle(color: Colors.white, fontSize: 18),
      ),
    );
  }
} 