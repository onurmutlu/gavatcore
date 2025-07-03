import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/app_state.dart';

part 'api_service.g.dart';

// Environment configuration
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api',
  );
  
  static const String wsUrl = String.fromEnvironment(
    'WS_URL', 
    defaultValue: 'ws://localhost:8000/ws',
  );
  
  static const bool useMockData = bool.fromEnvironment(
    'USE_MOCK_DATA',
    defaultValue: true, // Development için default true
  );
  
  static const bool enableDebugLogs = bool.fromEnvironment(
    'DEBUG_API',
    defaultValue: true,
  );
}

@RestApi(baseUrl: "")
abstract class ApiService {
  factory ApiService([Dio? dio]) {
    dio ??= _createDio();
    return _ApiService(dio, baseUrl: ApiConfig.baseUrl);
  }

  // Dashboard endpoints - GavatCore gerçek API
  @GET("/dashboard/stats")
  Future<DashboardStats> getDashboardStats();

  @POST("/dashboard/refresh")
  Future<Map<String, dynamic>> refreshDashboard();

  // Message Pool endpoints - GavatCore real endpoints
  @GET("/message-pools/list")
  Future<List<MessageData>> getMessages({
    @Query("page") int page = 1,
    @Query("limit") int limit = 50,
    @Query("status") String? status,
    @Query("bot_id") String? botId,
    @Query("search") String? search,
  });

  @POST("/message-pools/create")
  Future<MessageData> createMessage(@Body() Map<String, dynamic> message);

  @PUT("/message-pools/{id}")
  Future<MessageData> updateMessage(
    @Path("id") String id,
    @Body() Map<String, dynamic> message,
  );

  @DELETE("/message-pools/{id}")
  Future<void> deleteMessage(@Path("id") String id);

  @POST("/message-pools/bulk-delete")
  Future<void> bulkDeleteMessages(@Body() Map<String, dynamic> request);

  @POST("/message-pools/enhance")
  Future<MessageData> enhanceMessage(
    @Path("id") String id,
    @Body() Map<String, dynamic> request,
  );

  // Scheduler endpoints - GavatCore integration
  @GET("/scheduler/configs")
  Future<List<SchedulerConfig>> getSchedulerConfigs();

  @POST("/scheduler/configs")
  Future<SchedulerConfig> createSchedulerConfig(
    @Body() Map<String, dynamic> config,
  );

  @PUT("/scheduler/configs/{id}")
  Future<SchedulerConfig> updateSchedulerConfig(
    @Path("id") String id,
    @Body() Map<String, dynamic> config,
  );

  @DELETE("/scheduler/configs/{id}")
  Future<void> deleteSchedulerConfig(@Path("id") String id);

  @POST("/scheduler/configs/{id}/toggle")
  Future<SchedulerConfig> toggleSchedulerConfig(@Path("id") String id);

  // AI Prompts endpoints - AI Blending integration
  @GET("/ai/prompts")
  Future<List<AIPromptData>> getAIPrompts();

  @POST("/ai/prompts")
  Future<AIPromptData> createAIPrompt(@Body() Map<String, dynamic> prompt);

  @PUT("/ai/prompts/{id}")
  Future<AIPromptData> updateAIPrompt(
    @Path("id") String id,
    @Body() Map<String, dynamic> prompt,
  );

  @DELETE("/ai/prompts/{id}")
  Future<void> deleteAIPrompt(@Path("id") String id);

  @POST("/ai/enhance-message")
  Future<Map<String, dynamic>> enhanceMessage(
    @Body() Map<String, dynamic> request,
  );

  @POST("/ai/test-prompt")
  Future<Map<String, dynamic>> testPrompt(
    @Body() Map<String, dynamic> request,
  );

  // Logs endpoints - Real-time sistem logları
  @GET("/logs/list")
  Future<List<LogEntry>> getLogs({
    @Query("level") String? level,
    @Query("source") String? source,
    @Query("limit") int limit = 100,
    @Query("start_date") String? startDate,
    @Query("end_date") String? endDate,
  });

  @DELETE("/logs/clear")
  Future<void> clearLogs();

  @GET("/logs/export")
  Future<Map<String, dynamic>> exportLogs({
    @Query("format") String format = "json",
  });

  // Account & Billing endpoints - User management
  @GET("/account/profile")
  Future<UserAccount> getAccount();

  @PUT("/account/profile")
  Future<UserAccount> updateAccount(@Body() Map<String, dynamic> account);

  @GET("/billing/usage")
  Future<Map<String, dynamic>> getBillingUsage();

  @GET("/billing/invoices")
  Future<List<Map<String, dynamic>>> getInvoices();

  @POST("/billing/payment")
  Future<Map<String, dynamic>> createPayment(
    @Body() Map<String, dynamic> payment,
  );

  // Admin endpoints - System control
  @POST("/admin/bots/start")
  Future<Map<String, dynamic>> startBots(@Body() Map<String, dynamic> config);

  @POST("/admin/bots/stop")
  Future<Map<String, dynamic>> stopBots(@Body() Map<String, dynamic> config);

  @POST("/admin/bots/restart")
  Future<Map<String, dynamic>> restartBots(@Body() Map<String, dynamic> config);

  @POST("/admin/system/restart")
  Future<Map<String, dynamic>> restartSystem();

  @GET("/admin/system/status")
  Future<SystemStatus> getSystemStatus();

  @GET("/admin/system/health")
  Future<Map<String, dynamic>> getSystemHealth();

