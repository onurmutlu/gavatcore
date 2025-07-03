import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/app_state.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

part 'app_providers.g.dart';

// Environment provider
final environmentProvider = Provider<Map<String, dynamic>>((ref) {
  return {
    'api_base_url': ApiConfig.baseUrl,
    'ws_url': ApiConfig.wsUrl,
    'use_mock_data': ApiConfig.useMockData,
    'debug_mode': ApiConfig.enableDebugLogs,
    'environment': const String.fromEnvironment('ENVIRONMENT', defaultValue: 'development'),
  };
});

// App State Notifier
class AppStateNotifier extends StateNotifier<AppStateData> {
  AppStateNotifier() : super(const AppStateData());

  void setSelectedIndex(int index) {
    state = state.copyWith(selectedIndex: index);
  }

  void setConnected(bool connected) {
    state = state.copyWith(isConnected: connected);
  }

  void setLoading(bool loading) {
    state = state.copyWith(isLoading: loading);
  }

  void setError(String? error) {
    state = state.copyWith(errorMessage: error);
  }

  void setTheme(String theme) {
    state = state.copyWith(theme: theme);
  }

  void updateUserPreferences(Map<String, dynamic> preferences) {
    state = state.copyWith(userPreferences: preferences);
  }

  void setCurrentUser(UserAccount? user) {
    state = state.copyWith(currentUser: user);
  }
}

// Enhanced API Service Provider
final enhancedApiServiceProvider = Provider<EnhancedApiService>((ref) {
  final apiService = ApiService();
  return EnhancedApiService(apiService);
});

// Legacy API Service Provider (for backward compatibility)
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

// App State Provider
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppStateData>(
  (ref) => AppStateNotifier(),
);

// Dashboard Stats Provider - Now with real API integration
@riverpod
Future<DashboardStats> dashboardStats(DashboardStatsRef ref) async {
  final enhancedApi = ref.read(enhancedApiServiceProvider);
  
  try {
    print('📊 Fetching dashboard stats from API...');
    final stats = await enhancedApi.getDashboardStats();
    
    // Update connection status on success
    ref.read(appStateProvider.notifier).setConnected(true);
    ref.read(appStateProvider.notifier).setError(null);
    
    return stats;
  } catch (e) {
    print('❌ Dashboard stats API error: $e');
    
    // Update connection status on error
    ref.read(appStateProvider.notifier).setConnected(false);
    ref.read(appStateProvider.notifier).setError('API bağlantı hatası: $e');
    
    // Return mock data as fallback
    return _getFallbackDashboardStats();
  }
}

// Messages Provider - Real API with mock fallback
@riverpod
Future<List<MessageData>> messages(MessagesRef ref) async {
  final enhancedApi = ref.read(enhancedApiServiceProvider);
  
  try {
    print('💬 Fetching messages from API...');
    final messages = await enhancedApi.getMessages(limit: 100);
    
    ref.read(appStateProvider.notifier).setConnected(true);
    return messages;
  } catch (e) {
    print('❌ Messages API error: $e');
    ref.read(appStateProvider.notifier).setConnected(false);
    return _getFallbackMessages();
  }
}

// System Status Provider - Real monitoring
@riverpod
Future<SystemStatus> systemStatus(SystemStatusRef ref) async {
  final enhancedApi = ref.read(enhancedApiServiceProvider);
  
  try {
    print('🖥️ Fetching system status from API...');
    final status = await enhancedApi.getSystemStatus();
    
    ref.read(appStateProvider.notifier).setConnected(true);
    return status;
  } catch (e) {
    print('❌ System status API error: $e');
    ref.read(appStateProvider.notifier).setConnected(false);
    return _getFallbackSystemStatus();
  }
}

// Scheduler Configs Provider
@riverpod
Future<List<SchedulerConfig>> schedulerConfigs(SchedulerConfigsRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('⏰ Fetching scheduler configs from API...');
    return await api.getSchedulerConfigs();
  } catch (e) {
    print('❌ Scheduler configs API error: $e');
    return _getFallbackSchedulerConfigs();
  }
}

// AI Prompts Provider
@riverpod
Future<List<AIPromptData>> aiPrompts(AIPromptsRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('🧠 Fetching AI prompts from API...');
    return await api.getAIPrompts();
  } catch (e) {
    print('❌ AI prompts API error: $e');
    return _getFallbackAIPrompts();
  }
}

