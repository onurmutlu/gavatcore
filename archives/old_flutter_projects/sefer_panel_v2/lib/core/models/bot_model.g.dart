// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bot_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BotModel _$BotModelFromJson(Map<String, dynamic> json) => BotModel(
      id: json['id'] as String,
      username: json['username'] as String,
      token: json['token'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      isActive: json['isActive'] as bool,
      type: $enumDecode(_$BotTypeEnumMap, json['type']),
      role: $enumDecode(_$BotRoleEnumMap, json['role']),
      settings: json['settings'] as Map<String, dynamic>,
      createdAt: DateTime.parse(json['createdAt'] as String),
      lastActive: json['lastActive'] == null
          ? null
          : DateTime.parse(json['lastActive'] as String),
      stats: BotStats.fromJson(json['stats'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$BotModelToJson(BotModel instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'token': instance.token,
      'name': instance.name,
      'description': instance.description,
      'isActive': instance.isActive,
      'type': _$BotTypeEnumMap[instance.type]!,
      'role': _$BotRoleEnumMap[instance.role]!,
      'settings': instance.settings,
      'createdAt': instance.createdAt.toIso8601String(),
      'lastActive': instance.lastActive?.toIso8601String(),
      'stats': instance.stats,
    };

const _$BotTypeEnumMap = {
  BotType.ai: 'ai',
  BotType.admin: 'admin',
  BotType.support: 'support',
  BotType.showcase: 'showcase',
  BotType.system: 'system',
};

const _$BotRoleEnumMap = {
  BotRole.primary: 'primary',
  BotRole.secondary: 'secondary',
  BotRole.assistant: 'assistant',
  BotRole.monitor: 'monitor',
};

BotStats _$BotStatsFromJson(Map<String, dynamic> json) => BotStats(
      totalMessages: (json['totalMessages'] as num).toInt(),
      activeUsers: (json['activeUsers'] as num).toInt(),
      averageResponseTime: (json['averageResponseTime'] as num).toDouble(),
      aiRating: (json['aiRating'] as num).toDouble(),
      commandUsage: Map<String, int>.from(json['commandUsage'] as Map),
      errorCounts: Map<String, int>.from(json['errorCounts'] as Map),
    );

Map<String, dynamic> _$BotStatsToJson(BotStats instance) => <String, dynamic>{
      'totalMessages': instance.totalMessages,
      'activeUsers': instance.activeUsers,
      'averageResponseTime': instance.averageResponseTime,
      'aiRating': instance.aiRating,
      'commandUsage': instance.commandUsage,
      'errorCounts': instance.errorCounts,
    };
