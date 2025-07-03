import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/models/app_state.dart';
import '../../../core/services/api_service.dart';

part 'dashboard_providers.g.dart';

// Dashboard Stats Provider
@riverpod
class DashboardStats extends _$DashboardStats {
  @override
  Future<DashboardStatsData> build() async {
    // Simulate API call
    await Future.delayed(const Duration(seconds: 1));
    
    return const DashboardStatsData(
      totalMessages: 1247,
      activeBots: 6,
      scheduledTasks: 23,
      systemLoad: 0.65,
      errorCount: 2,
      lastUpdate: '2 minutes ago',
    );
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 1));
      
      return DashboardStatsData(
        totalMessages: 1247 + (DateTime.now().millisecond % 100),
        activeBots: 6,
        scheduledTasks: 23,
        systemLoad: 0.65 + (DateTime.now().millisecond % 30) / 100,
        errorCount: DateTime.now().millisecond % 5,
        lastUpdate: 'Just now',
      );
    });
  }
}

// Real-time Updates Provider
@riverpod
class RealTimeUpdates extends _$RealTimeUpdates {
  @override
  Stream<Map<String, dynamic>> build() async* {
    while (true) {
      await Future.delayed(const Duration(seconds: 5));
      yield {
        'timestamp': DateTime.now().toIso8601String(),
        'messageCount': DateTime.now().millisecond % 100,
        'systemLoad': (DateTime.now().millisecond % 80) / 100,
        'activeConnections': 3 + (DateTime.now().millisecond % 5),
      };
    }
  }
}

// System Status Provider
@riverpod
class SystemStatus extends _$SystemStatus {
  @override
  Map<String, dynamic> build() {
    return {
      'api_server': 'online',
      'redis': 'online',
      'telegram_bots': 'online',
      'scheduler': 'online',
      'ai_service': 'online',
    };
  }

  void updateStatus(String service, String status) {
    state = {...state, service: status};
  }
}

// Quick Actions Provider
@riverpod
class QuickActions extends _$QuickActions {
  @override
  bool build() {
    return false; // Not processing
  }

  Future<void> startAllBots() async {
    state = true;
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      // Update system status
      ref.read(systemStatusProvider.notifier).updateStatus('telegram_bots', 'online');
    } finally {
      state = false;
    }
  }

  Future<void> stopAllBots() async {
    state = true;
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      // Update system status
      ref.read(systemStatusProvider.notifier).updateStatus('telegram_bots', 'offline');
    } finally {
      state = false;
    }
  }

  Future<void> restartSystem() async {
    state = true;
    try {
      // Simulate restart process
      await Future.delayed(const Duration(seconds: 3));
      // Refresh all data
      ref.invalidate(dashboardStatsProvider);
    } finally {
      state = false;
    }
  }
} 