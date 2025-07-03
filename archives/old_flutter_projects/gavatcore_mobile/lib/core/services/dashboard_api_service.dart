import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/bot_status.dart';
import '../models/dashboard_analytics.dart';
import '../models/log_entry.dart';

class DashboardApiService {
  static const String baseUrl = 'http://localhost:5004/api';
  static const Duration timeout = Duration(seconds: 10);

  // Singleton pattern
  static final DashboardApiService _instance = DashboardApiService._internal();
  factory DashboardApiService() => _instance;
  DashboardApiService._internal();

  Future<List<BotStatus>> getBotStatuses() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/bots'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> botsData = data['bots'] ?? [];
        
        return botsData.map((bot) => BotStatus.fromJson(bot)).toList();
      } else {
        throw Exception('Failed to load bot statuses: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<BotStatus> getBotStatus(String botId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/bot/$botId/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return BotStatus.fromJson(data['bot']);
      } else {
        throw Exception('Failed to load bot status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<bool> startBot(String botId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bot/$botId/start'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }
      return false;
    } catch (e) {
      throw Exception('Failed to start bot: $e');
    }
  }

  Future<bool> stopBot(String botId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bot/$botId/stop'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }
      return false;
    } catch (e) {
      throw Exception('Failed to stop bot: $e');
    }
  }

  Future<bool> restartBot(String botId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/bot/$botId/restart'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }
      return false;
    } catch (e) {
      throw Exception('Failed to restart bot: $e');
    }
  }

  Future<bool> startAllBots() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/system/start'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }
      return false;
    } catch (e) {
      throw Exception('Failed to start all bots: $e');
    }
  }

  Future<bool> stopAllBots() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/system/stop'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['success'] == true;
      }
      return false;
    } catch (e) {
      throw Exception('Failed to stop all bots: $e');
    }
  }

  Future<DashboardAnalytics> getAnalytics() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/analytics'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return DashboardAnalytics.fromJson(data);
      } else {
        // Return mock data if analytics endpoint not available
        return _getMockAnalytics();
      }
    } catch (e) {
      // Return mock data for demo purposes
      return _getMockAnalytics();
    }
  }

  Future<List<LogEntry>> getRecentLogs() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/logs/recent'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> logsData = data['logs'] ?? [];
        
        return logsData.map((log) => LogEntry.fromJson(log)).toList();
      } else {
        return _getMockLogs();
      }
    } catch (e) {
      return _getMockLogs();
    }
  }

  Future<Map<String, dynamic>> getSystemHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/system/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return _getMockSystemHealth();
      }
    } catch (e) {
      return _getMockSystemHealth();
    }
  }

  Future<Map<String, dynamic>> getSystemStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/system/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return _getMockSystemStatus();
      }
    } catch (e) {
      return _getMockSystemStatus();
    }
  }

  Future<Map<String, dynamic>> getCampaignStats() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/campaigns/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(timeout);

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return _getMockCampaignStats();
      }
    } catch (e) {
      return _getMockCampaignStats();
    }
  }

  // Mock data methods for demo
  DashboardAnalytics _getMockAnalytics() {
    return DashboardAnalytics(
      categoryDistribution: {
        'motivation': 4,
        'lifestyle': 3,
        'tech': 3,
        'business': 2,
      },
      dailyPosts: [
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 6)),
          postsCount: 12,
          avgEngagement: 85.5,
        ),
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 5)),
          postsCount: 11,
          avgEngagement: 78.2,
        ),
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 4)),
          postsCount: 13,
          avgEngagement: 92.1,
        ),
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 3)),
          postsCount: 10,
          avgEngagement: 76.8,
        ),
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 2)),
          postsCount: 12,
          avgEngagement: 88.4,
        ),
        DailyPostData(
          date: DateTime.now().subtract(Duration(days: 1)),
          postsCount: 14,
          avgEngagement: 94.7,
        ),
        DailyPostData(
          date: DateTime.now(),
          postsCount: 8,
          avgEngagement: 91.2,
        ),
      ],
      engagementHistory: [],
      revenue: RevenueData(
        dailyRevenue: 2840.50,
        weeklyRevenue: 18925.30,
        monthlyRevenue: 75680.90,
        currency: 'TRY',
      ),
      systemHealth: SystemHealth(
        cpuUsage: 23.5,
        memoryUsage: 67.8,
        diskUsage: 45.2,
        activeConnections: 156,
        uptime: 4320.5, // 3 days
      ),
    );
  }

  List<LogEntry> _getMockLogs() {
    return [
      LogEntry(
        timestamp: DateTime.now().subtract(Duration(minutes: 2)).toIso8601String(),
        level: 'INFO',
        message: 'BabaGavat bot mesaj gönderildi: @user123',
        source: 'babagavat',
      ),
      LogEntry(
        timestamp: DateTime.now().subtract(Duration(minutes: 5)).toIso8601String(),
        level: 'INFO',
        message: 'Lara bot yeni kullanıcı kaydı: premium_user_456',
        source: 'lara',
      ),
      LogEntry(
        timestamp: DateTime.now().subtract(Duration(minutes: 8)).toIso8601String(),
        level: 'WARNING',
        message: 'Rate limit yaklaşılıyor - cooldown aktif',
        source: 'system',
      ),
      LogEntry(
        timestamp: DateTime.now().subtract(Duration(minutes: 12)).toIso8601String(),
        level: 'INFO',
        message: 'SeferVerse post yayınlandı: motivation kategori',
        source: 'ai_pipeline',
      ),
      LogEntry(
        timestamp: DateTime.now().subtract(Duration(minutes: 15)).toIso8601String(),
        level: 'INFO',
        message: 'Geisha bot grup mesajı yanıtlandı',
        source: 'geisha',
      ),
    ];
  }

  Map<String, dynamic> _getMockSystemHealth() {
    return {
      'status': 'healthy',
      'cpu_usage': 23.5,
      'memory_usage': 67.8,
      'disk_usage': 45.2,
      'active_connections': 156,
      'uptime': 4320.5,
    };
  }

  Map<String, dynamic> _getMockSystemStatus() {
    return {
      'api_status': 'Online',
      'db_status': 'Connected',
      'bot_count': 3,
      'active_sessions': 156,
      'uptime': '3d 2h 15m',
      'last_update': DateTime.now().toIso8601String(),
    };
  }

  Map<String, dynamic> _getMockCampaignStats() {
    return {
      'total_posts': 247,
      'weekly_posts': 35,
      'engagement_rate': 87.5,
      'active_campaigns': 5,
      'conversion_rate': 12.3,
      'revenue': 15420.50,
    };
  }
} 