import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/glass_container.dart';
import '../../../core/models/app_state.dart';
import '../providers/dashboard_providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stats = ref.watch(dashboardStatsProvider);
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome header
            _buildWelcomeHeader(),
            
            const SizedBox(height: 24),
            
            // Stats cards
            _buildStatsCards(ref, stats),
            
            const SizedBox(height: 24),
            
            // Charts section
            _buildChartsSection(stats),
            
            const SizedBox(height: 24),
            
            // Recent activity
            _buildRecentActivity(),
            
            const SizedBox(height: 100), // Bottom navigation space
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return GlassContainer(
      padding: const EdgeInsets.all(24),
      isNeonBorder: true,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome Back!',
                  style: NeonTextStyles.neonTitle.copyWith(fontSize: 28),
                ),
                
                const SizedBox(height: 8),
                
                Text(
                  'Your GavatCore system is running smoothly',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                Row(
                  children: [
                    _buildQuickActionButton(
                      'Start All Bots',
                      Icons.play_arrow,
                      AppTheme.neonColors.green,
                      () {},
                    ),
                    
                    const SizedBox(width: 12),
                    
                    _buildQuickActionButton(
                      'Emergency Stop',
                      Icons.stop,
                      AppTheme.neonColors.red,
                      () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // System status indicator
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.neonColors.purpleGlow,
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: Icon(
              Icons.auto_awesome,
              color: Colors.white,
              size: 40,
            ),
          ).animate(onPlay: (controller) => controller.repeat())
              .rotation(duration: 10.seconds),
        ],
      ),
    ).animate().slideY(begin: -0.3, duration: 600.ms);
  }

  Widget _buildQuickActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return AnimatedGlassContainer(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      onTap: onTap,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards(WidgetRef ref, DashboardStats stats) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard(
          'Aktif Botlar',
          '${stats.activeBots}',
          Icons.smart_toy,
          AppTheme.neonColors.purple,
          subtitle: '/ ${stats.totalBots} toplam',
          trend: '+2',
        ),
        _buildStatCard(
          'Günlük Mesaj',
          '${stats.todayMessages}',
          Icons.message,
          AppTheme.neonColors.blue,
          subtitle: 'son 24 saat',
          trend: '+15%',
        ),
        _buildStatCard(
          'API Çağrısı',
          '${stats.apiCalls}',
          Icons.api,
          AppTheme.neonColors.green,
          subtitle: 'bu saat',
          trend: '+8%',
        ),
        _buildStatCard(
          'Başarı Oranı',
          '${stats.successRate.toStringAsFixed(1)}%',
          Icons.trending_up,
          AppTheme.neonColors.orange,
          subtitle: 'ortalama',
          trend: '+3%',
        ),
      ],
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color, {
    String? subtitle,
    String? trend,
  }) {
    return AnimatedGlassContainer(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const Spacer(),
              if (trend != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: trend.startsWith('+') 
                        ? AppTheme.neonColors.green.withOpacity(0.2)
                        : AppTheme.neonColors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    trend,
                    style: TextStyle(
                      fontSize: 10,
                      color: trend.startsWith('+') 
                          ? AppTheme.neonColors.green
                          : AppTheme.neonColors.red,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          TweenAnimationBuilder<double>(
            duration: const Duration(milliseconds: 1500),
            tween: Tween(begin: 0, end: 1),
            builder: (context, value, child) {
              final animatedValue = value == 1 ? value : 0;
              return Text(
                value == 1 ? value : _formatNumber(animatedValue),
                style: NeonTextStyles.neonTitle.copyWith(
                  fontSize: 24,
                  color: color,
                ),
              );
            },
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.white70,
              fontWeight: FontWeight.w500,
            ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 2),
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.white54,
              ),
            ),
          ],
        ],
      ),
    ).animate()
        .fadeIn(delay: Duration(milliseconds: 100))
        .slideY(begin: 0.2, end: 0);
  }

  String _formatNumber(double value) {
    if (value >= 1000000) {
      return '${(value / 1000000).toStringAsFixed(1)}M';
    } else if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(1)}K';
    }
    return value.toInt().toString();
  }

  Widget _buildChartsSection(AsyncValue<DashboardStats> stats) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Analytics Overview',
          style: NeonTextStyles.neonSubtitle,
        ),
        
        const SizedBox(height: 16),
        
        Row(
          children: [
            // Message activity chart
            Expanded(
              flex: 2,
              child: GlassContainer(
                height: 250,
                padding: const EdgeInsets.all(20),
                isNeonBorder: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Message Activity',
                      style: NeonTextStyles.neonBody.copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    Expanded(
                      child: LineChart(
                        _buildLineChartData(),
                      ),
                    ),
                  ],
                ),
              ).animate(delay: 200.ms).slideX(begin: -0.3),
            ),
            
            const SizedBox(width: 16),
            
            // System status pie chart
            Expanded(
              child: GlassContainer(
                height: 250,
                padding: const EdgeInsets.all(20),
                isNeonBorder: true,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'System Status',
                      style: NeonTextStyles.neonBody.copyWith(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    Expanded(
                      child: PieChart(
                        _buildPieChartData(),
                      ),
                    ),
                  ],
                ),
              ).animate(delay: 400.ms).slideX(begin: 0.3),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRecentActivity() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Activity',
          style: NeonTextStyles.neonSubtitle,
        ),
        
        const SizedBox(height: 16),
        
        GlassContainer(
          padding: const EdgeInsets.all(20),
          isNeonBorder: true,
          child: Column(
            children: List.generate(5, (index) => 
              _buildActivityItem(
                'Bot ${index + 1} sent message to @group_${index + 1}',
                '${index + 2} minutes ago',
                _getActivityIcon(index),
                _getActivityColor(index),
              ).animate(delay: (index * 100).ms).slideX(begin: -0.2),
            ),
          ),
        ).animate(delay: 600.ms).slideY(begin: 0.3),
      ],
    );
  }

  Widget _buildActivityItem(
    String title,
    String time,
    IconData icon,
    Color color,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: color.withOpacity(0.5),
                width: 1,
              ),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          
          const SizedBox(width: 16),
          
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                Text(
                  time,
                  style: TextStyle(
                    color: Colors.white60,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          
          Icon(
            Icons.chevron_right,
            color: Colors.white30,
            size: 20,
          ),
        ],
      ),
    );
  }

  LineChartData _buildLineChartData() {
    return LineChartData(
      gridData: FlGridData(show: false),
      titlesData: FlTitlesData(show: false),
      borderData: FlBorderData(show: false),
      minX: 0,
      maxX: 6,
      minY: 0,
      maxY: 100,
      lineBarsData: [
        LineChartBarData(
          spots: const [
            FlSpot(0, 20),
            FlSpot(1, 45),
            FlSpot(2, 30),
            FlSpot(3, 70),
            FlSpot(4, 55),
            FlSpot(5, 85),
            FlSpot(6, 65),
          ],
          isCurved: true,
          gradient: LinearGradient(
            colors: [
              AppTheme.neonColors.purple,
              AppTheme.neonColors.blue,
            ],
          ),
          barWidth: 3,
          isStrokeCapRound: true,
          dotData: FlDotData(show: false),
          belowBarData: BarAreaData(
            show: true,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                AppTheme.neonColors.purple.withOpacity(0.3),
                AppTheme.neonColors.blue.withOpacity(0.1),
              ],
            ),
          ),
        ),
      ],
    );
  }

  PieChartData _buildPieChartData() {
    return PieChartData(
      sectionsSpace: 2,
      centerSpaceRadius: 40,
      sections: [
        PieChartSectionData(
          color: AppTheme.neonColors.green,
          value: 65,
          title: '65%',
          radius: 50,
          titleStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        PieChartSectionData(
          color: AppTheme.neonColors.yellow,
          value: 25,
          title: '25%',
          radius: 45,
          titleStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        PieChartSectionData(
          color: AppTheme.neonColors.red,
          value: 10,
          title: '10%',
          radius: 40,
          titleStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  IconData _getActivityIcon(int index) {
    final icons = [
      Icons.send,
      Icons.schedule,
      Icons.error,
      Icons.check_circle,
      Icons.refresh,
    ];
    return icons[index % icons.length];
  }

  Color _getActivityColor(int index) {
    final colors = [
      AppTheme.neonColors.blue,
      AppTheme.neonColors.green,
      AppTheme.neonColors.red,
      AppTheme.neonColors.purple,
      AppTheme.neonColors.yellow,
    ];
    return colors[index % colors.length];
  }
} 