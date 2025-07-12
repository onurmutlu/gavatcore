import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/app_state.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'api_service.g.dart';

// Environment configuration
class ApiConfig {
  // 🚀 SaaS API Base URL
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api', // SaaS API
  );
  /// Communication analysis endpoint (bait vs genuine)
  static const String communicationAnalysisUrl = '$baseUrl/analysis/communication';
  
  static const String wsUrl = String.fromEnvironment(
    'WS_URL', 
    defaultValue: 'ws://localhost:8000/ws',
  );
  
  static const bool useMockData = bool.fromEnvironment(
    'USE_MOCK_DATA',
    defaultValue: false, // SaaS için false, gerçek API kullan
  );
  
  static const bool enableDebugLogs = bool.fromEnvironment(
    'DEBUG_API',
    defaultValue: true,
  );
}

// 🔐 SaaS Authentication Models
class LoginRequest {
  final String username;
  final String password;
  
  LoginRequest({required this.username, required this.password});
  
  Map<String, dynamic> toJson() => {
    'username': username,
    'password': password,
  };
}

class RegisterRequest {
  final String username;
  final String? email;
  final String? password;
  final String? firstName;
  final String? lastName;
  
  RegisterRequest({
    required this.username,
    this.email,
    this.password,
    this.firstName,
    this.lastName,
  });
  
  Map<String, dynamic> toJson() => {
    'username': username,
    if (email != null) 'email': email,
    if (password != null) 'password': password,
    if (firstName != null) 'first_name': firstName,
    if (lastName != null) 'last_name': lastName,
  };
}

class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final UserData user;
  
  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });
  
  factory AuthResponse.fromJson(Map<String, dynamic> json) => AuthResponse(
    accessToken: json['access_token'],
    refreshToken: json['refresh_token'],
    tokenType: json['token_type'],
    expiresIn: json['expires_in'],
    user: UserData.fromJson(json['user']),
  );
}

class UserData {
  final int id;
  final String username;
  final String? email;
  final String fullName;
  final bool isActive;
  final String registrationSource;
  final String? telegramUsername;
  
  UserData({
    required this.id,
    required this.username,
    this.email,
    required this.fullName,
    required this.isActive,
    required this.registrationSource,
    this.telegramUsername,
  });
  
  factory UserData.fromJson(Map<String, dynamic> json) => UserData(
    id: json['id'],
    username: json['username'],
    email: json['email'],
    fullName: json['full_name'],
    isActive: json['is_active'],
    registrationSource: json['registration_source'],
    telegramUsername: json['telegram_username'],
  );
  
  Map<String, dynamic> toJson() => {
    'id': id,
    'username': username,
    'email': email,
    'full_name': fullName,
    'is_active': isActive,
    'registration_source': registrationSource,
    'telegram_username': telegramUsername,
  };
}

// 💳 Payment Models
class CheckoutRequest {
  final String planName;
  final String successUrl;
  final String cancelUrl;
  
  CheckoutRequest({
    required this.planName,
    required this.successUrl,
    required this.cancelUrl,
  });
  
  Map<String, dynamic> toJson() => {
    'plan_name': planName,
    'success_url': successUrl,
    'cancel_url': cancelUrl,
  };
}

class CheckoutResponse {
  final String sessionId;
  final String sessionUrl;
  final int paymentId;
  final double amount;
  final String currency;
  final String planName;
  
  CheckoutResponse({
    required this.sessionId,
    required this.sessionUrl,
    required this.paymentId,
    required this.amount,
    required this.currency,
    required this.planName,
  });
  
  factory CheckoutResponse.fromJson(Map<String, dynamic> json) => CheckoutResponse(
    sessionId: json['session_id'],
    sessionUrl: json['session_url'],
    paymentId: json['payment_id'],
    amount: json['amount'].toDouble(),
    currency: json['currency'],
    planName: json['plan_name'],
  );
}

class SubscriptionStatus {
  final bool hasSubscription;
  final SubscriptionData? subscription;
  
  SubscriptionStatus({
    required this.hasSubscription,
    this.subscription,
  });
  
  factory SubscriptionStatus.fromJson(Map<String, dynamic> json) => SubscriptionStatus(
    hasSubscription: json['has_subscription'],
    subscription: json['subscription'] != null 
        ? SubscriptionData.fromJson(json['subscription']) 
        : null,
  );
}

