import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../shared/themes/app_theme.dart';

// Real-time Bot Status Page
class RealtimeBotStatusPage extends ConsumerStatefulWidget {
  const RealtimeBotStatusPage({Key? key}) : super(key: key);

  @override
  ConsumerState<RealtimeBotStatusPage> createState() => _RealtimeBotStatusPageState();
}

class _RealtimeBotStatusPageState extends ConsumerState<RealtimeBotStatusPage> {
  List<BotStatusModel> _bots = [];
  bool _isLoading = true;
  String? _error;
  Timer? _refreshTimer;
  
  static const String apiBaseUrl = 'http://localhost:8000/api';
  static const Duration refreshInterval = Duration(seconds: 5);

  @override
  void initState() {
    super.initState();
    _loadBotStatuses();
    _startPeriodicRefresh();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  void _startPeriodicRefresh() {
    _refreshTimer = Timer.periodic(refreshInterval, (timer) {
      if (mounted) {
        _loadBotStatuses(showLoading: false);
      }
    });
  }

  Future<void> _loadBotStatuses({bool showLoading = true}) async {
    if (showLoading) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      // Try demo bots first (no auth required)
      final response = await http.get(
        Uri.parse('$apiBaseUrl/bots/demo'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        List<BotStatusModel> bots = [];
        
        if (data is List) {
          bots = data.map((bot) => BotStatusModel.fromJson(bot)).toList();
        }

        if (mounted) {
          setState(() {
            _bots = bots;
            _isLoading = false;
            _error = null;
          });
        }
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'API bağlantısı başarısız: $e';
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _controlBot(int botId, String action) async {
    try {
      final response = await http.post(
        Uri.parse('$apiBaseUrl/bots/$botId/$action'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Bot $action işlemi başarılı!'),
              backgroundColor: Colors.green,
            ),
          );
          // Immediate refresh after action
          await _loadBotStatuses(showLoading: false);
        } else {
          throw Exception(data['message'] ?? 'İşlem başarısız');
        }
      } else {
        throw Exception('HTTP ${response.statusCode}');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('$action işlemi başarısız: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: const Text(
          '🤖 Gerçek Zamanlı Bot Durumları',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: const Color(0xFF6366F1),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: () => _loadBotStatuses(),
            tooltip: 'Yenile',
          ),
          Container(
            margin: const EdgeInsets.only(right: 16),
            child: Chip(
              label: Text(
                'Auto: ${refreshInterval.inSeconds}s',
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
              backgroundColor: Colors.green.withOpacity(0.8),
              side: BorderSide.none,
            ),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _bots.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Color(0xFF6366F1)),
            SizedBox(height: 16),
            Text(
              'Bot durumları yükleniyor...',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    if (_error != null && _bots.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Hata: $_error',
              style: const TextStyle(fontSize: 16, color: Colors.red),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => _loadBotStatuses(),
              icon: const Icon(Icons.refresh),
              label: const Text('Tekrar Dene'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6366F1),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadBotStatuses(),
      color: const Color(0xFF6366F1),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatsHeader(),
            const SizedBox(height: 20),
            _buildBotList(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsHeader() {
    final activeBots = _bots.where((bot) => bot.isActive).length;
    final onlineBots = _bots.where((bot) => bot.isOnline).length;
    final totalMessages = _bots.fold<int>(0, (sum, bot) => sum + bot.messagesSent);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF6366F1).withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Bot Sistem Özeti',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  'Toplam Bot',
                  '${_bots.length}',
                  Icons.smart_toy,
                  Colors.white,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  'Aktif',
                  '$activeBots',
                  Icons.play_circle,
                  Colors.lightGreenAccent,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  'Online',
                  '$onlineBots',
                  Icons.wifi,
                  Colors.cyanAccent,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  'Mesajlar',
                  '$totalMessages',
                  Icons.message,
                  Colors.yellowAccent,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color iconColor) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Icon(icon, color: iconColor, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBotList() {
    if (_bots.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Text(
            'Henüz bot bulunamadı',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Bot Listesi',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF6366F1),
          ),
        ),
        const SizedBox(height: 16),
        ...(_bots.map((bot) => _buildBotCard(bot))),
      ],
    );
  }

  Widget _buildBotCard(BotStatusModel bot) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
        border: Border.all(
          color: bot.isActive 
              ? Colors.green.withOpacity(0.3)
              : Colors.grey.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              CircleAvatar(
                radius: 24,
                backgroundColor: _getPersonalityColor(bot.personality),
                child: Text(
                  _getPersonalityIcon(bot.personality),
                  style: const TextStyle(fontSize: 18),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          bot.botName,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF6366F1),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: bot.isOnline ? Colors.green : Colors.grey,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            bot.isOnline ? 'ONLİNE' : 'OFFLİNE',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    Text(
                      '${bot.personality} • ${bot.replyMode}',
                      style: const TextStyle(
                        color: Colors.grey,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              _buildStatusIndicator(bot),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Stats
          Row(
            children: [
              Expanded(
                child: _buildInfoItem(
                  Icons.send,
                  'Gönderilen',
                  '${bot.messagesSent}',
                  Colors.blue,
                ),
              ),
              Expanded(
                child: _buildInfoItem(
                  Icons.inbox,
                  'Alınan',
                  '${bot.messagesReceived}',
                  Colors.green,
                ),
              ),
              Expanded(
                child: _buildInfoItem(
                  Icons.monetization_on,
                  'Coin',
                  '${bot.coinsUsed}',
                  Colors.orange,
                ),
              ),
              Expanded(
                child: _buildInfoItem(
                  Icons.timer,
                  'Uptime',
                  _formatUptime(bot.uptimeSeconds),
                  Colors.purple,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Controls
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: bot.isActive 
                      ? null 
                      : () => _controlBot(bot.id, 'start'),
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Başlat'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: !bot.isActive 
                      ? null 
                      : () => _controlBot(bot.id, 'stop'),
                  icon: const Icon(Icons.stop),
                  label: const Text('Durdur'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: Colors.grey,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _controlBot(bot.id, 'restart'),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Yeniden'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIndicator(BotStatusModel bot) {
    String status;
    Color color;
    IconData icon;

    if (bot.isActive && bot.isOnline) {
      status = 'ÇALIŞIYOR';
      color = Colors.green;
      icon = Icons.check_circle;
    } else if (bot.isActive && !bot.isOnline) {
      status = 'BAĞLANIYOR';
      color = Colors.orange;
      icon = Icons.sync;
    } else {
      status = 'DURDURULDU';
      color = Colors.grey;
      icon = Icons.pause_circle;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 16),
          const SizedBox(width: 4),
          Text(
            status,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String label, String value, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Color _getPersonalityColor(String personality) {
    switch (personality.toLowerCase()) {
      case 'gawatbaba':
      case 'babagavat':
        return Colors.deepOrange;
      case 'yayincilara':
        return Colors.pink;
      case 'xxxgeisha':
        return Colors.purple;
      default:
        return const Color(0xFF6366F1);
    }
  }

  String _getPersonalityIcon(String personality) {
    switch (personality.toLowerCase()) {
      case 'gawatbaba':
      case 'babagavat':
        return '🔥';
      case 'yayincilara':
        return '💃';
      case 'xxxgeisha':
        return '💋';
      default:
        return '🤖';
    }
  }

  String _formatUptime(double seconds) {
    if (seconds < 60) {
      return '${seconds.toInt()}s';
    } else if (seconds < 3600) {
      return '${(seconds / 60).toInt()}m';
    } else if (seconds < 86400) {
      return '${(seconds / 3600).toStringAsFixed(1)}h';
    } else {
      return '${(seconds / 86400).toStringAsFixed(1)}d';
    }
  }
}

// Bot Status Model
class BotStatusModel {
  final int id;
  final String botName;
  final String personality;
  final String replyMode;
  final String sessionStatus;
  final bool isActive;
  final bool isOnline;
  final int messagesSent;
  final int messagesReceived;
  final int coinsUsed;
  final String createdAt;
  final double uptimeSeconds;

  BotStatusModel({
    required this.id,
    required this.botName,
    required this.personality,
    required this.replyMode,
    required this.sessionStatus,
    required this.isActive,
    required this.isOnline,
    required this.messagesSent,
    required this.messagesReceived,
    required this.coinsUsed,
    required this.createdAt,
    required this.uptimeSeconds,
  });

  factory BotStatusModel.fromJson(Map<String, dynamic> json) {
    return BotStatusModel(
      id: json['id'] ?? 0,
      botName: json['bot_name'] ?? 'Unknown',
      personality: json['personality'] ?? 'unknown',
      replyMode: json['reply_mode'] ?? 'manual',
      sessionStatus: json['session_status'] ?? 'pending',
      isActive: json['is_active'] ?? false,
      isOnline: json['is_online'] ?? false,
      messagesSent: json['messages_sent'] ?? 0,
      messagesReceived: json['messages_received'] ?? 0,
      coinsUsed: json['coins_used'] ?? 0,
      createdAt: json['created_at'] ?? '',
      uptimeSeconds: (json['uptime_seconds'] ?? 0).toDouble(),
    );
  }
} 