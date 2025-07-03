import 'package:flutter/foundation.dart';
import '../services/admin_dashboard_service.dart';

/// 🎛️ GAVATCore Admin Dashboard Provider
/// 
/// State management for admin dashboard data with real-time updates
class AdminDashboardProvider extends ChangeNotifier {
  final AdminDashboardService _service = AdminDashboardService();
  
  // Dashboard stats
  Map<String, dynamic>? _dashboardStats;
  Map<String, dynamic>? get dashboardStats => _dashboardStats;
  
  // System health
  Map<String, dynamic>? _systemHealth;
  Map<String, dynamic>? get systemHealth => _systemHealth;
  
  // Performance report
  Map<String, dynamic>? _performanceReport;
  Map<String, dynamic>? get performanceReport => _performanceReport;
  
  // Quick stats for widgets
  Map<String, dynamic>? _quickStats;
  Map<String, dynamic>? get quickStats => _quickStats;
  
  // Users list
  List<Map<String, dynamic>> _users = [];
  List<Map<String, dynamic>> get users => _users;
  
  // Power mode
  Map<String, dynamic>? _powerModeStatus;
  Map<String, dynamic>? get powerModeStatus => _powerModeStatus;
  
  Map<String, dynamic>? _availablePowerModes;
  Map<String, dynamic>? get availablePowerModes => _availablePowerModes;
  
  // Services status
  Map<String, dynamic>? _servicesStatus;
  Map<String, dynamic>? get servicesStatus => _servicesStatus;
  
  // Behavioral users
  List<Map<String, dynamic>> _behavioralUsers = [];
  List<Map<String, dynamic>> get behavioralUsers => _behavioralUsers;
  
  // Behavioral metrics
  Map<String, dynamic>? _behavioralMetrics;
  Map<String, dynamic>? get behavioralMetrics => _behavioralMetrics;
  
  // Loading states
  bool _isLoading = false;
  bool get isLoading => _isLoading;
  
  bool _isRefreshing = false;
  bool get isRefreshing => _isRefreshing;
  
  // Error handling
  String? _error;
  String? get error => _error;
  
  // Services connectivity
  Map<String, bool> _servicesConnectivity = {};
  Map<String, bool> get servicesConnectivity => _servicesConnectivity;
  
  // Auto-refresh timer
  bool _autoRefreshEnabled = true;
  bool get autoRefreshEnabled => _autoRefreshEnabled;
  
  /// 🚀 Initialize dashboard data
  Future<void> initialize() async {
    _setLoading(true);
    _clearError();
    
    try {
      // Test services connectivity first
      await testServicesConnectivity();
      
      // Load all dashboard data in parallel
      await Future.wait([
        loadDashboardStats(),
        loadSystemHealth(),
        loadQuickStats(),
        loadPowerModeStatus(),
        loadServicesStatus(),
        loadBehavioralUsers(),
        loadBehavioralMetrics(),
      ]);
      
    } catch (e) {
      _setError('Failed to initialize dashboard: $e');
    } finally {
      _setLoading(false);
    }
  }
  
  /// 📊 Load Dashboard Statistics
  Future<void> loadDashboardStats() async {
    try {
      _dashboardStats = await _service.getDashboardStats();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load dashboard stats: $e');
    }
  }
  
  /// 🏥 Load System Health
  Future<void> loadSystemHealth() async {
    try {
      _systemHealth = await _service.getSystemHealth();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load system health: $e');
    }
  }
  
  /// 🚀 Load Performance Report
  Future<void> loadPerformanceReport() async {
    try {
      _performanceReport = await _service.getPerformanceReport();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load performance report: $e');
    }
  }
  
  /// 📱 Load Quick Stats (for widgets)
  Future<void> loadQuickStats() async {
    try {
      _quickStats = await _service.getQuickStats();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load quick stats: $e');
    }
  }
  
  /// 👥 Load Users List
  Future<void> loadUsers() async {
    try {
      _users = await _service.getUsersList();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load users: $e');
    }
  }
  
  /// ⚡ Load Power Mode Status
  Future<void> loadPowerModeStatus() async {
    try {
      _powerModeStatus = await _service.getPowerModeStatus();
      _availablePowerModes = await _service.getAvailablePowerModes();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load power mode: $e');
    }
  }
  
  /// ⚡ Change Power Mode
  Future<bool> changePowerMode(String mode) async {
    try {
      final result = await _service.changePowerMode(mode);
      
      if (result['success'] == true) {
        // Reload power mode status after change
        await loadPowerModeStatus();
        return true;
      } else {
        _setError('Failed to change power mode: ${result['error']}');
        return false;
      }
    } catch (e) {
      _setError('Power mode change error: $e');
      return false;
    }
  }
  