// Logs Provider
@riverpod
Future<List<LogEntry>> logs(LogsRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('📋 Fetching logs from API...');
    return await api.getLogs(limit: 200);
  } catch (e) {
    print('❌ Logs API error: $e');
    return _getFallbackLogs();
  }
}

// User Account Provider
@riverpod
Future<UserAccount> userAccount(UserAccountRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('👤 Fetching user account from API...');
    return await api.getAccount();
  } catch (e) {
    print('❌ User account API error: $e');
    return _getFallbackUserAccount();
  }
}

// Characters Provider (GavatCore specific)
@riverpod
Future<List<Map<String, dynamic>>> characters(CharactersRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('🎭 Fetching characters from API...');
    return await api.getCharacters();
  } catch (e) {
    print('❌ Characters API error: $e');
    return _getFallbackCharacters();
  }
}

// Real-time updates provider using WebSocket
@riverpod
Stream<Map<String, dynamic>> realtimeUpdates(RealtimeUpdatesRef ref) async* {
  final wsService = ref.read(webSocketServiceProvider);
  
  try {
    await wsService.connect();
    wsService.subscribeToChannel('dashboard');
    wsService.subscribeToChannel('messages');
    wsService.subscribeToChannel('system');
    
    yield* wsService.messageStream;
  } catch (e) {
    print('❌ WebSocket connection error: $e');
    // Yield mock updates for development
    yield* _getMockRealtimeUpdates();
  }
}

// API Health Provider
@riverpod
Future<Map<String, dynamic>> apiHealth(ApiHealthRef ref) async {
  final api = ref.read(apiServiceProvider);
  
  try {
    print('🏥 Checking API health...');
    return await api.getSystemHealth();
  } catch (e) {
    print('❌ API health check failed: $e');
    return {
      'status': 'error',
      'message': 'API not reachable',
      'timestamp': DateTime.now().toIso8601String(),
      'endpoints': {
        'dashboard': false,
        'messages': false,
        'system': false,
      }
    };
  }
}

// WebSocket Provider
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.dispose());
  return service;
});

// Fallback data generators for development/offline mode
DashboardStats _getFallbackDashboardStats() {
  return DashboardStats(
    totalMessages: 15847,
    todayMessages: 342,
    activeBots: 5,
    totalBots: 8,
    apiCalls: 1247,
    successRate: 94.8,
    systemLoad: 0.67,
    scheduledTasks: 12,
    queuedMessages: 23,
    costToday: 12.45,
    costTotal: 847.32,
    messageChart: [
      ChartData(label: '00:00', value: 12, timestamp: DateTime.now().subtract(const Duration(hours: 6))),
      ChartData(label: '04:00', value: 8, timestamp: DateTime.now().subtract(const Duration(hours: 4))),
      ChartData(label: '08:00', value: 25, timestamp: DateTime.now().subtract(const Duration(hours: 2))),
      ChartData(label: '12:00', value: 42, timestamp: DateTime.now()),
    ],
    botActivityChart: [
      ChartData(label: 'Lara', value: 35, color: '#9C27B0'),
      ChartData(label: 'Geisha', value: 28, color: '#2196F3'),
      ChartData(label: 'Balkız', value: 22, color: '#4CAF50'),
      ChartData(label: 'Mystic', value: 15, color: '#FF9800'),
    ],
  );
}

List<MessageData> _getFallbackMessages() {
  return [
    MessageData(
      id: '1',
      content: 'Selam tatlım, nasılsın bugün? 💋',
      originalContent: 'Merhaba, nasılsın?',
      enhancedContent: 'Selam tatlım, nasılsın bugün? 💋',
      status: 'sent',
      botId: 'lara',
      enhancementType: 'flirty',
      createdAt: DateTime.now().subtract(const Duration(minutes: 5)),
      sentAt: DateTime.now().subtract(const Duration(minutes: 4)),
      targetUserId: 'user123',
    ),
    MessageData(
      id: '2',
      content: 'Burada mısın yoksa uyuyor musun? 😴',
      originalContent: 'Burada mısın?',
      status: 'pending',
      botId: 'geisha',
      enhancementType: 'caring',
      isScheduled: true,
      scheduledAt: DateTime.now().add(const Duration(minutes: 10)),
      createdAt: DateTime.now().subtract(const Duration(minutes: 15)),
      targetUserId: 'user456',
    ),
    MessageData(
      id: '3',
      content: 'Heyyyy! Çok güzel bir gün değil mi? ✨🌟',
      originalContent: 'Güzel gün!',
      enhancedContent: 'Heyyyy! Çok güzel bir gün değil mi? ✨🌟',
      status: 'sent',
      botId: 'balkiz',
      enhancementType: 'bubbly',
      createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      sentAt: DateTime.now().subtract(const Duration(minutes: 58)),
      targetUserId: 'user789',
    ),
  ];
}

