import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../../../../core/storage/storage_service.dart';
import '../../../../core/services/api_service.dart';
import '../../../../shared/themes/app_theme.dart';

// Dashboard Page
class DashboardPage extends ConsumerStatefulWidget {
  const DashboardPage({Key? key}) : super(key: key);

  @override
  ConsumerState<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends ConsumerState<DashboardPage> {
  late ApiService _apiService;
  bool _isLoading = true;
  Map<String, dynamic>? _systemStatus;
  Map<String, dynamic>? _campaignStats;
  List<Map<String, dynamic>> _recentLogs = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(storage: StorageService.instance);
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final futures = await Future.wait([
        _apiService.getSystemStatus(),
        _apiService.getCampaignStats(),
        _apiService.getRecentLogs(),
      ]);

      setState(() {
        _systemStatus = futures[0] as Map<String, dynamic>;
        _campaignStats = futures[1] as Map<String, dynamic>;
        _recentLogs = futures[2] as List<Map<String, dynamic>>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _performSystemAction(String action) async {
    try {
      bool success = false;
      
      switch (action) {
        case 'start':
          final result = await _apiService.startSystem();
          success = result['success'] ?? false;
          break;
        case 'stop':
          final result = await _apiService.stopSystem();
          success = result['success'] ?? false;
          break;
      }

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Sistem ${action == 'start' ? 'başlatıldı' : 'durduruldu'}'),
            backgroundColor: Colors.green,
          ),
        );
        _loadDashboardData();
      } else {
        throw Exception('İşlem başarısız');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Hata: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.darkBg,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(color: AppTheme.primaryColor),
              SizedBox(height: 16),
              Text(
                'Gerçek veriler yükleniyor...',
                style: TextStyle(color: AppTheme.textColor, fontSize: 16),
              ),
            ],
          ),
        ),
      );
    }

    if (_error != null) {
      return Scaffold(
        backgroundColor: AppTheme.darkBg,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                'Bağlantı Hatası',
                style: const TextStyle(
                  color: AppTheme.textColor,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Backend API\'larını başlatın:\npython production_bot_api.py\npython xp_token_api.py',
                textAlign: TextAlign.center,
                style: const TextStyle(color: AppTheme.textColorSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadDashboardData,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Tekrar Dene'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.darkBg,
      body: RefreshIndicator(
        color: AppTheme.primaryColor,
        onRefresh: _loadDashboardData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    '🚀 GavatCore Admin Panel',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textColor,
                    ),
                  ),
                  IconButton(
                    onPressed: _loadDashboardData,
                    icon: const Icon(Icons.refresh, color: AppTheme.primaryColor),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // System Status Cards
              _buildSystemStatusCards(),
              const SizedBox(height: 24),

              // System Control
              _buildSystemControls(),
              const SizedBox(height: 24),

              // Campaign Stats
              if (_campaignStats != null) ...[
                _buildCampaignStats(),
                const SizedBox(height: 24),
              ],

              // Recent Activity
              _buildRecentActivity(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSystemStatusCards() {
    final bots = _systemStatus?['bots'] as Map<String, dynamic>? ?? {};
    final systemHealth = _systemStatus?['system_health'] ?? 'unknown';
    final uptime = _systemStatus?['uptime'] ?? 'Bilinmiyor';

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _buildStatusCard(
          'Sistem Durumu',
          systemHealth == 'healthy' ? 'Çevrimiçi' : 'Offline',
          systemHealth == 'healthy' ? Icons.check_circle : Icons.error,
          systemHealth == 'healthy' ? Colors.green : Colors.red,
        ),
        _buildStatusCard(
          'Aktif Botlar',
          '${bots.entries.where((e) => e.value['status'] == 'active').length}/${bots.length}',
          Icons.smart_toy,
          AppTheme.primaryColor,
        ),
        _buildStatusCard(
          'Çalışma Süresi',
          uptime,
          Icons.timer,
          AppTheme.secondaryColor,
        ),
        _buildStatusCard(
          'Toplam Bot',
          bots.length.toString(),
          Icons.dashboard,
          Colors.orange,
        ),
      ],
    );
  }

  Widget _buildStatusCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: AppTheme.textColorSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSystemControls() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '⚡ Sistem Kontrolleri',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _performSystemAction('start'),
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Sistemi Başlat'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _performSystemAction('stop'),
                  icon: const Icon(Icons.stop),
                  label: const Text('Sistemi Durdur'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCampaignStats() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📊 Kampanya İstatistikleri',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Bugünkü Aktivite: ${_campaignStats?['today_activity'] ?? 'Veri yok'}',
            style: const TextStyle(color: AppTheme.textColor),
          ),
          Text(
            'Toplam Mesaj: ${_campaignStats?['total_messages'] ?? 'Veri yok'}',
            style: const TextStyle(color: AppTheme.textColor),
          ),
          Text(
            'Başarı Oranı: ${_campaignStats?['success_rate'] ?? 'Veri yok'}%',
            style: const TextStyle(color: AppTheme.textColor),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📋 Son Aktiviteler',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
          const SizedBox(height: 16),
          if (_recentLogs.isEmpty)
            const Text(
              'Henüz aktivite kaydı yok',
              style: TextStyle(color: AppTheme.textColorSecondary),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _recentLogs.take(5).length,
              itemBuilder: (context, index) {
                final log = _recentLogs[index];
                return ListTile(
                  leading: Icon(
                    Icons.info_outline,
                    color: AppTheme.primaryColor,
                    size: 20,
                  ),
                  title: Text(
                    log['message'] ?? 'Aktivite',
                    style: const TextStyle(
                      color: AppTheme.textColor,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Text(
                    log['timestamp'] ?? 'Bilinmiyor',
                    style: const TextStyle(
                      color: AppTheme.textColorSecondary,
                      fontSize: 12,
                    ),
                  ),
                  dense: true,
                );
              },
            ),
        ],
      ),
    );
  }
} 