  /// 🔧 Load Services Status
  Future<void> loadServicesStatus() async {
    try {
      _servicesStatus = await _service.getServicesStatus();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load services status: $e');
    }
  }
  
  /// 🧠 Load Behavioral Users
  Future<void> loadBehavioralUsers() async {
    try {
      _behavioralUsers = await _service.getBehavioralUsers();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load behavioral users: $e');
    }
  }
  
  /// 🧠 Load Behavioral Metrics
  Future<void> loadBehavioralMetrics() async {
    try {
      _behavioralMetrics = await _service.getBehavioralMetrics();
      notifyListeners();
    } catch (e) {
      _setError('Failed to load behavioral metrics: $e');
    }
  }
  
  /// 👤 Get User Profile (with caching)
  Future<Map<String, dynamic>?> getUserProfile(String userId) async {
    try {
      return await _service.getUserProfile(userId);
    } catch (e) {
      _setError('Failed to load user profile: $e');
      return null;
    }
  }
  
  /// 🧠 Get User Behavioral Profile
  Future<Map<String, dynamic>?> getUserBehavioralProfile(String userId) async {
    try {
      return await _service.getUserBehavioralProfile(userId);
    } catch (e) {
      _setError('Failed to load behavioral profile: $e');
      return null;
    }
  }
  
  /// 🗂️ Clear System Cache
  Future<bool> clearSystemCache() async {
    try {
      final result = await _service.clearSystemCache();
      
      if (result['success'] == true) {
        // Refresh data after cache clear
        await refresh();
        return true;
      } else {
        _setError('Failed to clear cache: ${result['error']}');
        return false;
      }
    } catch (e) {
      _setError('Clear cache error: $e');
      return false;
    }
  }
  
  /// 📊 Test Services Connectivity
  Future<void> testServicesConnectivity() async {
    try {
      _servicesConnectivity = await _service.testAllServices();
      notifyListeners();
    } catch (e) {
      _setError('Failed to test services: $e');
    }
  }
  
  /// 🔄 Refresh All Data
  Future<void> refresh() async {
    _setRefreshing(true);
    _clearError();
    
    try {
      await initialize();
    } finally {
      _setRefreshing(false);
    }
  }
  
  /// ⏰ Enable/Disable Auto-refresh
  void setAutoRefresh(bool enabled) {
    _autoRefreshEnabled = enabled;
    notifyListeners();
  }
  
  /// 📊 Get Overall System Health Percentage
  double get overallHealthPercentage {
    if (_systemHealth == null) return 0.0;
    
    final health = _systemHealth!['system_health'];
    if (health is num) {
      return health.toDouble();
    }
    return 0.0;
  }
  
  /// 📈 Get Cache Hit Rate
  double get cacheHitRate {
    if (_dashboardStats == null) return 0.0;
    
    final hitRate = _dashboardStats!['cache_hit_rate'];
    if (hitRate is num) {
      return hitRate.toDouble();
    }
    return 0.0;
  }
  
  /// 👥 Get Active Users Count
  int get activeUsersCount {
    if (_dashboardStats == null) return 0;
    
    final count = _dashboardStats!['active_users'];
    if (count is num) {
      return count.toInt();
    }
    return 0;
  }
  
  /// ⚡ Get Current Power Mode
  String get currentPowerMode {
    if (_powerModeStatus == null) return 'unknown';
    
    final status = _powerModeStatus!['status'];
    if (status is Map<String, dynamic>) {
      return status['current_mode'] ?? 'unknown';
    }
    return 'unknown';
  }
  
  /// 🔧 Get Online Services Count
  int get onlineServicesCount {
    if (_servicesStatus == null) return 0;
    
    final summary = _servicesStatus!['summary'];
    if (summary is Map<String, dynamic>) {
      return summary['online'] ?? 0;
    }
    return 0;
  }
  
  /// 🔧 Get Total Services Count
  int get totalServicesCount {
    if (_servicesStatus == null) return 0;
    
    final summary = _servicesStatus!['summary'];
    if (summary is Map<String, dynamic>) {
      return summary['total'] ?? 0;
    }
    return 0;
  }
  
  /// 🧠 Get Average Sentiment Score
  double get averageSentimentScore {
    if (_behavioralMetrics == null) return 0.0;
    
    final sentiment = _behavioralMetrics!['average_sentiment'];
    if (sentiment is num) {
      return sentiment.toDouble();
    }
    return 0.0;
  }
  
  // Private helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setRefreshing(bool refreshing) {
    _isRefreshing = refreshing;
    notifyListeners();
  }
  
  void _setError(String error) {
    _error = error;
    notifyListeners();
  }
  
  void _clearError() {
    _error = null;
  }
} 