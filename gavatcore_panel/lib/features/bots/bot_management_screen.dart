import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/services/api_service.dart';
import '../../core/providers/auth_provider.dart';

class BotManagementScreen extends ConsumerStatefulWidget {
  const BotManagementScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<BotManagementScreen> createState() => _BotManagementScreenState();
}

class _BotManagementScreenState extends ConsumerState<BotManagementScreen> {
  List<BotInstance> _bots = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadUserBots();
  }

  Future<void> _loadUserBots() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final apiService = ref.read(saasApiServiceProvider);
      final bots = await apiService.getUserBots();
      
      setState(() {
        _bots = bots;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Bot listesi yüklenemedi: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _createBot() async {
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => _CreateBotDialog(),
    );

    if (result != null) {
      try {
        final apiService = ref.read(saasApiServiceProvider);
        await apiService.createBot(
          personality: result['personality'],
          phoneNumber: result['phone_number'],
        );
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bot başarıyla oluşturuldu!'),
            backgroundColor: Colors.green,
          ),
        );
        
        _loadUserBots(); // Refresh list
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Bot oluşturma hatası: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _startBot(int botId) async {
    try {
      final apiService = ref.read(saasApiServiceProvider);
      await apiService.startBot(botId);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Bot başlatıldı!'),
          backgroundColor: Colors.green,
        ),
      );
      
      _loadUserBots();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Bot başlatma hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _stopBot(int botId) async {
    try {
      final apiService = ref.read(saasApiServiceProvider);
      await apiService.stopBot(botId);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Bot durduruldu!'),
          backgroundColor: Colors.orange,
        ),
      );
      
      _loadUserBots();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Bot durdurma hatası: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _deleteBot(int botId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Bot Silme'),
        content: const Text('Bu botu silmek istediğinizden emin misiniz?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Sil'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        final apiService = ref.read(saasApiServiceProvider);
        await apiService.deleteBot(botId);
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bot silindi!'),
            backgroundColor: Colors.red,
          ),
        );
        
        _loadUserBots();
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Bot silme hatası: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text(
          '🤖 Bot Yönetimi',
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            onPressed: _loadUserBots,
            icon: const Icon(Icons.refresh, color: Colors.white),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Colors.purple),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error, color: Colors.red, size: 48),
                      const SizedBox(height: 16),
                      Text(
                        _error!,
                        style: const TextStyle(color: Colors.white),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadUserBots,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.purple,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('Tekrar Dene'),
                      ),
                    ],
                  ),
                )
              : _bots.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.smart_toy, color: Colors.grey, size: 64),
                          const SizedBox(height: 16),
                          const Text(
                            'Henüz hiç botunuz yok',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                            ),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _createBot,
                            icon: const Icon(Icons.add),
                            label: const Text('İlk Botunuzu Oluşturun'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.purple,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 24,
                                vertical: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _bots.length,
                      itemBuilder: (context, index) {
                        final bot = _bots[index];
                        return _BotCard(
                          bot: bot,
                          onStart: () => _startBot(bot.id),
                          onStop: () => _stopBot(bot.id),
                          onDelete: () => _deleteBot(bot.id),
                        );
                      },
                    ),
      floatingActionButton: _bots.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: _createBot,
              backgroundColor: Colors.purple,
              icon: const Icon(Icons.add, color: Colors.white),
              label: const Text(
                'Yeni Bot',
                style: TextStyle(color: Colors.white),
              ),
            )
          : null,
    );
  }
}

class _BotCard extends StatelessWidget {
  final BotInstance bot;
  final VoidCallback onStart;
  final VoidCallback onStop;
  final VoidCallback onDelete;

  const _BotCard({
    Key? key,
    required this.bot,
    required this.onStart,
    required this.onStop,
    required this.onDelete,
  }) : super(key: key);