  @POST("/admin/maintenance/toggle")
  Future<Map<String, dynamic>> toggleMaintenanceMode();

  // FailSafe endpoints - Emergency controls
  @POST("/admin/failsafe/emergency-stop")
  Future<Map<String, dynamic>> emergencyStop();

  @POST("/admin/failsafe/reset-all")
  Future<Map<String, dynamic>> failsafeResetAll();

  @POST("/admin/failsafe/clear-sessions")
  Future<Map<String, dynamic>> clearAllSessions();

  @POST("/admin/failsafe/reset-database")
  Future<Map<String, dynamic>> resetDatabase(@Body() Map<String, dynamic> config);

  // Character Management - GavatCore characters
  @GET("/characters/list")
  Future<List<Map<String, dynamic>>> getCharacters();

  @GET("/characters/{id}")
  Future<Map<String, dynamic>> getCharacter(@Path("id") String id);

  @PUT("/characters/{id}")
  Future<Map<String, dynamic>> updateCharacter(
    @Path("id") String id,
    @Body() Map<String, dynamic> character,
  );

  @POST("/characters/{id}/test")
  Future<Map<String, dynamic>> testCharacter(
    @Path("id") String id,
    @Body() Map<String, dynamic> request,
  );
}

// Dio configuration with interceptors
Dio _createDio() {
  final dio = Dio();
  
  // Base configuration
  dio.options.connectTimeout = const Duration(seconds: 30);
  dio.options.receiveTimeout = const Duration(seconds: 30);
  dio.options.sendTimeout = const Duration(seconds: 30);
  
  // Headers
  dio.options.headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'GavatCore-Panel/1.0',
  };

  // Auth interceptor
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token if available
        // final token = await getStoredToken();
        // if (token != null) {
        //   options.headers['Authorization'] = 'Bearer $token';
        // }
        
        if (ApiConfig.enableDebugLogs) {
          print('🌐 API Request: ${options.method} ${options.path}');
          print('📦 Data: ${options.data}');
        }
        
        handler.next(options);
      },
      onResponse: (response, handler) {
        if (ApiConfig.enableDebugLogs) {
          print('✅ API Response: ${response.statusCode} ${response.requestOptions.path}');
        }
        handler.next(response);
      },
      onError: (error, handler) async {
        if (ApiConfig.enableDebugLogs) {
          print('❌ API Error: ${error.requestOptions.path}');
          print('🔥 Error: ${error.message}');
        }
        
        // Mock fallback on network error (development mode)
        if (ApiConfig.useMockData && _isNetworkError(error)) {
          print('🔄 Falling back to mock data...');
          // Return mock response (will be handled by provider layer)
        }
        
        handler.next(error);
      },
    ),
  );

  // Retry interceptor for production
  dio.interceptors.add(
    InterceptorsWrapper(
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Handle auth refresh
          print('🔐 Auth token expired, refreshing...');
          // TODO: Implement token refresh
        } else if (error.response?.statusCode == 503) {
          // Service unavailable, retry after delay
          print('🔄 Service unavailable, retrying...');
          await Future.delayed(const Duration(seconds: 2));
          // TODO: Implement retry logic
        }
        
        handler.next(error);
      },
    ),
  );

  return dio;
}

bool _isNetworkError(DioException error) {
  return error.type == DioExceptionType.connectionTimeout ||
         error.type == DioExceptionType.receiveTimeout ||
         error.type == DioExceptionType.connectionError;
}

// Enhanced API Service with Mock Fallback
class EnhancedApiService {
  final ApiService _apiService;
  
  EnhancedApiService(this._apiService);
  
  // Dashboard with fallback
  Future<DashboardStats> getDashboardStats() async {
    if (ApiConfig.useMockData) {
      return _getMockDashboardStats();
    }
    
    try {
      return await _apiService.getDashboardStats();
    } catch (e) {
      print('🔄 API failed, using mock data: $e');
      return _getMockDashboardStats();
    }
  }
  
  // Messages with fallback
  Future<List<MessageData>> getMessages({
    int page = 1,
    int limit = 50,
    String? status,
    String? botId,
    String? search,
  }) async {
    if (ApiConfig.useMockData) {
      return _getMockMessages();
    }
    
    try {
      return await _apiService.getMessages(
        page: page,
        limit: limit,
        status: status,
        botId: botId,
        search: search,
      );
    } catch (e) {
      print('🔄 API failed, using mock messages: $e');
      return _getMockMessages();
    }
  }
  
  // System status with fallback
  Future<SystemStatus> getSystemStatus() async {
    if (ApiConfig.useMockData) {
      return _getMockSystemStatus();
    }
    
    try {
      return await _apiService.getSystemStatus();
    } catch (e) {
      print('🔄 API failed, using mock system status: $e');
      return _getMockSystemStatus();
    }
  }
  
  // Delegate other methods
  Future<MessageData> createMessage(Map<String, dynamic> message) =>
      _apiService.createMessage(message);
  
  Future<void> deleteMessage(String id) => _apiService.deleteMessage(id);
  
  Future<Map<String, dynamic>> emergencyStop() => _apiService.emergencyStop();
  
  Future<Map<String, dynamic>> startBots(Map<String, dynamic> config) =>
      _apiService.startBots(config);
}

// Mock data generators
DashboardStats _getMockDashboardStats() {
  return const DashboardStats(
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
  );
}

List<MessageData> _getMockMessages() {
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
    // ... more mock data
  ];
}

SystemStatus _getMockSystemStatus() {
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
    warnings: ['High memory usage detected'],
  );
}

