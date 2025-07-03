// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_state.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$AppStateDataImpl _$$AppStateDataImplFromJson(Map<String, dynamic> json) =>
    _$AppStateDataImpl(
      selectedIndex: (json['selectedIndex'] as num?)?.toInt() ?? 0,
      isConnected: json['isConnected'] as bool? ?? false,
      theme: json['theme'] as String? ?? 'light',
      userPreferences:
          json['userPreferences'] as Map<String, dynamic>? ?? const {},
      isLoading: json['isLoading'] as bool? ?? false,
      errorMessage: json['errorMessage'] as String?,
      currentUser: json['currentUser'] == null
          ? null
          : UserAccount.fromJson(json['currentUser'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$$AppStateDataImplToJson(_$AppStateDataImpl instance) =>
    <String, dynamic>{
      'selectedIndex': instance.selectedIndex,
      'isConnected': instance.isConnected,
      'theme': instance.theme,
      'userPreferences': instance.userPreferences,
      'isLoading': instance.isLoading,
      'errorMessage': instance.errorMessage,
      'currentUser': instance.currentUser,
    };

_$DashboardStatsImpl _$$DashboardStatsImplFromJson(Map<String, dynamic> json) =>
    _$DashboardStatsImpl(
      totalMessages: (json['totalMessages'] as num?)?.toInt() ?? 0,
      todayMessages: (json['todayMessages'] as num?)?.toInt() ?? 0,
      activeBots: (json['activeBots'] as num?)?.toInt() ?? 0,
      totalBots: (json['totalBots'] as num?)?.toInt() ?? 0,
      apiCalls: (json['apiCalls'] as num?)?.toInt() ?? 0,
      successRate: (json['successRate'] as num?)?.toDouble() ?? 0.0,
      systemLoad: (json['systemLoad'] as num?)?.toDouble() ?? 0.0,
      scheduledTasks: (json['scheduledTasks'] as num?)?.toInt() ?? 0,
      queuedMessages: (json['queuedMessages'] as num?)?.toInt() ?? 0,
      costToday: (json['costToday'] as num?)?.toDouble() ?? 0.0,
      costTotal: (json['costTotal'] as num?)?.toDouble() ?? 0.0,
      messageChart: (json['messageChart'] as List<dynamic>?)
              ?.map((e) => ChartData.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      botActivityChart: (json['botActivityChart'] as List<dynamic>?)
              ?.map((e) => ChartData.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$DashboardStatsImplToJson(
        _$DashboardStatsImpl instance) =>
    <String, dynamic>{
      'totalMessages': instance.totalMessages,
      'todayMessages': instance.todayMessages,
      'activeBots': instance.activeBots,
      'totalBots': instance.totalBots,
      'apiCalls': instance.apiCalls,
      'successRate': instance.successRate,
      'systemLoad': instance.systemLoad,
      'scheduledTasks': instance.scheduledTasks,
      'queuedMessages': instance.queuedMessages,
      'costToday': instance.costToday,
      'costTotal': instance.costTotal,
      'messageChart': instance.messageChart,
      'botActivityChart': instance.botActivityChart,
    };

_$ChartDataImpl _$$ChartDataImplFromJson(Map<String, dynamic> json) =>
    _$ChartDataImpl(
      label: json['label'] as String,
      value: (json['value'] as num).toDouble(),
      color: json['color'] as String?,
      timestamp: json['timestamp'] == null
          ? null
          : DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$$ChartDataImplToJson(_$ChartDataImpl instance) =>
    <String, dynamic>{
      'label': instance.label,
      'value': instance.value,
      'color': instance.color,
      'timestamp': instance.timestamp?.toIso8601String(),
    };

_$MessageDataImpl _$$MessageDataImplFromJson(Map<String, dynamic> json) =>
    _$MessageDataImpl(
      id: json['id'] as String,
      content: json['content'] as String,
      originalContent: json['originalContent'] as String,
      enhancedContent: json['enhancedContent'] as String?,
      status: json['status'] as String? ?? 'pending',
      botId: json['botId'] as String? ?? 'babagavat',
      enhancementType: json['enhancementType'] as String? ?? 'friendly',
      isScheduled: json['isScheduled'] as bool? ?? false,
      scheduledAt: json['scheduledAt'] == null
          ? null
          : DateTime.parse(json['scheduledAt'] as String),
      sentAt: json['sentAt'] == null
          ? null
          : DateTime.parse(json['sentAt'] as String),
      targetUserId: json['targetUserId'] as String? ?? null,
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$MessageDataImplToJson(_$MessageDataImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'content': instance.content,
      'originalContent': instance.originalContent,
      'enhancedContent': instance.enhancedContent,
      'status': instance.status,
      'botId': instance.botId,
      'enhancementType': instance.enhancementType,
      'isScheduled': instance.isScheduled,
      'scheduledAt': instance.scheduledAt?.toIso8601String(),
      'sentAt': instance.sentAt?.toIso8601String(),
      'targetUserId': instance.targetUserId,
      'metadata': instance.metadata,
      'createdAt': instance.createdAt?.toIso8601String(),
      'updatedAt': instance.updatedAt?.toIso8601String(),
    };

_$SchedulerConfigImpl _$$SchedulerConfigImplFromJson(
        Map<String, dynamic> json) =>
    _$SchedulerConfigImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      cronExpression: json['cronExpression'] as String,
      isActive: json['isActive'] as bool? ?? true,
      actionType: json['actionType'] as String? ?? 'message',
      actionParams: json['actionParams'] as Map<String, dynamic>? ?? const {},
      nextRun: json['nextRun'] == null
          ? null
          : DateTime.parse(json['nextRun'] as String),
      lastRun: json['lastRun'] == null
          ? null
          : DateTime.parse(json['lastRun'] as String),
      executionCount: (json['executionCount'] as num?)?.toInt() ?? 0,
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$SchedulerConfigImplToJson(
        _$SchedulerConfigImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'cronExpression': instance.cronExpression,
      'isActive': instance.isActive,
      'actionType': instance.actionType,
      'actionParams': instance.actionParams,
      'nextRun': instance.nextRun?.toIso8601String(),
      'lastRun': instance.lastRun?.toIso8601String(),
      'executionCount': instance.executionCount,
      'createdAt': instance.createdAt?.toIso8601String(),
    };

_$AIPromptDataImpl _$$AIPromptDataImplFromJson(Map<String, dynamic> json) =>
    _$AIPromptDataImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      prompt: json['prompt'] as String,
      type: json['type'] as String? ?? 'persuasive',
      isActive: json['isActive'] as bool? ?? true,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 0.7,
      maxTokens: (json['maxTokens'] as num?)?.toInt() ?? 150,
      model: json['model'] as String? ?? 'gpt-4o',
      usageCount: (json['usageCount'] as num?)?.toInt() ?? 0,
      avgResponseTime: (json['avgResponseTime'] as num?)?.toDouble() ?? 0.0,
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      lastUsed: json['lastUsed'] == null
          ? null
          : DateTime.parse(json['lastUsed'] as String),
    );

Map<String, dynamic> _$$AIPromptDataImplToJson(_$AIPromptDataImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'prompt': instance.prompt,
      'type': instance.type,
      'isActive': instance.isActive,
      'temperature': instance.temperature,
      'maxTokens': instance.maxTokens,
      'model': instance.model,
      'usageCount': instance.usageCount,
      'avgResponseTime': instance.avgResponseTime,
      'createdAt': instance.createdAt?.toIso8601String(),
      'lastUsed': instance.lastUsed?.toIso8601String(),
    };

_$LogEntryImpl _$$LogEntryImplFromJson(Map<String, dynamic> json) =>
    _$LogEntryImpl(
      id: json['id'] as String,
      message: json['message'] as String,
      level: json['level'] as String? ?? 'info',
      source: json['source'] as String? ?? 'system',
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      timestamp: DateTime.parse(json['timestamp'] as String),
      botId: json['botId'] as String?,
      userId: json['userId'] as String?,
      action: json['action'] as String?,
    );

Map<String, dynamic> _$$LogEntryImplToJson(_$LogEntryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'message': instance.message,
      'level': instance.level,
      'source': instance.source,
      'metadata': instance.metadata,
      'timestamp': instance.timestamp.toIso8601String(),
      'botId': instance.botId,
      'userId': instance.userId,
      'action': instance.action,
    };

_$UserAccountImpl _$$UserAccountImplFromJson(Map<String, dynamic> json) =>
    _$UserAccountImpl(
      id: json['id'] as String,
      email: json['email'] as String,
      name: json['name'] as String,
      role: json['role'] as String? ?? 'user',
      plan: json['plan'] as String? ?? 'free',
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
      monthlyUsage: (json['monthlyUsage'] as num?)?.toDouble() ?? 0.0,
      monthlyLimit: (json['monthlyLimit'] as num?)?.toDouble() ?? 100.0,
      settings: json['settings'] as Map<String, dynamic>? ?? const {},
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      lastLogin: json['lastLogin'] == null
          ? null
          : DateTime.parse(json['lastLogin'] as String),
      isActive: json['isActive'] as bool? ?? true,
    );

Map<String, dynamic> _$$UserAccountImplToJson(_$UserAccountImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'email': instance.email,
      'name': instance.name,
      'role': instance.role,
      'plan': instance.plan,
      'balance': instance.balance,
      'monthlyUsage': instance.monthlyUsage,
      'monthlyLimit': instance.monthlyLimit,
      'settings': instance.settings,
      'createdAt': instance.createdAt?.toIso8601String(),
      'lastLogin': instance.lastLogin?.toIso8601String(),
      'isActive': instance.isActive,
    };

_$SystemStatusImpl _$$SystemStatusImplFromJson(Map<String, dynamic> json) =>
    _$SystemStatusImpl(
      status: json['status'] as String? ?? 'running',
      cpuUsage: (json['cpuUsage'] as num?)?.toDouble() ?? 0.0,
      memoryUsage: (json['memoryUsage'] as num?)?.toDouble() ?? 0.0,
      diskUsage: (json['diskUsage'] as num?)?.toDouble() ?? 0.0,
      activeConnections: (json['activeConnections'] as num?)?.toInt() ?? 0,
      queueLength: (json['queueLength'] as num?)?.toInt() ?? 0,
      maintenanceMode: json['maintenanceMode'] as bool? ?? false,
      lastRestart: json['lastRestart'] == null
          ? null
          : DateTime.parse(json['lastRestart'] as String),
      errors: (json['errors'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$SystemStatusImplToJson(_$SystemStatusImpl instance) =>
    <String, dynamic>{
      'status': instance.status,
      'cpuUsage': instance.cpuUsage,
      'memoryUsage': instance.memoryUsage,
      'diskUsage': instance.diskUsage,
      'activeConnections': instance.activeConnections,
      'queueLength': instance.queueLength,
      'maintenanceMode': instance.maintenanceMode,
      'lastRestart': instance.lastRestart?.toIso8601String(),
      'errors': instance.errors,
      'warnings': instance.warnings,
    };
