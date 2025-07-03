import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/auth_provider.dart';
import '../../shared/themes/app_theme.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('⚙️ Ayarlar'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // User Info Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '👤 Kullanıcı Bilgileri',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  authState.when(
                    data: (user) => user != null
                        ? Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('📧 Email: ${user.email}'),
                              const SizedBox(height: 8),
                              Text('👤 İsim: ${user.name}'),
                              const SizedBox(height: 8),
                              Text('🛡️ Rol: ${user.role}'),
                            ],
                          )
                        : const Text('⚠️ Kullanıcı bilgisi bulunamadı'),
                    loading: () => const CircularProgressIndicator(),
                    error: (e, _) => Text('❌ Hata: $e'),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // App Settings Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '📱 Uygulama Ayarları',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  
                  // Theme Setting
                  ListTile(
                    leading: Icon(Icons.palette, color: AppTheme.primaryColor),
                    title: const Text('🎨 Tema'),
                    subtitle: const Text('Açık/Koyu tema seçimi'),
                    trailing: Switch(
                      value: false, // TODO: Implement theme provider
                      onChanged: (value) {
                        // TODO: Toggle theme
                      },
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                  
                  // Notifications Setting
                  ListTile(
                    leading: Icon(Icons.notifications, color: AppTheme.secondaryColor),
                    title: const Text('🔔 Bildirimler'),
                    subtitle: const Text('Push bildirimleri'),
                    trailing: Switch(
                      value: true, // TODO: Implement notification provider
                      onChanged: (value) {
                        // TODO: Toggle notifications
                      },
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                  
                  // Auto-refresh Setting
                  ListTile(
                    leading: Icon(Icons.refresh, color: AppTheme.successColor),
                    title: const Text('🔄 Otomatik Yenileme'),
                    subtitle: const Text('Real-time güncellemeler'),
                    trailing: Switch(
                      value: true,
                      onChanged: (value) {
                        // TODO: Implement auto-refresh setting
                      },
                    ),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // System Info Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '🔧 Sistem Bilgileri',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text('📱 Versiyon: 1.0.0'),
                  const SizedBox(height: 8),
                  const Text('🏗️ Build: GAVATCore Mobile v1.0'),
                  const SizedBox(height: 8),
                  const Text('🌐 API: http://localhost:9500'),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 24),
          
          // Logout Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () async {
                final shouldLogout = await showDialog<bool>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('🚪 Çıkış'),
                    content: const Text('Çıkış yapmak istediğinizden emin misiniz?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('❌ İptal'),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.errorColor,
                        ),
                        child: const Text('✅ Çıkış Yap'),
                      ),
                    ],
                  ),
                );
                
                if (shouldLogout == true) {
                  await ref.read(authProvider.notifier).logout();
                  if (context.mounted) {
                    Navigator.of(context).pushReplacementNamed('/login');
                  }
                }
              },
              icon: const Icon(Icons.logout),
              label: const Text('🚪 Çıkış Yap'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.errorColor,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),
        ],
      ),
    );
  }
} 