SystemStatus _getFallbackSystemStatus() {
  return SystemStatus(
    status: 'running',
    cpuUsage: 45.2,
    memoryUsage: 67.8,
    diskUsage: 23.1,
    activeConnections: 847,
    queueLength: 12,
    maintenanceMode: false,
    lastRestart: DateTime.now().subtract(const Duration(hours: 3)),
    errors: [],
    warnings: ['Mock data - API not connected'],
  );
}

List<SchedulerConfig> _getFallbackSchedulerConfigs() {
  return [
    SchedulerConfig(
      id: '1',
      name: 'Sabah Mesajları',
      cronExpression: '0 9 * * *',
      isActive: true,
      actionType: 'send_message',
      actionParams: {'template': 'morning_greeting'},
      nextRun: DateTime.now().add(const Duration(hours: 16)),
      lastRun: DateTime.now().subtract(const Duration(hours: 8)),
      executionCount: 45,
      createdAt: DateTime.now().subtract(const Duration(days: 15)),
    ),
  ];
}

List<AIPromptData> _getFallbackAIPrompts() {
  return [
    AIPromptData(
      id: '1',
      name: 'Flört Prompt',
      prompt: 'Sen çok çekici ve akıllı bir kadınsın. Her zaman flörtöz ve eğlenceli davranırsın...',
      type: 'flirty',
      isActive: true,
      temperature: 0.8,
      maxTokens: 150,
      model: 'gpt-4o',
      usageCount: 1247,
      avgResponseTime: 2.3,
      createdAt: DateTime.now().subtract(const Duration(days: 30)),
      lastUsed: DateTime.now().subtract(const Duration(minutes: 12)),
    ),
  ];
}

List<LogEntry> _getFallbackLogs() {
  return [
    LogEntry(
      id: '1',
      message: 'Bot Lara başarıyla mesaj gönderdi',
      level: 'info',
      source: 'bot_manager',
      timestamp: DateTime.now().subtract(const Duration(minutes: 2)),
      botId: 'lara',
      userId: 'user123',
      action: 'send_message',
    ),
    LogEntry(
      id: '2',
      message: 'Mock data mode aktif - gerçek API bağlantısı yok',
      level: 'warning',
      source: 'api_service',
      timestamp: DateTime.now().subtract(const Duration(minutes: 1)),
      metadata: {'mock_mode': true},
    ),
  ];
}

UserAccount _getFallbackUserAccount() {
  return UserAccount(
    id: 'user_1',
    email: 'admin@gavatcore.com',
    name: 'GavatCore Admin',
    role: 'admin',
    plan: 'premium',
    balance: 247.85,
    monthlyUsage: 67.3,
    monthlyLimit: 500.0,
    settings: {
      'notifications': true,
      'dark_mode': true,
      'auto_enhance': true,
      'mock_mode': true,
    },
    createdAt: DateTime.now().subtract(const Duration(days: 180)),
    lastLogin: DateTime.now().subtract(const Duration(minutes: 5)),
    isActive: true,
  );
}

List<Map<String, dynamic>> _getFallbackCharacters() {
  return [
    {
      'id': 'lara',
      'name': 'Lara',
      'status': 'active',
      'personality': 'flirty',
      'model': 'gpt-4o',
      'lastActive': DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(),
      'messageCount': 1247,
    },
    {
      'id': 'geisha',
      'name': 'XXXGeisha',
      'status': 'active',
      'personality': 'caring',
      'model': 'gpt-4o',
      'lastActive': DateTime.now().subtract(const Duration(minutes: 15)).toIso8601String(),
      'messageCount': 892,
    },
  ];
}

Stream<Map<String, dynamic>> _getMockRealtimeUpdates() async* {
  while (true) {
    await Future.delayed(const Duration(seconds: 5));
    yield {
      'type': 'dashboard_update',
      'data': {
        'new_message_count': 1,
        'active_users': 847 + (DateTime.now().millisecond % 10),
        'timestamp': DateTime.now().toIso8601String(),
      }
    };
  }
} 