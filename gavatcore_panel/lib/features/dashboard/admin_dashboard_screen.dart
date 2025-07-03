import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/dashboard_provider.dart';
import '../../core/models/log_entry.dart';
import '../../shared/widgets/bot_status_card.dart';
import '../../shared/widgets/analytics_charts_section.dart';
import '../../shared/themes/app_theme.dart';
import '../../shared/widgets/system_health_chart.dart';
import '../../shared/widgets/power_mode_selector.dart';

// Riverpod provider
final dashboardProvider = ChangeNotifierProvider<DashboardProvider>((ref) {
  return DashboardProvider();
});

class AdminDashboardScreen extends ConsumerStatefulWidget {
  @override
  _AdminDashboardScreenState createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends ConsumerState<AdminDashboardScreen> {
  @override
  void initState() {
    super.initState();
    // Load dashboard data on init
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(dashboardProvider).loadDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('GavatCore Admin Panel'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () {
              ref.read(dashboardProvider).refreshData();
            },
          ),
        ],
      ),
      body: Consumer(
        builder: (context, ref, child) {
          final provider = ref.watch(dashboardProvider);
          
          if (provider.isLoading && provider.bots.isEmpty) {
            return _buildLoadingState();
          }

          if (provider.error != null) {
            return _buildErrorState(provider.error!);
          }

          return RefreshIndicator(
            onRefresh: provider.refreshData,
            child: SingleChildScrollView(
              physics: AlwaysScrollableScrollPhysics(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(provider),
                  _buildBotStatusGrid(provider),
                  _buildGlobalControls(provider),
                  _buildAnalyticsSection(provider),
                  _buildRevenueCard(provider),
                  _buildSystemHealthCard(provider),
                  _buildLogsSection(provider),
                  SizedBox(height: 60), // Bottom padding
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            color: Colors.deepPurple,
          ),
          SizedBox(height: 16),
          Text(
            'Dashboard yükleniyor...',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            SizedBox(height: 16),
            Text(
              'Hata Oluştu',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                ref.read(dashboardProvider).loadDashboardData();
              },
              child: Text('Tekrar Dene'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(DashboardProvider provider) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Colors.deepPurple, Colors.purple.shade300],
        ),
      ),
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Dashboard Özeti',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Aktif Botlar',
                    '${provider.runningBots}',
                    Icons.smart_toy,
                    Colors.green,
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Toplam Mesaj',
                    '${provider.totalMessages}',
                    Icons.message,
                    Colors.blue,
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard(
                    'Avg Uptime',
                    '${provider.avgUptime.toStringAsFixed(0)}dk',
                    Icons.access_time,
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

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 24,
          ),
          SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: Colors.white70,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildBotStatusGrid(DashboardProvider provider) {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Bot Durumları',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 16),
          GridView.builder(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: _getCrossAxisCount(context),
              childAspectRatio: 1.2,
              crossAxisSpacing: 8,
              mainAxisSpacing: 8,
            ),
            itemCount: provider.bots.length,
            itemBuilder: (context, index) {
              final bot = provider.bots[index];
              return BotStatusCard(
                bot: bot,
                isLoading: provider.isLoading,
                onStart: () => _handleBotAction(
                  () => provider.startBot(bot.id),
                  'Bot başlatılıyor...',
                ),
                onStop: () => _handleBotAction(
                  () => provider.stopBot(bot.id),
                  'Bot durduruluyor...',
                ),
                onRestart: () => _handleBotAction(
                  () => provider.restartBot(bot.id),
                  'Bot yeniden başlatılıyor...',
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildGlobalControls(DashboardProvider provider) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Global Kontroller',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: provider.isLoading
                          ? null
                          : () => _handleBotAction(
                                provider.startAllBots,
                                'Tüm botlar başlatılıyor...',
                              ),
                      icon: Icon(Icons.play_arrow),
                      label: Text('Tümünü Başlat'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: provider.isLoading
                          ? null
                          : () => _handleBotAction(
                                provider.stopAllBots,
                                'Tüm botlar durduruluyor...',
                              ),
                      icon: Icon(Icons.stop),
                      label: Text('Tümünü Durdur'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAnalyticsSection(DashboardProvider provider) {
    return AnalyticsChartsSection(
      analytics: provider.analytics,
    );
  }

  Widget _buildRevenueCard(DashboardProvider provider) {
    final revenue = provider.analytics?.revenue;
    if (revenue == null) return SizedBox();

    return Padding(
      padding: EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Kasa Akışı',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildRevenueItem(
                    'Günlük',
                    '${revenue.dailyRevenue.toStringAsFixed(2)} ${revenue.currency}',
                    Icons.today,
                    Colors.green,
                  ),
                  _buildRevenueItem(
                    'Haftalık',
                    '${revenue.weeklyRevenue.toStringAsFixed(2)} ${revenue.currency}',
                    Icons.date_range,
                    Colors.blue,
                  ),
                  _buildRevenueItem(
                    'Aylık',
                    '${revenue.monthlyRevenue.toStringAsFixed(2)} ${revenue.currency}',
                    Icons.calendar_month,
                    Colors.purple,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRevenueItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildSystemHealthCard(DashboardProvider provider) {
    final health = provider.systemHealth;
    if (health.isEmpty) return SizedBox();

    return Padding(
      padding: EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Sistem Sağlığı',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildHealthMetric(
                      'CPU',
                      '${health['cpu_usage']?.toStringAsFixed(1) ?? '0'}%',
                      health['cpu_usage']?.toDouble() ?? 0,
                    ),
                  ),
                  Expanded(
                    child: _buildHealthMetric(
                      'RAM',
                      '${health['memory_usage']?.toStringAsFixed(1) ?? '0'}%',
                      health['memory_usage']?.toDouble() ?? 0,
                    ),
                  ),
                  Expanded(
                    child: _buildHealthMetric(
                      'Disk',
                      '${health['disk_usage']?.toStringAsFixed(1) ?? '0'}%',
                      health['disk_usage']?.toDouble() ?? 0,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHealthMetric(String label, String value, double percentage) {
    Color color = Colors.green;
    if (percentage > 80) {
      color = Colors.red;
    } else if (percentage > 60) {
      color = Colors.orange;
    }

    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 12)),
        SizedBox(height: 4),
        LinearProgressIndicator(
          value: percentage / 100,
          color: color,
          backgroundColor: Colors.grey[300],
        ),
        SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildLogsSection(DashboardProvider provider) {
    if (provider.logs.isEmpty) return SizedBox();

    return Padding(
      padding: EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Son Aktiviteler',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              ...provider.logs.take(5).map((log) => _buildLogItem(log)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLogItem(LogEntry log) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(log.levelIcon),
          SizedBox(width: 8),
          Text(
            log.formattedTime,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[600],
            ),
          ),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              log.message,
              style: TextStyle(fontSize: 12),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  int _getCrossAxisCount(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width > 1200) return 3;
    if (width > 800) return 2;
    return 1;
  }

  Future<void> _handleBotAction(
    Future<bool> Function() action,
    String loadingMessage,
  ) async {
    try {
      // Show loading snackbar
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(loadingMessage),
          duration: Duration(seconds: 1),
        ),
      );

      final success = await action();

      // Show result
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            success ? 'İşlem başarılı!' : 'İşlem başarısız!',
          ),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
} 