class SubscriptionData {
  final int id;
  final String planName;
  final DateTime startedAt;
  final DateTime expiresAt;
  final bool isTrial;
  final int maxBots;
  final int maxCoins;
  final int daysRemaining;
  final List<String> features;
  
  SubscriptionData({
    required this.id,
    required this.planName,
    required this.startedAt,
    required this.expiresAt,
    required this.isTrial,
    required this.maxBots,
    required this.maxCoins,
    required this.daysRemaining,
    required this.features,
  });
  
  factory SubscriptionData.fromJson(Map<String, dynamic> json) => SubscriptionData(
    id: json['id'],
    planName: json['plan_name'],
    startedAt: DateTime.parse(json['started_at']),
    expiresAt: DateTime.parse(json['expires_at']),
    isTrial: json['is_trial'],
    maxBots: json['max_bots'],
    maxCoins: json['max_coins'],
    daysRemaining: json['days_remaining'],
    features: List<String>.from(json['features']),
  );
}

@RestApi(baseUrl: "")
abstract class ApiService {
  factory ApiService([Dio? dio]) {
    dio ??= _createDio();
    return _ApiService(dio, baseUrl: ApiConfig.baseUrl);
  }

  // 🔐 SaaS Authentication Endpoints
  @POST("/auth/login")
  Future<AuthResponse> login(@Body() LoginRequest request);

  @POST("/auth/register")
  Future<AuthResponse> register(@Body() RegisterRequest request);

  @POST("/auth/telegram")
  Future<AuthResponse> telegramAuth(@Body() Map<String, dynamic> request);

  @GET("/auth/me")
  Future<UserData> getCurrentUser();

  @GET("/auth/verify")
  Future<Map<String, dynamic>> verifyToken();

  @POST("/auth/logout")
  Future<Map<String, dynamic>> logout();

  // 💳 SaaS Payment Endpoints
  @GET("/payment/plans")
  Future<Map<String, dynamic>> getPricingPlans();

  @POST("/payment/stripe/create-checkout")
  Future<CheckoutResponse> createStripeCheckout(@Body() CheckoutRequest request);

  @GET("/payment/subscription/status")
  Future<SubscriptionStatus> getSubscriptionStatus();

  @GET("/payment/history")
  Future<Map<String, dynamic>> getPaymentHistory();

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

  // 🤖 SaaS Bot Management Endpoints
  @GET("/bots/")
  Future<List<Map<String, dynamic>>> getUserBots();

  @POST("/bots/create")
  Future<Map<String, dynamic>> createBot(@Body() Map<String, dynamic> request);

  @GET("/bots/{id}")
  Future<Map<String, dynamic>> getBotDetails(@Path("id") int botId);

  @POST("/bots/{id}/start")
  Future<Map<String, dynamic>> startBot(@Path("id") int botId);

  @POST("/bots/{id}/stop")
  Future<Map<String, dynamic>> stopBot(@Path("id") int botId);

  @POST("/bots/{id}/restart")
  Future<Map<String, dynamic>> restartBot(@Path("id") int botId);

  @DELETE("/bots/{id}")
  Future<Map<String, dynamic>> deleteBot(@Path("id") int botId);

  @PUT("/bots/{id}/config")
  Future<Map<String, dynamic>> updateBotConfig(
    @Path("id") int botId,
    @Body() Map<String, dynamic> config,
  );

  @GET("/bots/personalities/available")
  Future<Map<String, dynamic>> getAvailablePersonalities();
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
        // 🔐 Add JWT token for SaaS API
        final token = await _getStoredToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        
        if (ApiConfig.enableDebugLogs) {
          print('🌐 API Request: ${options.method} ${options.path}');
          print('🔐 Token: ${token != null ? "Present" : "None"}');
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
          // 🔐 Handle auth token expired - redirect to login
          print('🔐 Auth token expired, clearing auth state...');
          await _clearStoredToken();
          // TODO: Navigate to login screen
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

// 🔐 JWT Token Management
const String _tokenKey = 'auth_token';
const String _refreshTokenKey = 'refresh_token';
const String _userDataKey = 'user_data';

/// Store JWT token securely
Future<void> storeAuthTokens({
  required String accessToken,
  required String refreshToken,
  required UserData user,
}) async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.setString(_tokenKey, accessToken);
  await prefs.setString(_refreshTokenKey, refreshToken);
  
  // Store user data as JSON
  final userJson = user.toJson();
  await prefs.setString(_userDataKey, userJson.toString());
  
  print('🔐 Auth tokens stored successfully');
}

/// Get stored JWT token
Future<String?> _getStoredToken() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_tokenKey);
}

