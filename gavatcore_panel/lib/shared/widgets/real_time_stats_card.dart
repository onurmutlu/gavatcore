import 'dart:async';
import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../themes/app_theme.dart';

class RealTimeStatsCard extends StatefulWidget {
  final String title;
  final IconData icon;
  final Color color;
  final String apiEndpoint;
  final String valueKey;
  final String unit;
  final Duration refreshInterval;

  const RealTimeStatsCard({
    super.key,
    required this.title,
    required this.icon,
    required this.color,
    required this.apiEndpoint,
    required this.valueKey,
    this.unit = '',
    this.refreshInterval = const Duration(seconds: 30),
  });

  @override
  State<RealTimeStatsCard> createState() => _RealTimeStatsCardState();
}

class _RealTimeStatsCardState extends State<RealTimeStatsCard>
    with SingleTickerProviderStateMixin {
  Timer? _refreshTimer;
  String _currentValue = '---';
  bool _isLoading = false;
  bool _hasError = false;
  DateTime? _lastUpdate;
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    
    // Animation setup
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    // Initial load and setup timer
    _fetchData();
    _startRefreshTimer();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _animationController.dispose();
    super.dispose();
  }

  void _startRefreshTimer() {
    _refreshTimer = Timer.periodic(widget.refreshInterval, (_) {
      _fetchData();
    });
  }

  Future<void> _fetchData() async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
      _hasError = false;
    });

    try {
      final response = await _apiService.get(widget.apiEndpoint);
      
      final dynamic value = _extractValue(response, widget.valueKey);
      
      setState(() {
        _currentValue = _formatValue(value);
        _lastUpdate = DateTime.now();
        _hasError = false;
      });

      // Trigger pulse animation on update
      _animationController.forward().then((_) {
        _animationController.reverse();
      });

    } catch (e) {
      setState(() {
        _hasError = true;
        _currentValue = 'Error';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  dynamic _extractValue(Map<String, dynamic> response, String key) {
    // Handle nested keys like 'stats.total_users'
    final keys = key.split('.');
    dynamic value = response;
    
    for (final k in keys) {
      if (value is Map<String, dynamic> && value.containsKey(k)) {
        value = value[k];
      } else {
        return null;
      }
    }
    
    return value;
  }

  String _formatValue(dynamic value) {
    if (value == null) return '---';
    
    if (value is num) {
      if (value >= 1000000) {
        return '${(value / 1000000).toStringAsFixed(1)}M';
      } else if (value >= 1000) {
        return '${(value / 1000).toStringAsFixed(1)}K';
      } else {
        return value.toString();
      }
    }
    
    return value.toString();
  }

  String _getTimeAgo() {
    if (_lastUpdate == null) return '';
    
    final now = DateTime.now();
    final diff = now.difference(_lastUpdate!);
    
    if (diff.inSeconds < 60) {
      return '${diff.inSeconds}s ago';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else {
      return '${diff.inHours}h ago';
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _fetchData,
      child: AnimatedBuilder(
        animation: _pulseAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: widget.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: widget.color.withOpacity(0.3),
                  width: 1,
                ),
                boxShadow: [
                  BoxShadow(
                    color: widget.color.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Icon with loading indicator
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      Icon(
                        widget.icon,
                        color: _hasError ? Colors.red : widget.color,
                        size: 32,
                      ),
                      if (_isLoading)
                        SizedBox(
                          width: 40,
                          height: 40,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(widget.color),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  
                  // Value
                  Text(
                    '$_currentValue${widget.unit}',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: _hasError ? Colors.red : widget.color,
                    ),
                  ),
                  const SizedBox(height: 4),
                  
                  // Title
                  Text(
                    widget.title,
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppTheme.textColorSecondary,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  // Last update time
                  if (_lastUpdate != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      _getTimeAgo(),
                      style: TextStyle(
                        fontSize: 10,
                        color: AppTheme.textColorSecondary.withOpacity(0.7),
                      ),
                    ),
                  ],
                  
                  // Status indicator
                  const SizedBox(height: 8),
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: _hasError 
                          ? Colors.red 
                          : _isLoading 
                              ? Colors.orange 
                              : Colors.green,
                      shape: BoxShape.circle,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
} 