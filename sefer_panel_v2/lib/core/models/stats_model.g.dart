// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stats_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StatsModel _$StatsModelFromJson(Map<String, dynamic> json) => StatsModel(
      totalMessages: (json['totalMessages'] as num).toInt(),
      activeUsers: (json['activeUsers'] as num).toInt(),
      totalBots: (json['totalBots'] as num).toInt(),
      averageAiRating: (json['averageAiRating'] as num).toDouble(),
      totalRevenue: (json['totalRevenue'] as num).toDouble(),
      messagesByType: Map<String, int>.from(json['messagesByType'] as Map),
      revenueBySource: (json['revenueBySource'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      dailyStats: (json['dailyStats'] as List<dynamic>)
          .map((e) => DailyStats.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$StatsModelToJson(StatsModel instance) =>
    <String, dynamic>{
      'totalMessages': instance.totalMessages,
      'activeUsers': instance.activeUsers,
      'totalBots': instance.totalBots,
      'averageAiRating': instance.averageAiRating,
      'totalRevenue': instance.totalRevenue,
      'messagesByType': instance.messagesByType,
      'revenueBySource': instance.revenueBySource,
      'dailyStats': instance.dailyStats,
    };

DailyStats _$DailyStatsFromJson(Map<String, dynamic> json) => DailyStats(
      date: DateTime.parse(json['date'] as String),
      messageCount: (json['messageCount'] as num).toInt(),
      activeUsers: (json['activeUsers'] as num).toInt(),
      revenue: (json['revenue'] as num).toDouble(),
      aiRating: (json['aiRating'] as num).toDouble(),
    );

Map<String, dynamic> _$DailyStatsToJson(DailyStats instance) =>
    <String, dynamic>{
      'date': instance.date.toIso8601String(),
      'messageCount': instance.messageCount,
      'activeUsers': instance.activeUsers,
      'revenue': instance.revenue,
      'aiRating': instance.aiRating,
    };
