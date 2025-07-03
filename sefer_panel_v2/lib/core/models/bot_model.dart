import 'package:json_annotation/json_annotation.dart';

part 'bot_model.g.dart';

@JsonSerializable()
class BotModel {
  final String id;
  final String username;
  final String token;
  final String name;
  final String description;
  final bool isActive;
  final BotType type;
  final BotRole role;
  final Map<String, dynamic> settings;
  final DateTime createdAt;
  final DateTime? lastActive;
  final BotStats stats;

  BotModel({
    required this.id,
    required this.username,
    required this.token,
    required this.name,
    required this.description,
    required this.isActive,
    required this.type,
    required this.role,
    required this.settings,
    required this.createdAt,
    this.lastActive,
    required this.stats,
  });

  factory BotModel.fromJson(Map<String, dynamic> json) => _$BotModelFromJson(json);
  Map<String, dynamic> toJson() => _$BotModelToJson(this);
}

enum BotType {
  ai,
  admin,
  support,
  showcase,
  system,
}

enum BotRole {
  primary,
  secondary,
  assistant,
  monitor,
}

@JsonSerializable()
class BotStats {
  final int totalMessages;
  final int activeUsers;
  final double averageResponseTime;
  final double aiRating;
  final Map<String, int> commandUsage;
  final Map<String, int> errorCounts;

  BotStats({
    required this.totalMessages,
    required this.activeUsers,
    required this.averageResponseTime,
    required this.aiRating,
    required this.commandUsage,
    required this.errorCounts,
  });

  factory BotStats.fromJson(Map<String, dynamic> json) => _$BotStatsFromJson(json);
  Map<String, dynamic> toJson() => _$BotStatsToJson(this);
} 