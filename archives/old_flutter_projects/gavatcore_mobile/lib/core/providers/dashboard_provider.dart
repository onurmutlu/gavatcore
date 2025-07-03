import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/bot_status.dart';
import '../models/dashboard_analytics.dart';
import '../models/log_entry.dart';
import '../services/dashboard_api_service.dart';
import '../services/api_service.dart';

class DashboardProvider with ChangeNotifier {
  final DashboardApiService _apiService = DashboardApiService();
  
  // State
  List<BotStatus> _bots = [];
  DashboardAnalytics? _analytics;
  List<LogEntry> _logs = [];
  Map<String, dynamic> _systemHealth = {};
  bool _isLoading = false;
  String? _error;
  Timer? _refreshTimer;

  // Getters
  List<BotStatus> get bots => _bots;
  DashboardAnalytics? get analytics => _analytics;
  List<LogEntry> get logs => _logs;
  Map<String, dynamic> get systemHealth => _systemHealth;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Statistics
  int get runningBots => _bots.where((bot) => bot.isRunning).length;
  int get stoppedBots => _bots.where((bot) => bot.isStopped).length;
  int get errorBots => _bots.where((bot) => bot.hasError).length;
  int get totalMessages => _bots.fold(0, (sum, bot) => sum + bot.messagesSent);
  double get avgUptime => _bots.isEmpty 
      ? 0 
      : _bots.fold(0.0, (sum, bot) => sum + bot.uptime) / _bots.length;

  DashboardProvider() {
    _initialize();
  }

  void _initialize() {
    loadDashboardData();
    _startPeriodicRefresh();
  }

  void _startPeriodicRefresh() {
    _refreshTimer = Timer.periodic(Duration(seconds: 10), (timer) {
      refreshData();
    });
  }

  Future<void> loadDashboardData() async {
    _setLoading(true);
    try {
      await Future.wait([
        _loadBots(),
        _loadAnalytics(),
        _loadLogs(),
        _loadSystemHealth(),
      ]);
      _clearError();
    } catch (e) {
      _setError('Dashboard yüklenirken hata: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> refreshData() async {
    try {
      await Future.wait([
        _loadBots(),
        _loadLogs(),
        _loadSystemHealth(),
      ]);
      _clearError();
    } catch (e) {
      _setError('Veri yenilenirken hata: $e');
    }
  }

  Future<void> _loadBots() async {
    try {
      _bots = await _apiService.getBotStatuses();
      notifyListeners();
    } catch (e) {
      // Use mock data if API fails
      _bots = _getMockBots();
      notifyListeners();
    }
  }

  Future<void> _loadAnalytics() async {
    try {
      _analytics = await _apiService.getAnalytics();
      notifyListeners();
    } catch (e) {
      debugPrint('Analytics load error: $e');
    }
  }

  Future<void> _loadLogs() async {
    try {
      _logs = await _apiService.getRecentLogs();
      notifyListeners();
    } catch (e) {
      debugPrint('Logs load error: $e');
    }
  }

  Future<void> _loadSystemHealth() async {
    try {
      _systemHealth = await _apiService.getSystemHealth();
      notifyListeners();
    } catch (e) {
      debugPrint('System health load error: $e');
    }
  }

  // Bot control methods
  Future<bool> startBot(String botId) async {
    try {
      final success = await _apiService.startBot(botId);
      if (success) {
        await _loadBots(); // Refresh bot status
        return true;
      }
      return false;
    } catch (e) {
      _setError('Bot başlatılırken hata: $e');
      return false;
    }
  }

  Future<bool> stopBot(String botId) async {
    try {
      final success = await _apiService.stopBot(botId);
      if (success) {
        await _loadBots(); // Refresh bot status
        return true;
      }
      return false;
    } catch (e) {
      _setError('Bot durdurulurken hata: $e');
      return false;
    }
  }

  Future<bool> restartBot(String botId) async {
    try {
      final success = await _apiService.restartBot(botId);
      if (success) {
        await _loadBots(); // Refresh bot status
        return true;
      }
      return false;
    } catch (e) {
      _setError('Bot yeniden başlatılırken hata: $e');
      return false;
    }
  }

  Future<bool> startAllBots() async {
    try {
      final success = await _apiService.startAllBots();
      if (success) {
        await _loadBots(); // Refresh all bot statuses
        return true;
      }
      return false;
    } catch (e) {
      _setError('Tüm botlar başlatılırken hata: $e');
      return false;
    }
  }

  Future<bool> stopAllBots() async {
    try {
      final success = await _apiService.stopAllBots();
      if (success) {
        await _loadBots(); // Refresh all bot statuses
        return true;
      }
      return false;
    } catch (e) {
      _setError('Tüm botlar durdurulurken hata: $e');
      return false;
    }
  }

  // Helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
    notifyListeners();
  }

  BotStatus? getBotById(String botId) {
    try {
      return _bots.firstWhere((bot) => bot.id == botId);
    } catch (e) {
      return null;
    }
  }

  // Mock data for demo - 3 Ana Karakter Bot
  List<BotStatus> _getMockBots() {
    return [
      BotStatus(
        id: 'babagavat',
        name: 'BabaGavat',
        description: 'Sokak lideri, para babası, alfa erkek bot',
        status: 'running',
        pid: 12001,
        uptime: 185.5, // 3+ hours
        messagesSent: 1847,
        memoryUsage: 45.6,
        cpuUsage: 12.3,
        lastRestart: DateTime.now().subtract(Duration(hours: 3)),
        restartCount: 2,
        performer: 'BabaGavat K.',
        telegramHandle: '@babagavat',
        autoRestart: true,
      ),
      BotStatus(
        id: 'lara',
        name: 'Lara',
        description: 'Premium yayıncı, aşık edici performanslar',
        status: 'running',
        pid: 12002,
        uptime: 95.2, // 1.5+ hours
        messagesSent: 892,
        memoryUsage: 38.9,
        cpuUsage: 8.7,
        lastRestart: DateTime.now().subtract(Duration(hours: 2)),
        restartCount: 1,
        performer: 'Lara Y.',
        telegramHandle: '@yayincilara',
        autoRestart: true,
      ),
      BotStatus(
        id: 'geisha',
        name: 'Geisha',
        description: 'Baştan çıkarıcı, tutku dolu deneyimler',
        status: 'stopped',
        pid: null,
        uptime: 0,
        messagesSent: 1456,
        memoryUsage: 0,
        cpuUsage: 0,
        lastRestart: DateTime.now().subtract(Duration(hours: 1)),
        restartCount: 3,
        performer: 'Geisha Y.',
        telegramHandle: '@xxxgeisha',
        autoRestart: false,
      ),
    ];
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
} 