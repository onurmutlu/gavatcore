class DashboardAnalytics {
  final Map<String, int> categoryDistribution;
  final List<DailyPostData> dailyPosts;
  final List<EngagementData> engagementHistory;
  final RevenueData revenue;
  final SystemHealth systemHealth;

  DashboardAnalytics({
    required this.categoryDistribution,
    required this.dailyPosts,
    required this.engagementHistory,
    required this.revenue,
    required this.systemHealth,
  });

  factory DashboardAnalytics.fromJson(Map<String, dynamic> json) {
    return DashboardAnalytics(
      categoryDistribution: Map<String, int>.from(json['category_distribution'] ?? {}),
      dailyPosts: (json['daily_posts'] as List? ?? [])
          .map((e) => DailyPostData.fromJson(e))
          .toList(),
      engagementHistory: (json['engagement_history'] as List? ?? [])
          .map((e) => EngagementData.fromJson(e))
          .toList(),
      revenue: RevenueData.fromJson(json['revenue'] ?? {}),
      systemHealth: SystemHealth.fromJson(json['system_health'] ?? {}),
    );
  }
}

class DailyPostData {
  final DateTime date;
  final int postsCount;
  final double avgEngagement;

  DailyPostData({
    required this.date,
    required this.postsCount,
    required this.avgEngagement,
  });

  factory DailyPostData.fromJson(Map<String, dynamic> json) {
    return DailyPostData(
      date: DateTime.parse(json['date']),
      postsCount: json['posts_count'] ?? 0,
      avgEngagement: (json['avg_engagement'] ?? 0).toDouble(),
    );
  }
}

class EngagementData {
  final DateTime timestamp;
  final double score;
  final String category;

  EngagementData({
    required this.timestamp,
    required this.score,
    required this.category,
  });

  factory EngagementData.fromJson(Map<String, dynamic> json) {
    return EngagementData(
      timestamp: DateTime.parse(json['timestamp']),
      score: (json['score'] ?? 0).toDouble(),
      category: json['category'] ?? '',
    );
  }
}

class RevenueData {
  final double dailyRevenue;
  final double weeklyRevenue;
  final double monthlyRevenue;
  final String currency;

  RevenueData({
    required this.dailyRevenue,
    required this.weeklyRevenue,
    required this.monthlyRevenue,
    required this.currency,
  });

  factory RevenueData.fromJson(Map<String, dynamic> json) {
    return RevenueData(
      dailyRevenue: (json['daily_revenue'] ?? 0).toDouble(),
      weeklyRevenue: (json['weekly_revenue'] ?? 0).toDouble(),
      monthlyRevenue: (json['monthly_revenue'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'TRY',
    );
  }
}

class SystemHealth {
  final double cpuUsage;
  final double memoryUsage;
  final double diskUsage;
  final int activeConnections;
  final double uptime;

  SystemHealth({
    required this.cpuUsage,
    required this.memoryUsage,
    required this.diskUsage,
    required this.activeConnections,
    required this.uptime,
  });

  factory SystemHealth.fromJson(Map<String, dynamic> json) {
    return SystemHealth(
      cpuUsage: (json['cpu_usage'] ?? 0).toDouble(),
      memoryUsage: (json['memory_usage'] ?? 0).toDouble(),
      diskUsage: (json['disk_usage'] ?? 0).toDouble(),
      activeConnections: json['active_connections'] ?? 0,
      uptime: (json['uptime'] ?? 0).toDouble(),
    );
  }
} 