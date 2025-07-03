import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/models/bot_model.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/loading_view.dart';

class BotManagementScreen extends ConsumerStatefulWidget {
  const BotManagementScreen({super.key});

  @override
  ConsumerState<BotManagementScreen> createState() => _BotManagementScreenState();
}

class _BotManagementScreenState extends ConsumerState<BotManagementScreen> {
  final _apiService = ApiService();
  List<BotModel>? _bots;
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _loadBots();
  }

  Future<void> _loadBots() async {
    try {
      setState(() => _isLoading = true);
      final bots = await _apiService.getBots();
      setState(() {
        _bots = bots;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Botlar yüklenirken hata oluştu: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _updateBotStatus(BotModel bot, bool isActive) async {
    try {
      await _apiService.updateBot(bot.id, {'isActive': isActive});
      _loadBots(); // Listeyi yenile
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Bot durumu güncellenirken hata: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const LoadingView();
    }

    if (_error.isNotEmpty) {
      return ErrorView(
        error: _error,
        onRetry: _loadBots,
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bot Yönetimi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadBots,
          ),
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _bots?.length ?? 0,
        itemBuilder: (context, index) {
          final bot = _bots![index];
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: ExpansionTile(
              leading: Icon(
                Icons.smart_toy,
                color: bot.isActive ? Colors.green : Colors.grey,
              ),
              title: Text(bot.name),
              subtitle: Text(bot.username),
              trailing: Switch(
                value: bot.isActive,
                onChanged: (value) => _updateBotStatus(bot, value),
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Açıklama: ${bot.description}'),
                      const SizedBox(height: 8),
                      Text('Tip: ${bot.type.name}'),
                      const SizedBox(height: 8),
                      Text('Rol: ${bot.role.name}'),
                      const SizedBox(height: 16),
                      const Text(
                        'İstatistikler',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildStatRow('Toplam Mesaj', bot.stats.totalMessages),
                      _buildStatRow('Aktif Kullanıcı', bot.stats.activeUsers),
                      _buildStatRow(
                        'Ortalama Yanıt Süresi',
                        '${bot.stats.averageResponseTime.toStringAsFixed(2)}s',
                      ),
                      _buildStatRow(
                        'AI Puanı',
                        bot.stats.aiRating.toStringAsFixed(2),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: () {
                              // TODO: Bot ayarları düzenleme
                            },
                            child: const Text('Ayarları Düzenle'),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            onPressed: () {
                              // TODO: Bot detay sayfasına git
                            },
                            child: const Text('Detayları Görüntüle'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // TODO: Yeni bot ekleme
        },
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildStatRow(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value.toString(),
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
} 