import 'package:flutter/material.dart';
import 'dart:math' as math;

/// 🏥 System Health Chart Widget
/// 
/// Displays system health with circular progress and detailed metrics
class SystemHealthChart extends StatefulWidget {
  final Map<String, dynamic> healthData;

  const SystemHealthChart({
    Key? key,
    required this.healthData,
  }) : super(key: key);

  @override
  State<SystemHealthChart> createState() => _SystemHealthChartState();
}

class _SystemHealthChartState extends State<SystemHealthChart>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _animation = Tween<double>(
      begin: 0,
      end: 1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutCubic,
    ));
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final healthPercentage = _getHealthPercentage();
    final healthColor = _getHealthColor(healthPercentage);
    final healthStatus = _getHealthStatus(healthPercentage);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F3A),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(
                Icons.monitor_heart,
                color: healthColor,
                size: 24,
              ),
              const SizedBox(width: 12),
              const Text(
                'System Health',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: healthColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  healthStatus,
                  style: TextStyle(
                    color: healthColor,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Circular Health Chart
          Row(
            children: [
              Expanded(
                flex: 2,
                child: AspectRatio(
                  aspectRatio: 1,
                  child: AnimatedBuilder(
                    animation: _animation,
                    builder: (context, child) {
                      return CustomPaint(
                        painter: HealthCirclePainter(
                          progress: _animation.value * (healthPercentage / 100),
                          color: healthColor,
                          backgroundColor: Colors.grey[700]!,
                        ),
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                '${(healthPercentage * _animation.value).toInt()}%',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                'Health Score',
                                style: TextStyle(
                                  color: Colors.grey[400],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              const SizedBox(width: 20),
              
              // Health Metrics
              Expanded(
                flex: 3,
                child: Column(
                  children: [
                    _buildHealthMetric(
                      'CPU Usage',
                      _getCPUUsage(),
                      Icons.memory,
                      _getCPUUsage() < 70 ? Colors.green : 
                      _getCPUUsage() < 85 ? Colors.orange : Colors.red,
                    ),
                    const SizedBox(height: 12),
                    _buildHealthMetric(
                      'Memory',
                      _getMemoryUsage(),
                      Icons.storage,
                      _getMemoryUsage() < 70 ? Colors.green : 
                      _getMemoryUsage() < 85 ? Colors.orange : Colors.red,
                    ),
                    const SizedBox(height: 12),
                    _buildHealthMetric(
                      'Response Time',
                      _getResponseTime(),
                      Icons.speed,
                      _getResponseTime() < 100 ? Colors.green : 
                      _getResponseTime() < 300 ? Colors.orange : Colors.red,
                    ),
                    const SizedBox(height: 12),
                    _buildHealthMetric(
                      'Active Services',
                      _getActiveServices(),
                      Icons.cloud,
                      _getActiveServices() >= 3 ? Colors.green : 
                      _getActiveServices() >= 2 ? Colors.orange : Colors.red,
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Health Details Row
          Row(
            children: [
              Expanded(
                child: _buildHealthDetail(
                  'Uptime',
                  _getUptime(),
                  Icons.schedule,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildHealthDetail(
                  'Last Check',
                  _getLastCheck(),
                  Icons.update,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildHealthDetail(
                  'Cache Hit',
                  '${_getCacheHitRate()}%',
                  Icons.cached,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHealthMetric(String label, dynamic value, IconData icon, Color color) {
    final isPercentage = value is double && value <= 100;
    final displayValue = isPercentage ? '${value.toInt()}%' : value.toString();
    
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(
            icon,
            color: color,
            size: 14,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  color: Colors.grey[400],
                  fontSize: 10,
                ),
              ),
              Text(
                displayValue,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        if (isPercentage)
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[700],
              borderRadius: BorderRadius.circular(2),
            ),
            child: FractionallySizedBox(
              alignment: Alignment.centerLeft,
              widthFactor: (value as double) / 100,
              child: Container(
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildHealthDetail(String label, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1419),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: Colors.grey[400],
            size: 16,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              color: Colors.grey[500],
              fontSize: 9,
            ),
          ),
        ],
      ),
    );
  }

  double _getHealthPercentage() {
    if (widget.healthData.isEmpty) return 0.0;
    
    final health = widget.healthData['system_health'];
    if (health is num) {
      return health.toDouble();
    }
    
    // Calculate from available metrics
    final cpu = _getCPUUsage();
    final memory = _getMemoryUsage();
    final services = _getActiveServices();
    
    final cpuScore = math.max(0, 100 - cpu);
    final memoryScore = math.max(0, 100 - memory);
    final serviceScore = (services / 4) * 100;
    
    return (cpuScore + memoryScore + serviceScore) / 3;
  }

  Color _getHealthColor(double health) {
    if (health >= 80) return Colors.green;
    if (health >= 60) return Colors.orange;
    if (health >= 40) return Colors.yellow;
    return Colors.red;
  }

  String _getHealthStatus(double health) {
    if (health >= 80) return 'Excellent';
    if (health >= 60) return 'Good';
    if (health >= 40) return 'Warning';
    return 'Critical';
  }

  double _getCPUUsage() {
    final metrics = widget.healthData['system_metrics'];
    if (metrics is Map<String, dynamic>) {
      final cpu = metrics['cpu_usage'];
      if (cpu is num) return cpu.toDouble();
    }
    return math.Random().nextDouble() * 60 + 20; // Mock data
  }

  double _getMemoryUsage() {
    final metrics = widget.healthData['system_metrics'];
    if (metrics is Map<String, dynamic>) {
      final memory = metrics['memory_usage'];
      if (memory is num) return memory.toDouble();
    }
    return math.Random().nextDouble() * 50 + 30; // Mock data
  }

  double _getResponseTime() {
    final metrics = widget.healthData['performance_metrics'];
    if (metrics is Map<String, dynamic>) {
      final responseTime = metrics['avg_response_time'];
      if (responseTime is num) return responseTime.toDouble();
    }
    return math.Random().nextDouble() * 200 + 50; // Mock data
  }

  int _getActiveServices() {
    final services = widget.healthData['active_services'];
    if (services is num) return services.toInt();
    return 3; // Mock data
  }

  String _getUptime() {
    final uptime = widget.healthData['uptime'];
    if (uptime is String) return uptime;
    return '2h 45m';
  }

  String _getLastCheck() {
    final lastCheck = widget.healthData['last_check'];
    if (lastCheck is String) return lastCheck;
    return 'Just now';
  }

  int _getCacheHitRate() {
    final cacheHit = widget.healthData['cache_hit_rate'];
    if (cacheHit is num) return (cacheHit * 100).toInt();
    return 75;
  }
}

/// Custom Painter for Health Circle
class HealthCirclePainter extends CustomPainter {
  final double progress;
  final Color color;
  final Color backgroundColor;

  HealthCirclePainter({
    required this.progress,
    required this.color,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 8;
    
    // Background circle
    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;
    
    canvas.drawCircle(center, radius, backgroundPaint);
    
    // Progress arc
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;
    
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
} 