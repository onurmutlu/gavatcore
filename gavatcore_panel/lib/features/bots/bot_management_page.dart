import 'package:flutter/material.dart';
import '../../core/models/bot.dart';
import '../../shared/themes/app_theme.dart';

class BotManagementPage extends StatefulWidget {
  const BotManagementPage({super.key});

  @override
  State<BotManagementPage> createState() => _BotManagementPageState();
}

class _BotManagementPageState extends State<BotManagementPage> {
  final List<Bot> _bots = [
    Bot(
      id: '1',
      name: 'Lara',
      username: 'yayincilara',
      isActive: true,
      messageCount: 2847,
      userCount: 156,
      lastActivity: DateTime.now().subtract(const Duration(minutes: 5)),
    ),
    Bot(
      id: '2',
      name: 'BabaGavat',
      username: 'babagavat',
      isActive: true,
      messageCount: 1923,
      userCount: 89,
      lastActivity: DateTime.now().subtract(const Duration(minutes: 12)),
    ),
    Bot(
      id: '3',
      name: 'Geisha',
      username: 'xxxgeisha',
      isActive: false,
      messageCount: 3102,
      userCount: 234,
      lastActivity: DateTime.now().subtract(const Duration(hours: 2)),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.dark().colorScheme.surface,
      appBar: AppBar(
        title: const Text('Bot Yönetimi'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _addNewBot,
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _bots.length,
        itemBuilder: (context, index) {
          final bot = _bots[index];
          return Card(
            color: Colors.grey[900],
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: bot.isActive ? Colors.green : Colors.red,
                child: Text(
                  bot.name[0],
                  style: const TextStyle(color: Colors.white),
                ),
              ),
              title: Text(
                bot.name,
                style: const TextStyle(color: Colors.white),
              ),
              subtitle: Text(
                '@${bot.username} • ${bot.messageCount} mesaj • ${bot.userCount} kullanıcı',
                style: const TextStyle(color: Colors.white60),
              ),
              trailing: Switch(
                value: bot.isActive,
                onChanged: (value) => _toggleBot(index, value),
              ),
              onTap: () => _showBotDetails(bot),
            ),
          );
        },
      ),
    );
  }

  void _toggleBot(int index, bool isActive) {
    setState(() {
      _bots[index] = _bots[index].copyWith(isActive: isActive);
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '${_bots[index].name} ${isActive ? 'aktif edildi' : 'durduruldu'}',
        ),
      ),
    );
  }

  void _addNewBot() {
    // Show add bot dialog
    showDialog(
      context: context,
      builder: (context) => const AlertDialog(
        title: Text('Yeni Bot Ekle'),
        content: Text('Bu özellik yakında eklenecek.'),
      ),
    );
  }

  void _showBotDetails(Bot bot) {
    // Show bot details
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(bot.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Kullanıcı adı: @${bot.username}'),
            Text('Durum: ${bot.isActive ? 'Aktif' : 'Pasif'}'),
            Text('Mesaj sayısı: ${bot.messageCount}'),
            Text('Kullanıcı sayısı: ${bot.userCount}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Kapat'),
          ),
        ],
      ),
    );
  }
} 