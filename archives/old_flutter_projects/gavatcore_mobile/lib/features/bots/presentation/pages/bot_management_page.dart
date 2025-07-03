import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../../../../core/storage/storage_service.dart';
import '../../../../core/services/api_service.dart';
import '../../../../shared/themes/app_theme.dart';

// Bot Management Page
class BotManagementPage extends ConsumerStatefulWidget {
  const BotManagementPage({Key? key}) : super(key: key);

  @override
  ConsumerState<BotManagementPage> createState() => _BotManagementPageState();
}

class _BotManagementPageState extends ConsumerState<BotManagementPage> {
  late ApiService _apiService;
  bool _isLoading = true;
  Map<String, dynamic> _botStatus = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(storage: StorageService.instance);
    _loadBotData();
  }

  Future<void> _loadBotData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final systemStatus = await _apiService.getSystemStatus();
      setState(() {
        _botStatus = systemStatus['bots'] ?? {};
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _restartBot(String botUsername) async {
    try {
      final success = await _apiService.restartBot(botUsername);
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$botUsername yeniden başlatıldı'),
            backgroundColor: Colors.green,
          ),
        );
        _loadBotData();
      } else {
        throw Exception('Bot yeniden başlatılamadı');
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
                'Bot durumları yükleniyor...',
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
              const Text(
                'Bağlantı Hatası',
                style: TextStyle(
                  color: AppTheme.textColor,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'production_bot_api.py dosyasını çalıştırın',
                textAlign: TextAlign.center,
                style: TextStyle(color: AppTheme.textColorSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadBotData,
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
        onRefresh: _loadBotData,
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
                    '🤖 Bot Yönetimi',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textColor,
                    ),
                  ),
                  IconButton(
                    onPressed: _loadBotData,
                    icon: const Icon(Icons.refresh, color: AppTheme.primaryColor),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Bot Status Overview
              _buildBotOverview(),
              const SizedBox(height: 24),

              // Bot List
              if (_botStatus.isEmpty)
                _buildEmptyState()
              else
                _buildBotList(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBotOverview() {
    final totalBots = _botStatus.length;
    final activeBots = _botStatus.entries
        .where((entry) => entry.value['status'] == 'active')
        .length;
    final offlineBots = totalBots - activeBots;

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
            '📊 Bot Durumu Özeti',
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
                child: _buildOverviewCard(
                  'Toplam Bot',
                  totalBots.toString(),
                  Icons.smart_toy,
                  AppTheme.primaryColor,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildOverviewCard(
                  'Aktif',
                  activeBots.toString(),
                  Icons.check_circle,
                  Colors.green,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildOverviewCard(
                  'Offline',
                  offlineBots.toString(),
                  Icons.error,
                  Colors.red,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
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
          ),
        ],
      ),
    );
  }

  Widget _buildBotList() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '🎯 Aktif Botlar',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppTheme.textColor,
          ),
        ),
        const SizedBox(height: 16),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _botStatus.length,
          itemBuilder: (context, index) {
            final entry = _botStatus.entries.elementAt(index);
            final botName = entry.key;
            final botData = entry.value;
            
            return _buildBotCard(botName, botData);
          },
        ),
      ],
    );
  }

  Widget _buildBotCard(String botName, Map<String, dynamic> botData) {
    final status = botData['status'] ?? 'unknown';
    final isActive = status == 'active';
    final displayName = botData['display_name'] ?? botName;
    final lastActivity = botData['last_activity'] ?? 'Bilinmiyor';
    final messagesSent = botData['messages_sent'] ?? 0;
    final uptime = botData['uptime'] ?? 'Bilinmiyor';

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isActive ? Colors.green.withOpacity(0.3) : Colors.red.withOpacity(0.3),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Bot Header
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: isActive ? Colors.green : Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                displayName,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColor,
                ),
              ),
              const Spacer(),
              PopupMenuButton(
                icon: const Icon(Icons.more_vert, color: AppTheme.textColorSecondary),
                color: AppTheme.cardBg,
                itemBuilder: (context) => [
                  PopupMenuItem(
                    onTap: () => _restartBot(botName),
                    child: const Row(
                      children: [
                        Icon(Icons.restart_alt, color: AppTheme.primaryColor),
                        SizedBox(width: 8),
                        Text('Yeniden Başlat', style: TextStyle(color: AppTheme.textColor)),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Bot Stats
          Row(
            children: [
              Expanded(
                child: _buildStatItem('Durum', status.toUpperCase(), 
                  isActive ? Colors.green : Colors.red),
              ),
              Expanded(
                child: _buildStatItem('Mesaj', messagesSent.toString(), 
                  AppTheme.primaryColor),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _buildStatItem('Çalışma Süresi', uptime, 
                  AppTheme.secondaryColor),
              ),
              Expanded(
                child: _buildStatItem('Son Aktivite', lastActivity, 
                  AppTheme.textColorSecondary),
              ),
            ],
          ),

          // Action Buttons
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _restartBot(botName),
                  icon: const Icon(Icons.restart_alt, size: 18),
                  label: const Text('Yeniden Başlat'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    // Show bot details dialog
                    _showBotDetails(botName, botData);
                  },
                  icon: const Icon(Icons.info_outline, size: 18),
                  label: const Text('Detaylar'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.primaryColor,
                    side: const BorderSide(color: AppTheme.primaryColor),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: AppTheme.textColorSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: AppTheme.cardBg,
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Center(
        child: Column(
          children: [
            Icon(
              Icons.smart_toy_outlined,
              size: 64,
              color: AppTheme.textColorSecondary,
            ),
            SizedBox(height: 16),
            Text(
              'Henüz bot bulunamadı',
              style: TextStyle(
                fontSize: 18,
                color: AppTheme.textColor,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Backend API\'sini başlatarak botları görüntüleyebilirsiniz',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppTheme.textColorSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showBotDetails(String botName, Map<String, dynamic> botData) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardBg,
        title: Text(
          '$botName Detayları',
          style: const TextStyle(color: AppTheme.textColor),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('Kullanıcı Adı', botName),
            _buildDetailRow('Durum', botData['status'] ?? 'Bilinmiyor'),
            _buildDetailRow('Görünen Ad', botData['display_name'] ?? 'Bilinmiyor'),
            _buildDetailRow('Son Aktivite', botData['last_activity'] ?? 'Bilinmiyor'),
            _buildDetailRow('Gönderilen Mesaj', '${botData['messages_sent'] ?? 0}'),
            _buildDetailRow('Çalışma Süresi', botData['uptime'] ?? 'Bilinmiyor'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Kapat', style: TextStyle(color: AppTheme.primaryColor)),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(
                color: AppTheme.textColorSecondary,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(color: AppTheme.textColor),
            ),
          ),
        ],
      ),
    );
  }
} 