import 'package:json_annotation/json_annotation.dart';

part 'stats_model.g.dart';

@JsonSerializable()
class StatsModel {
  final int totalMessages;
  final int activeUsers;
  final int totalBots;
  final double averageAiRating;
  final double totalRevenue;
  final Map<String, int> messagesByType;
  final Map<String, double> revenueBySource;
  final List<DailyStats> dailyStats;

  StatsModel({
    required this.totalMessages,
    required this.activeUsers,
    required this.totalBots,
    required this.averageAiRating,
    required this.totalRevenue,
    required this.messagesByType,
    required this.revenueBySource,
    required this.dailyStats,
  });

  factory StatsModel.fromJson(Map<String, dynamic> json) => _$StatsModelFromJson(json);
  Map<String, dynamic> toJson() => _$StatsModelToJson(this);
}

@JsonSerializable()
class DailyStats {
  final DateTime date;
  final int messageCount;
  final int activeUsers;
  final double revenue;
  final double aiRating;

  DailyStats({
    required this.date,
    required this.messageCount,
    required this.activeUsers,
    required this.revenue,
    required this.aiRating,
  });

  factory DailyStats.fromJson(Map<String, dynamic> json) => _$DailyStatsFromJson(json);
  Map<String, dynamic> toJson() => _$DailyStatsToJson(this);
} 