import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/stats_model.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/stat_card.dart';
import '../../shared/widgets/chart_card.dart';
import 'bot_management_screen.dart';
import 'message_monitor_screen.dart';
import 'revenue_screen.dart';

class AdminDashboardScreen extends ConsumerStatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  ConsumerState<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends ConsumerState<AdminDashboardScreen> {
  final _apiService = ApiService();
  StatsModel? _stats;
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      setState(() => _isLoading = true);
      final stats = await _apiService.getStats();
      setState(() {
        _stats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'İstatistikler yüklenirken hata oluştu: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error.isNotEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_error, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadStats,
              child: const Text('Yeniden Dene'),
            ),
          ],
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Paneli'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadStats,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Üst İstatistik Kartları
            Row(
              children: [
                Expanded(
                  child: StatCard(
                    title: 'Toplam Mesaj',
                    value: _stats?.totalMessages.toString() ?? '0',
                    icon: Icons.message,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: StatCard(
                    title: 'Aktif Kullanıcı',
                    value: _stats?.activeUsers.toString() ?? '0',
                    icon: Icons.people,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: StatCard(
                    title: 'Ortalama AI Puanı',
                    value: (_stats?.averageAiRating ?? 0).toStringAsFixed(2),
                    icon: Icons.psychology,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Grafik Kartları
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: ChartCard(
                    title: 'Günlük Mesaj İstatistikleri',
                    data: _stats?.dailyStats ?? [],
                    dataKey: 'messageCount',
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ChartCard(
                    title: 'Gelir Dağılımı',
                    data: _stats?.revenueBySource.entries.toList() ?? [],
                    dataKey: 'value',
                    color: Colors.green,
                    isDonut: true,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Yönetim Kartları
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 3,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              children: [
                _buildManagementCard(
                  'Bot Yönetimi',
                  Icons.smart_toy,
                  () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const BotManagementScreen(),
                    ),
                  ),
                ),
                _buildManagementCard(
                  'Mesaj İzleme',
                  Icons.message,
                  () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const MessageMonitorScreen(),
                    ),
                  ),
                ),
                _buildManagementCard(
                  'Gelir Takibi',
                  Icons.monetization_on,
                  () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const RevenueScreen(),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildManagementCard(String title, IconData icon, VoidCallback onTap) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48),
              const SizedBox(height: 16),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 