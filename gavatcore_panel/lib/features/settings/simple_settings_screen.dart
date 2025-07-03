import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SimpleSettingsScreen extends ConsumerStatefulWidget {
  const SimpleSettingsScreen({super.key});

  @override
  ConsumerState<SimpleSettingsScreen> createState() => _SimpleSettingsScreenState();
}

class _SimpleSettingsScreenState extends ConsumerState<SimpleSettingsScreen> {
  bool _isDarkMode = true;
  bool _notifications = true;
  bool _autoRefresh = true;
  bool _soundEffects = false;
  double _refreshInterval = 30.0;
  String _apiUrl = 'http://localhost:5050';
  String _selectedLanguage = 'Türkçe';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text(
          '⚙️ Ayarlar',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
        ),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.purple),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('✅ Ayarlar yenilendi'),
                  backgroundColor: Colors.green,
                ),
              );
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
            // Sistem Ayarları
            _buildSettingsSection(
              '🏥 Sistem Ayarları',
              Colors.purple,
              [
                _buildSwitchTile(
                  'Karanlık Mod',
                  'Arayüzde karanlık tema kullan',
                  Icons.dark_mode,
                  _isDarkMode,
                  (value) => setState(() => _isDarkMode = value),
                ),
                _buildSwitchTile(
                  'Otomatik Yenileme',
                  'Verileri otomatik olarak güncelle',
                  Icons.refresh,
                  _autoRefresh,
                  (value) => setState(() => _autoRefresh = value),
                ),
                _buildSliderTile(
                  'Yenileme Aralığı',
                  'Saniye cinsinden güncelleme sıklığı',
                  Icons.timer,
                  _refreshInterval,
                  5.0,
                  120.0,
                  (value) => setState(() => _refreshInterval = value),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Bildirim Ayarları
            _buildSettingsSection(
              '🔔 Bildirim Ayarları',
              Colors.blue,
              [
                _buildSwitchTile(
                  'Bildirimler',
                  'Sistem bildirimleri göster',
                  Icons.notifications,
                  _notifications,
                  (value) => setState(() => _notifications = value),
                ),
                _buildSwitchTile(
                  'Ses Efektleri',
                  'Bildirim sesleri çal',
                  Icons.volume_up,
                  _soundEffects,
                  (value) => setState(() => _soundEffects = value),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // API Ayarları
            _buildSettingsSection(
              '🔗 API Ayarları',
              Colors.green,
              [
                _buildTextFieldTile(
                  'API URL',
                  'Backend API adresi',
                  Icons.link,
                  _apiUrl,
                  (value) => setState(() => _apiUrl = value),
                ),
                _buildDropdownTile(
                  'Dil',
                  'Arayüz dili',
                  Icons.language,
                  _selectedLanguage,
                  ['Türkçe', 'English', 'Español', 'Français'],
                  (value) => setState(() => _selectedLanguage = value!),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Sistem Bilgileri
            _buildSettingsSection(
              '📊 Sistem Bilgileri',
              Colors.orange,
              [
                _buildInfoTile('Versiyon', '1.0.0', Icons.info),
                _buildInfoTile('Build', '2025.06.21', Icons.build),
                _buildInfoTile('API Durumu', 'Çalışıyor', Icons.check_circle),
                _buildInfoTile('Son Güncelleme', '2 dakika önce', Icons.update),
              ],
            ),

            const SizedBox(height: 24),

            // Eylem Butonları
            _buildActionsSection(),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingsSection(String title, Color color, List<Widget> children) {
    return Card(
      color: const Color(0xFF1A1A1F),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings, color: color, size: 24),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 18,
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchTile(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.purple, size: 20),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: Colors.white60,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.green,
            activeTrackColor: Colors.green.withOpacity(0.3),
          ),
        ],
      ),
    );
  }

  Widget _buildSliderTile(
    String title,
    String subtitle,
    IconData icon,
    double value,
    double min,
    double max,
    ValueChanged<double> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.blue, size: 20),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: Colors.white60,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '${value.round()}s',
                style: const TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: Colors.blue,
              inactiveTrackColor: Colors.blue.withOpacity(0.3),
              thumbColor: Colors.blue,
              overlayColor: Colors.blue.withOpacity(0.2),
            ),
            child: Slider(
              value: value,
              min: min,
              max: max,
              divisions: ((max - min) / 5).round(),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextFieldTile(
    String title,
    String subtitle,
    IconData icon,
    String value,
    ValueChanged<String> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.green, size: 20),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: Colors.white60,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          TextField(
            controller: TextEditingController(text: value),
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.green.withOpacity(0.3)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.green.withOpacity(0.3)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.green),
              ),
              filled: true,
              fillColor: const Color(0xFF1A1A1F),
            ),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownTile(
    String title,
    String subtitle,
    IconData icon,
    String value,
    List<String> options,
    ValueChanged<String?> onChanged,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.yellow, size: 20),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      subtitle,
                      style: const TextStyle(
                        color: Colors.white60,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: value,
            items: options.map((option) => DropdownMenuItem(
              value: option,
              child: Text(option, style: const TextStyle(color: Colors.white)),
            )).toList(),
            onChanged: onChanged,
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.yellow.withOpacity(0.3)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(color: Colors.yellow.withOpacity(0.3)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Colors.yellow),
              ),
              filled: true,
              fillColor: const Color(0xFF1A1A1F),
            ),
            dropdownColor: const Color(0xFF1A1A1F),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoTile(String title, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.orange, size: 20),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.orange,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionsSection() {
    return Card(
      color: const Color(0xFF1A1A1F),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.settings_applications, color: Colors.red, size: 24),
                const SizedBox(width: 12),
                Text(
                  '🔧 Sistem Eylemleri',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.red,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      _showSaveDialog();
                    },
                    icon: const Icon(Icons.save),
                    label: const Text('Kaydet'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      _showResetDialog();
                    },
                    icon: const Icon(Icons.restore),
                    label: const Text('Sıfırla'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      padding: const EdgeInsets.symmetric(vertical: 16),
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

  void _showSaveDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text(
          'Ayarları Kaydet',
          style: TextStyle(color: Colors.green),
        ),
        content: const Text(
          'Tüm ayarlar kaydedilsin mi?',
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('✅ Ayarlar kaydedildi'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
            ),
            child: const Text('Kaydet'),
          ),
        ],
      ),
    );
  }

  void _showResetDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A1F),
        title: const Text(
          'Ayarları Sıfırla',
          style: TextStyle(color: Colors.red),
        ),
        content: const Text(
          'Tüm ayarlar varsayılan değerlere döndürülsün mü?',
          style: TextStyle(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _isDarkMode = true;
                _notifications = true;
                _autoRefresh = true;
                _soundEffects = false;
                _refreshInterval = 30.0;
                _apiUrl = 'http://localhost:5050';
                _selectedLanguage = 'Türkçe';
              });
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('🔄 Ayarlar sıfırlandı'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Sıfırla'),
          ),
        ],
      ),
    );
  }
} 