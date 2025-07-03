import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../shared/themes/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../shared/themes/app_colors.dart';
import '../../shared/widgets/loading_overlay.dart';

// Behavioral data model
class BehavioralData {
  final String userId;
  final String username;
  final double trustIndex;
  final double vipProbability;
  final int messageCount;
  final Map<String, dynamic> emotionalProfile;
  final List<Map<String, dynamic>> messageHistory;
  final Map<String, dynamic> suggestedStrategy;
  final DateTime lastActivity;
  final double manipulationResistance;
  final double silenceThreshold;
  
  BehavioralData({
    required this.userId,
    required this.username,
    required this.trustIndex,
    required this.vipProbability,
    required this.messageCount,
    required this.emotionalProfile,
    required this.messageHistory,
    required this.suggestedStrategy,
    required this.lastActivity,
    required this.manipulationResistance,
    required this.silenceThreshold,
  });
  
  factory BehavioralData.fromJson(Map<String, dynamic> json) {
    return BehavioralData(
      userId: json['user_id'] ?? '',
      username: json['username'] ?? 'Unknown',
      trustIndex: (json['trust_index'] ?? 0).toDouble(),
      vipProbability: (json['vip_probability'] ?? 0).toDouble(),
      messageCount: json['message_count'] ?? 0,
      emotionalProfile: json['emotional_profile'] ?? {},
      messageHistory: List<Map<String, dynamic>>.from(json['message_history'] ?? []),
      suggestedStrategy: json['suggested_strategy'] ?? {},
      lastActivity: DateTime.parse(json['last_activity'] ?? DateTime.now().toIso8601String()),
      manipulationResistance: (json['manipulation_resistance'] ?? 0).toDouble(),
      silenceThreshold: (json['silence_threshold'] ?? 0).toDouble(),
    );
  }
}

// Provider for behavioral data
final behavioralInsightsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final api = ref.read(apiServiceProvider);
  return await api.getBehavioralInsights();
});

final highRiskUsersProvider = FutureProvider<List<BehavioralData>>((ref) async {
  final api = ref.read(apiServiceProvider);
  final response = await api.getHighRiskUsers();
  
  if (response['success'] == true && response['users'] != null) {
    return (response['users'] as List)
        .map((u) => BehavioralData.fromJson(u))
        .toList();
  }
  return [];
});

final selectedUserProvider = StateProvider<String?>((ref) => null);

final userBehaviorProvider = FutureProvider.family<BehavioralData?, String>((ref, userId) async {
  if (userId.isEmpty) return null;
  
  final api = ref.read(apiServiceProvider);
  final response = await api.getUserBehavior(userId);
  
  if (response['success'] == true && response['profile'] != null) {
    return BehavioralData.fromJson(response['profile']);
  }
  return null;
});

class BehavioralTrackerScreen extends ConsumerStatefulWidget {
  const BehavioralTrackerScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<BehavioralTrackerScreen> createState() => _BehavioralTrackerScreenState();
}

class _BehavioralTrackerScreenState extends ConsumerState<BehavioralTrackerScreen> {
  final _searchController = TextEditingController();
  final _userIdController = TextEditingController();
  