  String _getPersonalityEmoji(String personality) {
    switch (personality) {
      case 'gawatbaba':
        return '👨‍💼';
      case 'yayincilara':
        return '🎮';
      case 'xxxgeisha':
        return '💃';
      default:
        return '🤖';
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'active':
        return Colors.green;
      case 'creating':
        return Colors.orange;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purple.withOpacity(0.1),
            Colors.blue.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.purple.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(
                  _getPersonalityEmoji(bot.personality),
                  style: const TextStyle(fontSize: 24),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        bot.botName,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        bot.personality.toUpperCase(),
                        style: TextStyle(
                          color: Colors.grey[400],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getStatusColor(bot.sessionStatus),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    bot.isActive ? 'AKTIF' : 'PASIF',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Stats
            Row(
              children: [
                _StatItem(
                  icon: Icons.send,
                  label: 'Gönderilen',
                  value: bot.messagesSent.toString(),
                ),
                const SizedBox(width: 24),
                _StatItem(
                  icon: Icons.inbox,
                  label: 'Alınan',
                  value: bot.messagesReceived.toString(),
                ),
                const SizedBox(width: 24),
                _StatItem(
                  icon: Icons.monetization_on,
                  label: 'Coin',
                  value: bot.coinsUsed.toString(),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Actions
            Row(
              children: [
                if (!bot.isActive) ...[
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: onStart,
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('Başlat'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ] else ...[
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: onStop,
                      icon: const Icon(Icons.pause),
                      label: const Text('Durdur'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
                const SizedBox(width: 12),
                IconButton(
                  onPressed: onDelete,
                  icon: const Icon(Icons.delete_forever),
                  color: Colors.red,
                  style: IconButton.styleFrom(
                    backgroundColor: Colors.red.withOpacity(0.1),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _StatItem({
    Key? key,
    required this.icon,
    required this.label,
    required this.value,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.purple, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[400],
            fontSize: 10,
          ),
        ),
      ],
    );
  }
}

class _CreateBotDialog extends StatefulWidget {
  @override
  State<_CreateBotDialog> createState() => _CreateBotDialogState();
}

class _CreateBotDialogState extends State<_CreateBotDialog> {
  String _selectedPersonality = 'yayincilara';
  final _phoneController = TextEditingController();

  final Map<String, Map<String, String>> _personalities = {
    'gawatbaba': {
      'name': 'GawatBaba',
      'emoji': '👨‍💼',
      'description': 'Sistem yöneticisi, coin kontrol'
    },
    'yayincilara': {
      'name': 'Yayıncı Lara',
      'emoji': '🎮',
      'description': 'Gaming persona, Türkçe-Rusça mix'
    },
    'xxxgeisha': {
      'name': 'XXX Geisha',
      'emoji': '💃',
      'description': 'Seductive AI, sophisticated responses'
    },
  };

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: Colors.grey[900],
      title: const Text(
        '🤖 Yeni Bot Oluştur',
        style: TextStyle(color: Colors.white),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Kişilik Seçin:',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ..._personalities.entries.map((entry) {
            final isSelected = _selectedPersonality == entry.key;
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              decoration: BoxDecoration(
                border: Border.all(
                  color: isSelected ? Colors.purple : Colors.grey,
                  width: 2,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListTile(
                leading: Text(
                  entry.value['emoji']!,
                  style: const TextStyle(fontSize: 24),
                ),
                title: Text(
                  entry.value['name']!,
                  style: TextStyle(
                    color: isSelected ? Colors.purple : Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                subtitle: Text(
                  entry.value['description']!,
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
                onTap: () {
                  setState(() {
                    _selectedPersonality = entry.key;
                  });
                },
              ),
            );
          }).toList(),
          
          const SizedBox(height: 16),
          
          const Text(
            'Telefon Numarası (Opsiyonel):',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _phoneController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: '+90XXXXXXXXXX',
              hintStyle: TextStyle(color: Colors.grey[400]),
              enabledBorder: OutlineInputBorder(
                borderSide: BorderSide(color: Colors.grey[600]!),
              ),
              focusedBorder: const OutlineInputBorder(
                borderSide: BorderSide(color: Colors.purple),
              ),
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('İptal'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop({
              'personality': _selectedPersonality,
              'phone_number': _phoneController.text.isEmpty 
                  ? null 
                  : _phoneController.text,
            });
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.purple,
            foregroundColor: Colors.white,
          ),
          child: const Text('Oluştur'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _phoneController.dispose();
    super.dispose();
  }
}

// Data Models
class BotInstance {
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

  BotInstance({
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

  factory BotInstance.fromJson(Map<String, dynamic> json) {
    return BotInstance(
      id: json['id'],
      botName: json['bot_name'],
      personality: json['personality'],
      replyMode: json['reply_mode'],
      sessionStatus: json['session_status'],
      isActive: json['is_active'],
      isOnline: json['is_online'],
      messagesSent: json['messages_sent'],
      messagesReceived: json['messages_received'],
      coinsUsed: json['coins_used'],
      createdAt: json['created_at'],
      uptimeSeconds: json['uptime_seconds'].toDouble(),
    );
  }
} 