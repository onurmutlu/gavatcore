import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/storage/storage_service.dart';
import '../../shared/themes/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../core/storage/storage_service.dart';
import '../../shared/themes/app_colors.dart';
import '../../shared/widgets/loading_overlay.dart';
import 'package:package_info_plus/package_info_plus.dart';

// Providers
final systemHealthProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getSystemHealth();
});

final systemStatusProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getSystemStatus();
});

final packageInfoProvider = FutureProvider<PackageInfo>((ref) async {
  return await PackageInfo.fromPlatform();
});

class SystemSettingsScreen extends ConsumerStatefulWidget {
  const SystemSettingsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<SystemSettingsScreen> createState() => _SystemSettingsScreenState();
}

class _SystemSettingsScreenState extends ConsumerState<SystemSettingsScreen> {
  final _apiUrlController = TextEditingController();
  bool _isDarkMode = true;
  bool _autoRefresh = true;
  int _refreshInterval = 30; // seconds
  
  @override
  void initState() {
    super.initState();
    _loadSettings();
  }
  
  Future<void> _loadSettings() async {
    final storage = ref.read(storageServiceProvider);
    final apiUrl = await storage.getString('api_url') ?? 'http://localhost:8000';
    _apiUrlController.text = apiUrl;
    
    setState(() {
      _isDarkMode = storage.getBool('dark_mode') ?? true;
      _autoRefresh = storage.getBool('auto_refresh') ?? true;
      _refreshInterval = storage.getInt('refresh_interval') ?? 30;
    });
  }
  
  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final healthAsync = ref.watch(systemHealthProvider);
    final statusAsync = ref.watch(systemStatusProvider);
    final packageInfoAsync = ref.watch(packageInfoProvider);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: const Text(
          '⚙️ Sistem Ayarları',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(systemHealthProvider);
              ref.invalidate(systemStatusProvider);
            },
            tooltip: 'Yenile',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // System Health Card
            Card(
              color: AppColors.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '🏥 Sistem Sağlığı',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    healthAsync.when(
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (err, stack) => Text(
                        'Hata: $err',
                        style: TextStyle(color: AppColors.error),
                      ),
                      data: (health) => Column(
                        children: [
                          _buildHealthItem(
                            'API Durumu',
                            health['healthy'] == true ? 'Çalışıyor' : 'Sorunlu',
                            health['healthy'] == true ? Icons.check_circle : Icons.error,
                            health['healthy'] == true ? AppColors.success : AppColors.error,
                          ),
                          const SizedBox(height: 8),
                          _buildHealthItem(
                            'Process',
                            health['process_running'] == true ? 'Aktif' : 'Durdurulmuş',
                            Icons.memory,
                            health['process_running'] == true ? AppColors.success : AppColors.warning,
                          ),
                          const SizedBox(height: 8),
                          _buildHealthItem(
                            'Aktif Session',
                            '${health['active_sessions'] ?? 0} / ${health['total_bots'] ?? 0}',
                            Icons.people,
                            (health['active_sessions'] ?? 0) > 0 ? AppColors.info : AppColors.error,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // System Status Card
            statusAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (status) => Card(
                color: AppColors.surface,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '📊 Sistem İstatistikleri',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: _buildStatCard(
                              'Toplam Bot',
                              status['system_stats']?['total_bots']?.toString() ?? '0',
                              Icons.smart_toy,
                              AppColors.primary,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: _buildStatCard(
                              'Aktif Bot',
                              status['system_stats']?['active_bots']?.toString() ?? '0',
                              Icons.online_prediction,
                              AppColors.success,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: _buildStatCard(
                              'Toplam Mesaj',
                              status['system_stats']?['total_messages']?.toString() ?? '0',
                              Icons.message,
                              AppColors.info,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: _buildStatCard(
                              'Hata Oranı',
                              '${status['system_stats']?['error_rate']?.toStringAsFixed(1) ?? 0}%',
                              Icons.error_outline,
                              AppColors.warning,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // API Settings Card
            Card(
              color: AppColors.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '🌐 API Ayarları',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _apiUrlController,
                      decoration: InputDecoration(
                        labelText: 'API URL',
                        hintText: 'http://localhost:8000',
                        prefixIcon: const Icon(Icons.link),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        filled: true,
                        fillColor: AppColors.background,
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () async {
                          final storage = ref.read(storageServiceProvider);
                          await storage.setString('api_url', _apiUrlController.text);
                          
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('✅ API URL güncellendi'),
                              backgroundColor: AppColors.success,
                            ),
                          );
                        },
                        icon: const Icon(Icons.save),
                        label: const Text('Kaydet'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // UI Settings Card
            Card(
              color: AppColors.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '🎨 Görünüm Ayarları',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    SwitchListTile(
                      title: const Text('Dark Mode'),
                      subtitle: const Text('Koyu tema kullan'),
                      value: _isDarkMode,
                      onChanged: (value) async {
                        setState(() {
                          _isDarkMode = value;
                        });
                        final storage = ref.read(storageServiceProvider);
                        await storage.setBool('dark_mode', value);
                      },
                      secondary: Icon(
                        _isDarkMode ? Icons.dark_mode : Icons.light_mode,
                      ),
                    ),
                    const Divider(),
                    SwitchListTile(
                      title: const Text('Otomatik Yenileme'),
                      subtitle: Text('Her $_refreshInterval saniyede yenile'),
                      value: _autoRefresh,
                      onChanged: (value) async {
                        setState(() {
                          _autoRefresh = value;
                        });
                        final storage = ref.read(storageServiceProvider);
                        await storage.setBool('auto_refresh', value);
                      },
                      secondary: const Icon(Icons.refresh),
                    ),
                    if (_autoRefresh) ...[
                      const SizedBox(height: 8),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Yenileme Aralığı: $_refreshInterval saniye',
                              style: TextStyle(color: AppColors.textSecondary),
                            ),
                            Slider(
                              value: _refreshInterval.toDouble(),
                              min: 10,
                              max: 120,
                              divisions: 11,
                              label: '$_refreshInterval s',
                              onChanged: (value) {
                                setState(() {
                                  _refreshInterval = value.toInt();
                                });
                              },
                              onChangeEnd: (value) async {
                                final storage = ref.read(storageServiceProvider);
                                await storage.setInt('refresh_interval', value.toInt());
                              },
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Bot Control Card
            Card(
              color: AppColors.surface,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '🤖 Bot Kontrolü',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () async {
                              try {
                                final api = ref.read(apiServiceProvider);
                                await api.startSystem();
                                
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('✅ Sistem başlatıldı'),
                                    backgroundColor: AppColors.success,
                                  ),
                                );
                                
                                ref.invalidate(systemHealthProvider);
                                ref.invalidate(systemStatusProvider);
                              } catch (e) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('❌ Hata: $e'),
                                    backgroundColor: AppColors.error,
                                  ),
                                );
                              }
                            },
                            icon: const Icon(Icons.play_arrow),
                            label: const Text('Başlat'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.success,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () async {
                              try {
                                final api = ref.read(apiServiceProvider);
                                await api.stopSystem();
                                
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('⏹️ Sistem durduruldu'),
                                    backgroundColor: AppColors.warning,
                                  ),
                                );
                                
                                ref.invalidate(systemHealthProvider);
                                ref.invalidate(systemStatusProvider);
                              } catch (e) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('❌ Hata: $e'),
                                    backgroundColor: AppColors.error,
                                  ),
                                );
                              }
                            },
                            icon: const Icon(Icons.stop),
                            label: const Text('Durdur'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.error,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // About Card
            packageInfoAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (packageInfo) => Card(
                color: AppColors.surface,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '📱 Hakkında',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      ListTile(
                        leading: const Icon(Icons.apps),
                        title: const Text('Uygulama Adı'),
                        subtitle: Text(packageInfo.appName),
                      ),
                      ListTile(
                        leading: const Icon(Icons.numbers),
                        title: const Text('Versiyon'),
                        subtitle: Text('${packageInfo.version} (${packageInfo.buildNumber})'),
                      ),
                      ListTile(
                        leading: const Icon(Icons.code),
                        title: const Text('Geliştirici'),
                        subtitle: const Text('GavatCore Team'),
                      ),
                      const Divider(),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          TextButton.icon(
                            onPressed: () async {
                              const url = 'https://github.com/gavatcore/gavatcore';
                              if (await canLaunchUrl(Uri.parse(url))) {
                                await launchUrl(Uri.parse(url));
                              }
                            },
                            icon: const Icon(Icons.code),
                            label: const Text('GitHub'),
                          ),
                          TextButton.icon(
                            onPressed: () async {
                              const url = 'https://gavatcore.com/docs';
                              if (await canLaunchUrl(Uri.parse(url))) {
                                await launchUrl(Uri.parse(url));
                              }
                            },
                            icon: const Icon(Icons.book),
                            label: const Text('Dokümantasyon'),
                          ),
                          TextButton.icon(
                            onPressed: () {
                              showDialog(
                                context: context,
                                builder: (context) => AlertDialog(
                                  title: const Text('Geri Bildirim'),
                                  content: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const TextField(
                                        maxLines: 5,
                                        decoration: InputDecoration(
                                          hintText: 'Görüş ve önerilerinizi yazın...',
                                          border: OutlineInputBorder(),
                                        ),
                                      ),
                                      const SizedBox(height: 16),
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.end,
                                        children: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(context),
                                            child: const Text('İptal'),
                                          ),
                                          const SizedBox(width: 8),
                                          ElevatedButton(
                                            onPressed: () {
                                              Navigator.pop(context);
                                              ScaffoldMessenger.of(context).showSnackBar(
                                                const SnackBar(
                                                  content: Text('✅ Geri bildirim gönderildi'),
                                                  backgroundColor: AppColors.success,
                                                ),
                                              );
                                            },
                                            child: const Text('Gönder'),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                            icon: const Icon(Icons.feedback),
                            label: const Text('Geri Bildirim'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
  
  Widget _buildHealthItem(String label, String value, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Text(label),
        ),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
  
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 4),
              Text(
                title,
                style: TextStyle(
                  fontSize: 12,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
} 