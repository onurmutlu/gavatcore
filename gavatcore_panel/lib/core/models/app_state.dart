import 'package:freezed_annotation/freezed_annotation.dart';

part 'app_state.freezed.dart';
part 'app_state.g.dart';

@freezed
class AppStateData with _$AppStateData {
  const factory AppStateData({
    @Default(0) int selectedIndex,
    @Default(false) bool isConnected,
    @Default('light') String theme,
    @Default({}) Map<String, dynamic> userPreferences,
    @Default(false) bool isLoading,
    String? errorMessage,
    @Default(null) UserAccount? currentUser,
  }) = _AppStateData;

  factory AppStateData.fromJson(Map<String, dynamic> json) =>
      _$AppStateDataFromJson(json);
}

@freezed
class DashboardStats with _$DashboardStats {
  const factory DashboardStats({
    @Default(0) int totalMessages,
    @Default(0) int todayMessages,
    @Default(0) int activeBots,
    @Default(0) int totalBots,
    @Default(0) int apiCalls,
    @Default(0.0) double successRate,
    @Default(0.0) double systemLoad,
    @Default(0) int scheduledTasks,
    @Default(0) int queuedMessages,
    @Default(0.0) double costToday,
    @Default(0.0) double costTotal,
    @Default([]) List<ChartData> messageChart,
    @Default([]) List<ChartData> botActivityChart,
  }) = _DashboardStats;

  factory DashboardStats.fromJson(Map<String, dynamic> json) =>
      _$DashboardStatsFromJson(json);
}

@freezed
class ChartData with _$ChartData {
  const factory ChartData({
    required String label,
    required double value,
    String? color,
    DateTime? timestamp,
  }) = _ChartData;

  factory ChartData.fromJson(Map<String, dynamic> json) =>
      _$ChartDataFromJson(json);
}

@freezed
class MessageData with _$MessageData {
  const factory MessageData({
    required String id,
    required String content,
    required String originalContent,
    String? enhancedContent,
    @Default('pending') String status,
    @Default('babagavat') String botId,
    @Default('friendly') String enhancementType,
    @Default(false) bool isScheduled,
    DateTime? scheduledAt,
    DateTime? sentAt,
    @Default(null) String? targetUserId,
    @Default({}) Map<String, dynamic> metadata,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) = _MessageData;

  factory MessageData.fromJson(Map<String, dynamic> json) =>
      _$MessageDataFromJson(json);
}

@freezed
class SchedulerConfig with _$SchedulerConfig {
  const factory SchedulerConfig({
    required String id,
    required String name,
    required String cronExpression,
    @Default(true) bool isActive,
    @Default('message') String actionType,
    @Default({}) Map<String, dynamic> actionParams,
    DateTime? nextRun,
    DateTime? lastRun,
    @Default(0) int executionCount,
    DateTime? createdAt,
  }) = _SchedulerConfig;

  factory SchedulerConfig.fromJson(Map<String, dynamic> json) =>
      _$SchedulerConfigFromJson(json);
}

@freezed
class AIPromptData with _$AIPromptData {
  const factory AIPromptData({
    required String id,
    required String name,
    required String prompt,
    @Default('persuasive') String type,
    @Default(true) bool isActive,
    @Default(0.7) double temperature,
    @Default(150) int maxTokens,
    @Default('gpt-4o') String model,
    @Default(0) int usageCount,
    @Default(0.0) double avgResponseTime,
    DateTime? createdAt,
    DateTime? lastUsed,
  }) = _AIPromptData;

  factory AIPromptData.fromJson(Map<String, dynamic> json) =>
      _$AIPromptDataFromJson(json);
}

@freezed
class LogEntry with _$LogEntry {
  const factory LogEntry({
    required String id,
    required String message,
    @Default('info') String level,
    @Default('system') String source,
    @Default({}) Map<String, dynamic> metadata,
    required DateTime timestamp,
    String? botId,
    String? userId,
    String? action,
  }) = _LogEntry;

  factory LogEntry.fromJson(Map<String, dynamic> json) =>
      _$LogEntryFromJson(json);
}

@freezed
class UserAccount with _$UserAccount {
  const factory UserAccount({
    required String id,
    required String email,
    required String name,
    @Default('user') String role,
    @Default('free') String plan,
    @Default(0.0) double balance,
    @Default(0.0) double monthlyUsage,
    @Default(100.0) double monthlyLimit,
    @Default({}) Map<String, dynamic> settings,
    DateTime? createdAt,
    DateTime? lastLogin,
    @Default(true) bool isActive,
  }) = _UserAccount;

  factory UserAccount.fromJson(Map<String, dynamic> json) =>
      _$UserAccountFromJson(json);
}

@freezed
class SystemStatus with _$SystemStatus {
  const factory SystemStatus({
    @Default('running') String status,
    @Default(0.0) double cpuUsage,
    @Default(0.0) double memoryUsage,
    @Default(0.0) double diskUsage,
    @Default(0) int activeConnections,
    @Default(0) int queueLength,
    @Default(false) bool maintenanceMode,
    DateTime? lastRestart,
    @Default([]) List<String> errors,
    @Default([]) List<String> warnings,
  }) = _SystemStatus;

  factory SystemStatus.fromJson(Map<String, dynamic> json) =>
      _$SystemStatusFromJson(json);
} 