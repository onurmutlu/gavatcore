import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../shared/themes/app_theme.dart';

class PerformerDashboard extends StatefulWidget {
  final String performerId;
  
  const PerformerDashboard({
    Key? key,
    required this.performerId,
  }) : super(key: key);

  @override
  State<PerformerDashboard> createState() => _PerformerDashboardState();
}

class _PerformerDashboardState extends State<PerformerDashboard> {
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _myBots = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMyBots();
  }

  Future<void> _loadMyBots() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Şimdilik tüm botları getir, normalde performer-specific olacak
      final response = await _apiService.getAllBots();
      setState(() {
        _myBots = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _controlBot(String botId, String action) async {
    try {
      bool success = false;
      String message = '';

      switch (action) {
        case 'start':
          final result = await _apiService.startSystem();
          success = result['success'] ?? false;
          message = 'Bot başlatıldı';
          break;
        case 'stop':
          final result = await _apiService.stopSystem();
          success = result['success'] ?? false;
          message = 'Bot durduruldu';
          break;
        case 'restart':
          final result = await _apiService.restartSystem();
          success = result['success'] ?? false;
          message = 'Bot yeniden başlatıldı';
          break;
      }

      if (success) {
        _showSnackbar(message, Colors.green);
        _loadMyBots();
      } else {
        _showSnackbar('İşlem başarısız', Colors.red);
      }
    } catch (e) {
      _showSnackbar('Hata: ${e.toString()}', Colors.red);
    }
  }

  void _showSnackbar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      appBar: AppBar(
        title: const Text(
          'Botlarım',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: AppTheme.primaryColor,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadMyBots,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: AppTheme.primaryColor),
            SizedBox(height: 16),
            Text(
              'Botlarınız yükleniyor...',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
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
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white.withOpacity(0.7)),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadMyBots,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
                foregroundColor: Colors.white,
              ),
              child: const Text('Tekrar Dene'),
            ),
          ],
        ),
      );
    }

    if (_myBots.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.smart_toy_outlined,
              size: 64,
              color: Colors.white.withOpacity(0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'Henüz botunuz yok',
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Adminle iletişime geçin',
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadMyBots,
      color: AppTheme.primaryColor,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Özet kartı
          _buildSummaryCard(),
          const SizedBox(height: 20),
          
          // Bot listesi
          const Text(
            'Bot Listesi',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          
          ...(_myBots.map((bot) => _buildBotCard(bot)).toList()),
        ],
      ),
    );
  }

  Widget _buildSummaryCard() {
    final runningBots = _myBots.where((bot) => bot['status'] == 'running').length;
    final totalBots = _myBots.length;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryColor.withOpacity(0.8),
            AppTheme.accentColor.withOpacity(0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(
                Icons.dashboard,
                color: Colors.white,
                size: 28,
              ),
              const SizedBox(width: 12),
              const Text(
                'Bot Özeti',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem(
                'Toplam Bot',
                totalBots.toString(),
                Icons.smart_toy,
              ),
              _buildSummaryItem(
                'Aktif Bot',
                runningBots.toString(),
                Icons.play_circle,
              ),
              _buildSummaryItem(
                'Durum',
                runningBots == totalBots ? 'İyi' : 'Uyarı',
                runningBots == totalBots ? Icons.check_circle : Icons.warning,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.white.withOpacity(0.9),
          size: 24,
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          title,
          style: TextStyle(
            color: Colors.white.withOpacity(0.8),
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildBotCard(Map<String, dynamic> bot) {
    final isRunning = bot['status'] == 'running';
    final statusColor = isRunning ? Colors.green : Colors.grey;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  Icons.smart_toy,
                  color: statusColor,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      bot['name'] ?? 'Bot',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: statusColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          isRunning ? 'Çalışıyor' : 'Durduruldu',
                          style: TextStyle(
                            color: statusColor,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              _buildBotActions(bot),
            ],
          ),
          
          if (isRunning && bot['users_count'] != null) ...[
            const SizedBox(height: 12),
            const Divider(color: Colors.white12),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildBotStat('Kullanıcı', '${bot['users_count']}', Icons.people),
                if (bot['messages_today'] != null)
                  _buildBotStat('Mesaj', '${bot['messages_today']}', Icons.message),
                _buildBotStat('Uptime', bot['last_activity'] ?? 'Bilinmiyor', Icons.timer),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildBotStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.white.withOpacity(0.6),
          size: 16,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.6),
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  Widget _buildBotActions(Map<String, dynamic> bot) {
    final isRunning = bot['status'] == 'running';
    final botId = bot['username'] ?? bot['bot_id'] ?? '';

    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert, color: Colors.white),
      color: AppTheme.cardColor,
      onSelected: (action) => _controlBot(botId, action),
      itemBuilder: (context) => [
        if (!isRunning)
          const PopupMenuItem(
            value: 'start',
            child: Row(
              children: [
                Icon(Icons.play_arrow, color: Colors.green, size: 20),
                SizedBox(width: 8),
                Text('Başlat', style: TextStyle(color: Colors.white)),
              ],
            ),
          ),
        if (isRunning) ...[
          const PopupMenuItem(
            value: 'stop',
            child: Row(
              children: [
                Icon(Icons.stop, color: Colors.red, size: 20),
                SizedBox(width: 8),
                Text('Durdur', style: TextStyle(color: Colors.white)),
              ],
            ),
          ),
          const PopupMenuItem(
            value: 'restart',
            child: Row(
              children: [
                Icon(Icons.refresh, color: Colors.orange, size: 20),
                SizedBox(width: 8),
                Text('Yeniden Başlat', style: TextStyle(color: Colors.white)),
              ],
            ),
          ),
        ],
        const PopupMenuItem(
          value: 'logs',
          child: Row(
            children: [
              Icon(Icons.list_alt, color: Colors.blue, size: 20),
              SizedBox(width: 8),
              Text('Logları Gör', style: TextStyle(color: Colors.white)),
            ],
          ),
        ),
      ],
    );
  }
} 