/// Get stored refresh token
Future<String?> getStoredRefreshToken() async {
  final prefs = await SharedPreferences.getInstance();
  return prefs.getString(_refreshTokenKey);
}

/// Get stored user data
Future<UserData?> getStoredUser() async {
  final prefs = await SharedPreferences.getInstance();
  final userDataString = prefs.getString(_userDataKey);
  
  if (userDataString != null) {
    try {
      // Parse user data from stored JSON
      // Note: You'll need to implement UserData.fromJsonString()
      return null; // Placeholder - implement JSON parsing
    } catch (e) {
      print('❌ Failed to parse stored user data: $e');
      return null;
    }
  }
  
  return null;
}

/// Clear stored auth data (logout)
Future<void> _clearStoredToken() async {
  final prefs = await SharedPreferences.getInstance();
  await prefs.remove(_tokenKey);
  await prefs.remove(_refreshTokenKey);
  await prefs.remove(_userDataKey);
  
  print('🔐 Auth tokens cleared');
}

/// Check if user is authenticated
Future<bool> isAuthenticated() async {
  final token = await _getStoredToken();
  return token != null && token.isNotEmpty;
}

// 🎯 SaaS API Helper Functions
class SaasApiService {
  final ApiService _apiService;
  
  SaasApiService(this._apiService);
  
  /// Login and store tokens
  Future<AuthResponse> login(String username, String password) async {
    final request = LoginRequest(username: username, password: password);
    final response = await _apiService.login(request);
    
    // Store tokens
    await storeAuthTokens(
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      user: response.user,
    );
    
    return response;
  }
  
  /// Register and store tokens
  Future<AuthResponse> register({
    required String username,
    String? email,
    String? password,
    String? firstName,
    String? lastName,
  }) async {
    final request = RegisterRequest(
      username: username,
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
    );
    
    final response = await _apiService.register(request);
    
    // Store tokens
    await storeAuthTokens(
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      user: response.user,
    );
    
    return response;
  }
  
  /// Logout and clear tokens
  Future<void> logout() async {
    try {
      await _apiService.logout();
    } catch (e) {
      print('❌ Logout API call failed: $e');
    } finally {
      await _clearStoredToken();
    }
  }
  
  /// Get subscription status
  Future<SubscriptionStatus> getSubscriptionStatus() async {
    return await _apiService.getSubscriptionStatus();
  }
  
  /// Create Stripe checkout
  Future<CheckoutResponse> createCheckout({
    required String planName,
    required String successUrl,
    required String cancelUrl,
  }) async {
    final request = CheckoutRequest(
      planName: planName,
      successUrl: successUrl,
      cancelUrl: cancelUrl,
    );
    
    return await _apiService.createStripeCheckout(request);
  }
  
  /// Get pricing plans
  Future<Map<String, dynamic>> getPricingPlans() async {
    return await _apiService.getPricingPlans();
  }

  // 🤖 Bot Management Methods
  Future<List<Map<String, dynamic>>> getUserBots() async {
    return await _apiService.getUserBots();
  }

  Future<Map<String, dynamic>> createBot({
    required String personality,
    String? phoneNumber,
    String? customName,
  }) async {
    return await _apiService.createBot({
      'personality': personality,
      'phone_number': phoneNumber,
      'custom_name': customName,
    });
  }

  Future<Map<String, dynamic>> getBotDetails(int botId) async {
    return await _apiService.getBotDetails(botId);
  }

  Future<Map<String, dynamic>> startBot(int botId) async {
    return await _apiService.startBot(botId);
  }

  Future<Map<String, dynamic>> stopBot(int botId) async {
    return await _apiService.stopBot(botId);
  }

  Future<Map<String, dynamic>> restartBot(int botId) async {
    return await _apiService.restartBot(botId);
  }

  Future<Map<String, dynamic>> deleteBot(int botId) async {
    return await _apiService.deleteBot(botId);
  }

  Future<Map<String, dynamic>> updateBotConfig(int botId, Map<String, dynamic> config) async {
    return await _apiService.updateBotConfig(botId, config);
  }

  Future<Map<String, dynamic>> getAvailablePersonalities() async {
    return await _apiService.getAvailablePersonalities();
  }
}
