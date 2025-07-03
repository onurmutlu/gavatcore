import 'package:flutter/material.dart';
import '../../../shared/widgets/real_time_stats_card.dart';
import '../../../shared/themes/app_theme.dart';

class DashboardStatsSection extends StatelessWidget {
  const DashboardStatsSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.all(16),
          child: Text(
            '📊 Real-Time System Stats',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppTheme.textColor,
            ),
          ),
        ),
        
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            mainAxisSpacing: 16,
            crossAxisSpacing: 16,
            childAspectRatio: 1.2,
            children: const [
              // Active Users
              RealTimeStatsCard(
                title: 'Active Users',
                icon: Icons.people,
                color: AppTheme.primaryColor,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'active_users',
                refreshInterval: Duration(seconds: 30),
              ),
              
              // Total Messages
              RealTimeStatsCard(
                title: 'Messages Today',
                icon: Icons.message,
                color: Colors.green,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'messages_today',
                refreshInterval: Duration(seconds: 30),
              ),
              
              // System Health
              RealTimeStatsCard(
                title: 'System Health',
                icon: Icons.health_and_safety,
                color: Colors.orange,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'system_health',
                unit: '%',
                refreshInterval: Duration(seconds: 15),
              ),
              
              // Bot Status
              RealTimeStatsCard(
                title: 'Active Bots',
                icon: Icons.smart_toy,
                color: Colors.purple,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'active_bots',
                refreshInterval: Duration(seconds: 45),
              ),
              
              // Response Time
              RealTimeStatsCard(
                title: 'Avg Response',
                icon: Icons.speed,
                color: Colors.blue,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'avg_response_time',
                unit: 'ms',
                refreshInterval: Duration(seconds: 20),
              ),
              
              // Cache Hit Rate
              RealTimeStatsCard(
                title: 'Cache Hit Rate',
                icon: Icons.storage,
                color: Colors.teal,
                apiEndpoint: '/api/flutter/quick-stats',
                valueKey: 'cache_hit_rate',
                unit: '%',
                refreshInterval: Duration(seconds: 60),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        
        // Quick Actions Section
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '⚡ Quick Actions',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textColor,
                ),
              ),
              const SizedBox(height: 12),
              
              Row(
                children: [
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.refresh,
                      label: 'Refresh All',
                      color: AppTheme.primaryColor,
                      onTap: () {
                        // This will be handled by the parent widget
                        // to refresh all RealTimeStatsCard widgets
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionButton(
                      icon: Icons.settings,
                      label: 'Settings',
                      color: Colors.grey,
                      onTap: () {
                        // Navigate to settings
                      },
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: color.withOpacity(0.3),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 18),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
} 