  @override
  void dispose() {
    _searchController.dispose();
    _userIdController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    final selectedUserId = ref.watch(selectedUserProvider);
    final highRiskUsersAsync = ref.watch(highRiskUsersProvider);
    final insightsAsync = ref.watch(behavioralInsightsProvider);
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        title: Row(
          children: [
            const Text(
              '🧠 Behavioral Tracker',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const Spacer(),
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () {
                ref.invalidate(highRiskUsersProvider);
                ref.invalidate(behavioralInsightsProvider);
              },
              tooltip: 'Yenile',
            ),
          ],
        ),
        elevation: 0,
      ),
      body: Row(
        children: [
          // Sol panel - Kullanıcı listesi ve arama
          Container(
            width: 350,
            decoration: BoxDecoration(
              color: AppColors.surface,
              border: Border(
                right: BorderSide(color: AppColors.divider),
              ),
            ),
            child: Column(
              children: [
                // Manuel kullanıcı ID girişi
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      TextField(
                        controller: _userIdController,
                        decoration: InputDecoration(
                          hintText: 'Kullanıcı ID girin...',
                          prefixIcon: const Icon(Icons.person_search),
                          suffixIcon: IconButton(
                            icon: const Icon(Icons.search),
                            onPressed: () {
                              if (_userIdController.text.isNotEmpty) {
                                ref.read(selectedUserProvider.notifier).state = 
                                    _userIdController.text;
                              }
                            },
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          filled: true,
                          fillColor: AppColors.background,
                        ),
                        onSubmitted: (value) {
                          if (value.isNotEmpty) {
                            ref.read(selectedUserProvider.notifier).state = value;
                          }
                        },
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Arama
                      TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Yüksek riskli kullanıcılarda ara...',
                          prefixIcon: const Icon(Icons.search),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          filled: true,
                          fillColor: AppColors.background,
                        ),
                        onChanged: (value) {
                          setState(() {});
                        },
                      ),
                    ],
                  ),
                ),
                
                const Divider(),
                
                // Yüksek riskli kullanıcılar başlığı
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Row(
                    children: [
                      Icon(Icons.warning, color: AppColors.error, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Yüksek Riskli Kullanıcılar',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                
                // Kullanıcı listesi
                Expanded(
                  child: highRiskUsersAsync.when(
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (err, stack) => Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.error_outline, color: AppColors.error),
                          const SizedBox(height: 8),
                          Text('Hata: $err'),
                        ],
                      ),
                    ),
                    data: (users) {
                      final filteredUsers = users.where((user) {
                        if (_searchController.text.isEmpty) return true;
                        return user.username.toLowerCase()
                            .contains(_searchController.text.toLowerCase());
                      }).toList();
                      
                      if (filteredUsers.isEmpty) {
                        return const Center(
                          child: Text('Yüksek riskli kullanıcı bulunamadı'),
                        );
                      }
                      
                      return ListView.builder(
                        itemCount: filteredUsers.length,
                        itemBuilder: (context, index) {
                          final user = filteredUsers[index];
                          final isSelected = selectedUserId == user.userId;
                          
                          return ListTile(
                            selected: isSelected,
                            selectedTileColor: AppColors.primary.withOpacity(0.1),
                            leading: Stack(
                              children: [
                                CircleAvatar(
                                  backgroundColor: _getTrustColor(user.trustIndex),
                                  child: Text(
                                    user.username[0].toUpperCase(),
                                    style: const TextStyle(color: Colors.white),
                                  ),
                                ),
                                if (user.vipProbability > 0.7)
                                  const Positioned(
                                    right: 0,
                                    bottom: 0,
                                    child: CircleAvatar(
                                      radius: 8,
                                      backgroundColor: Colors.amber,
                                      child: Icon(
                                        Icons.star,
                                        size: 12,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                              ],
                            ),
                            title: Text(
                              user.username,
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Trust: ${(user.trustIndex * 100).toStringAsFixed(0)}%'),
                                Text(
                                  'VIP: ${(user.vipProbability * 100).toStringAsFixed(0)}%',
                                  style: TextStyle(
                                    color: user.vipProbability > 0.7 ? Colors.amber : null,
                                  ),
                                ),
                              ],
                            ),
                            trailing: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.message,
                                  size: 16,
                                  color: AppColors.textSecondary,
                                ),
                                Text(
                                  '${user.messageCount}',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: AppColors.textSecondary,
                                  ),
                                ),
                              ],
                            ),
                            onTap: () {
                              ref.read(selectedUserProvider.notifier).state = user.userId;
                              _userIdController.text = user.userId;
                            },
                          );
                        },
                      );
                    },
                  ),
                ),
                
                // Genel istatistikler
                insightsAsync.when(
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                  data: (insights) => Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.background,
                      border: Border(
                        top: BorderSide(color: AppColors.divider),
                      ),
                    ),
                    child: Column(
                      children: [
                        _buildInsightRow(
                          'Toplam Kullanıcı',
                          insights['total_users']?.toString() ?? '0',
                          Icons.people,
                        ),
                        const SizedBox(height: 8),
                        _buildInsightRow(
                          'Ortalama Trust',
                          '${((insights['avg_trust_index'] ?? 0) * 100).toStringAsFixed(0)}%',
                          Icons.shield,
                        ),
                        const SizedBox(height: 8),
                        _buildInsightRow(
                          'VIP Adayı',
                          insights['high_vip_potential']?.toString() ?? '0',
                          Icons.star,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Sağ panel - Detaylı analiz
          Expanded(
            child: selectedUserId == null
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.person_search, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text(
                          'Analiz için bir kullanıcı seçin veya ID girin',
                          style: TextStyle(fontSize: 18),
                        ),
                      ],
                    ),
                  )
                : _buildUserAnalysis(selectedUserId),
          ),
        ],
      ),
    );
  }
  
  Widget _buildUserAnalysis(String userId) {
    final userBehaviorAsync = ref.watch(userBehaviorProvider(userId));
    
    return userBehaviorAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, stack) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: AppColors.error),
            const SizedBox(height: 16),
            Text(
              'Kullanıcı bulunamadı veya hata oluştu',
              style: TextStyle(color: AppColors.error),
            ),
            const SizedBox(height: 8),
            Text(err.toString()),
          ],
        ),
      ),
      data: (user) {
        if (user == null) {
          return const Center(
            child: Text('Kullanıcı verisi bulunamadı'),
          );
        }
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  CircleAvatar(
                    radius: 32,
                    backgroundColor: _getTrustColor(user.trustIndex),
                    child: Text(
                      user.username[0].toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user.username,
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'ID: ${user.userId}',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (user.vipProbability > 0.7)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.amber,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.star, color: Colors.white, size: 16),
                          SizedBox(width: 4),
                          Text(
                            'VIP Aday',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Metrikler
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Trust Index',
                      '${(user.trustIndex * 100).toStringAsFixed(0)}%',
                      _getTrustColor(user.trustIndex),
                      Icons.shield,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricCard(
                      'VIP Olasılığı',
                      '${(user.vipProbability * 100).toStringAsFixed(0)}%',
                      user.vipProbability > 0.7 ? Colors.amber : AppColors.warning,
                      Icons.star,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Manipülasyon Direnci',
                      '${(user.manipulationResistance * 100).toStringAsFixed(0)}%',
                      AppColors.info,
                      Icons.security,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricCard(
                      'Sessizlik Eşiği',
                      '${(user.silenceThreshold * 100).toStringAsFixed(0)}%',
                      AppColors.primary,
                      Icons.volume_off,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Mesaj Sayısı',
                      user.messageCount.toString(),
                      AppColors.success,
                      Icons.message,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildMetricCard(
                      'Son Aktivite',
                      _formatTime(user.lastActivity.toIso8601String()),
                      AppColors.textSecondary,
                      Icons.access_time,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Duygusal Profil Grafiği
              if (user.emotionalProfile.isNotEmpty)
                Card(
                  color: AppColors.surface,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '😊 Duygusal Profil',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          height: 200,
                          child: _buildEmotionalProfileChart(user.emotionalProfile),
                        ),
                      ],
                    ),
                  ),
                ),
              
              const SizedBox(height: 24),
              
              // AI Önerisi
              if (user.suggestedStrategy.isNotEmpty)
                Card(
                  color: AppColors.primary.withOpacity(0.1),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              Icons.lightbulb,
                              color: AppColors.primary,
                            ),
                            const SizedBox(width: 8),
                            const Text(
                              '🤖 AI Strateji Önerisi',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(
                          user.suggestedStrategy['recommendation'] ?? 
                          'Bu kullanıcı için daha fazla veri toplanması gerekiyor.',
                          style: const TextStyle(fontSize: 16),
                        ),
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 8,
                          children: [
                            if (user.suggestedStrategy['tone'] != null)
                              Chip(
                                label: Text('Önerilen Ton: ${user.suggestedStrategy['tone']}'),
                                backgroundColor: AppColors.warning.withOpacity(0.2),
                              ),
                            if (user.suggestedStrategy['approach'] != null)
                              Chip(
                                label: Text('Yaklaşım: ${user.suggestedStrategy['approach']}'),
                                backgroundColor: AppColors.info.withOpacity(0.2),
                              ),
                            if (user.suggestedStrategy['reply_mode'] != null)
                              Chip(
                                label: Text('Mode: ${user.suggestedStrategy['reply_mode']}'),
                                backgroundColor: AppColors.success.withOpacity(0.2),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              
              const SizedBox(height: 24),
              
              // Son Mesajlar
              if (user.messageHistory.isNotEmpty)
                Card(
                  color: AppColors.surface,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '💬 Son Mesajlar',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ...user.messageHistory.take(10).map((msg) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Icon(
                                msg['is_bot'] == true ? Icons.smart_toy : Icons.person,
                                size: 20,
                                color: msg['is_bot'] == true ? AppColors.primary : AppColors.textSecondary,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      msg['message'] ?? '',
                                      style: const TextStyle(fontSize: 14),
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Text(
                                          _formatTime(msg['timestamp']),
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: AppColors.textSecondary,
                                          ),
                                        ),
                                        if (msg['emotion'] != null) ...[
                                          const SizedBox(width: 8),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 6,
                                              vertical: 2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: _getEmotionColor(msg['emotion']).withOpacity(0.2),
                                              borderRadius: BorderRadius.circular(10),
                                            ),
                                            child: Text(
                                              msg['emotion'],
                                              style: TextStyle(
                                                fontSize: 10,
                                                color: _getEmotionColor(msg['emotion']),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        )).toList(),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
  
  Widget _buildInsightRow(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppColors.textSecondary),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: AppColors.textSecondary,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
  
  Widget _buildMetricCard(String title, String value, Color color, IconData icon) {
    return Card(
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildEmotionalProfileChart(Map<String, dynamic> profile) {
    final emotions = profile.entries
        .where((e) => e.value is num)
        .map((e) => MapEntry(e.key, (e.value as num).toDouble()))
        .toList();
    
    if (emotions.isEmpty) {
      return const Center(
        child: Text('Duygusal profil verisi yok'),
      );
    }
    
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 1.0,
        barTouchData: BarTouchData(
          enabled: true,
          touchTooltipData: BarTouchTooltipData(
            tooltipBgColor: AppColors.surface,
            getTooltipItem: (group, groupIndex, rod, rodIndex) {
              final emotion = emotions[group.x.toInt()].key;
              final value = (rod.toY * 100).toStringAsFixed(0);
              return BarTooltipItem(
                '$emotion\n$value%',
                const TextStyle(color: Colors.white),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                if (value.toInt() < emotions.length) {
                  final emotion = emotions[value.toInt()].key;
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      _getEmotionLabel(emotion),
                      style: const TextStyle(fontSize: 10),
                    ),
                  );
                }
                return const SizedBox();
              },
              reservedSize: 30,
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                return Text(
                  '${(value * 100).toInt()}%',
                  style: const TextStyle(fontSize: 10),
                );
              },
              reservedSize: 30,
            ),
          ),
          topTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 0.2,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: AppColors.divider,
              strokeWidth: 0.5,
            );
          },
        ),
        borderData: FlBorderData(show: false),
        barGroups: emotions.asMap().entries.map((entry) {
          final index = entry.key;
          final emotion = entry.value;
          
          return BarChartGroupData(
            x: index,
            barRods: [
              BarChartRodData(
                toY: emotion.value,
                color: _getEmotionColor(emotion.key),
                width: 20,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(4),
                ),
              ),
            ],
          );
        }).toList(),
      ),
    );
  }
  
  Color _getTrustColor(double trust) {
    if (trust > 0.7) return AppColors.success;
    if (trust > 0.4) return AppColors.warning;
    return AppColors.error;
  }
  
  Color _getEmotionColor(String? emotion) {
    switch (emotion?.toLowerCase()) {
      case 'happy':
      case 'joy':
      case 'positive':
        return Colors.green;
      case 'love':
      case 'flirty':
        return Colors.pink;
      case 'sad':
      case 'negative':
        return Colors.blue;
      case 'angry':
      case 'anger':
        return Colors.red;
      case 'fear':
        return Colors.purple;
      case 'surprise':
        return Colors.orange;
      case 'neutral':
        return Colors.grey;
      default:
        return AppColors.textSecondary;
    }
  }
  
  String _getEmotionLabel(String emotion) {
    final labels = {
      'happy': '😊',
      'joy': '😄',
      'positive': '👍',
      'love': '❤️',
      'flirty': '😘',
      'sad': '😢',
      'negative': '👎',
      'angry': '😠',
      'anger': '😡',
      'fear': '😨',
      'surprise': '😮',
      'neutral': '😐',
    };
    
    return labels[emotion.toLowerCase()] ?? emotion;
  }
  
  String _formatTime(String? timestamp) {
    if (timestamp == null) return '';
    
    try {
      final time = DateTime.parse(timestamp);
      final now = DateTime.now();
      final diff = now.difference(time);
      
      if (diff.inMinutes < 1) return 'şimdi';
      if (diff.inMinutes < 60) return '${diff.inMinutes}dk önce';
      if (diff.inHours < 24) return '${diff.inHours}sa önce';
      if (diff.inDays < 7) return '${diff.inDays}g önce';
      
      return '${time.day}/${time.month}';
    } catch (e) {
      return '';
    }
  }
} 