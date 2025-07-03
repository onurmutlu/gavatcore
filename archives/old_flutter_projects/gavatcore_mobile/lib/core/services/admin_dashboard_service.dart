import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// 🎛️ GAVATCore Admin Dashboard Service
/// 
/// Comprehensive API service for Flutter mobile admin panel integration
class AdminDashboardService {
  static const String _baseUrl = 'http://localhost:8000';
  static const String _flutterApiUrl = 'http://localhost:9500';
  static const String _powerModeUrl = 'http://localhost:7500';
  static const String _behavioralUrl = 'http://localhost:5057';
  
  static const Duration _timeout = Duration(seconds: 10);
  
  /// 📊 Main Dashboard Statistics
  Future<Map<String, dynamic>> getDashboardStats() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/dashboard/stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load dashboard stats: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Dashboard stats error: $e');
    }
  }
  
  /// 🏥 System Health Status
  Future<Map<String, dynamic>> getSystemHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/system/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load system health: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('System health error: $e');
    }
  }
  
  /// 🚀 Performance Report
  Future<Map<String, dynamic>> getPerformanceReport() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/api/performance/report'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load performance report: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Performance report error: $e');
    }
  }
  
  /// 📱 Flutter-Optimized Quick Stats (for widgets)
  Future<Map<String, dynamic>> getQuickStats() async {
    try {
      final response = await http.get(
        Uri.parse('$_flutterApiUrl/api/flutter/quick-stats'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load quick stats: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Quick stats error: $e');
    }
  }
  
  /// 👥 Users List (Flutter optimized)
  Future<List<Map<String, dynamic>>> getUsersList() async {
    try {
      final response = await http.get(
        Uri.parse('$_flutterApiUrl/api/flutter/users'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['users'] ?? []);
      } else {
        throw Exception('Failed to load users: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Users list error: $e');
    }
  }
  
  /// 👤 User Profile (Big Five personality analysis)
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$_flutterApiUrl/api/flutter/user/$userId/profile'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load user profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('User profile error: $e');
    }
  }
  
  /// ⚡ Power Mode Status
  Future<Map<String, dynamic>> getPowerModeStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_powerModeUrl/api/power/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load power mode status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Power mode status error: $e');
    }
  }
  
  /// ⚡ Available Power Modes
  Future<Map<String, dynamic>> getAvailablePowerModes() async {
    try {
      final response = await http.get(
        Uri.parse('$_powerModeUrl/api/power/modes'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load power modes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Power modes error: $e');
    }
  }
  
  /// ⚡ Change Power Mode
  Future<Map<String, dynamic>> changePowerMode(String mode) async {
    try {
      final response = await http.post(
        Uri.parse('$_powerModeUrl/api/power/mode/$mode'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to change power mode: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Power mode change error: $e');
    }
  }
  
  /// 🔧 Services Status
  Future<Map<String, dynamic>> getServicesStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_flutterApiUrl/api/flutter/services/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load services status: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Services status error: $e');
    }
  }
  
  /// 🧠 Behavioral Insights Users
  Future<List<Map<String, dynamic>>> getBehavioralUsers() async {
    try {
      final response = await http.get(
        Uri.parse('$_behavioralUrl/api/users'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['users'] ?? []);
      } else {
        throw Exception('Failed to load behavioral users: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Behavioral users error: $e');
    }
  }
  
  /// 🧠 User Behavioral Profile
  Future<Map<String, dynamic>> getUserBehavioralProfile(String userId) async {
    try {
      final response = await http.get(
        Uri.parse('$_behavioralUrl/api/profile/$userId'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load behavioral profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Behavioral profile error: $e');
    }
  }
  
  /// 🧠 Behavioral Insights Metrics
  Future<Map<String, dynamic>> getBehavioralMetrics() async {
    try {
      final response = await http.get(
        Uri.parse('$_behavioralUrl/api/metrics'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load behavioral metrics: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Behavioral metrics error: $e');
    }
  }
  
  /// 🗂️ Clear System Cache
  Future<Map<String, dynamic>> clearSystemCache() async {
    try {
      final response = await http.delete(
        Uri.parse('$_baseUrl/api/cache/clear'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to clear cache: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Clear cache error: $e');
    }
  }
  
  /// 📊 Test All Services Connectivity
  Future<Map<String, bool>> testAllServices() async {
    final results = <String, bool>{};
    
    // Test main dashboard
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 3));
      results['comprehensive_dashboard'] = response.statusCode == 200;
    } catch (e) {
      results['comprehensive_dashboard'] = false;
    }
    
    // Test Flutter API
    try {
      final response = await http.get(
        Uri.parse('$_flutterApiUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 3));
      results['flutter_api'] = response.statusCode == 200;
    } catch (e) {
      results['flutter_api'] = false;
    }
    
    // Test Power Mode Controller
    try {
      final response = await http.get(
        Uri.parse('$_powerModeUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 3));
      results['power_mode_controller'] = response.statusCode == 200;
    } catch (e) {
      results['power_mode_controller'] = false;
    }
    
    // Test Behavioral Insights
    try {
      final response = await http.get(
        Uri.parse('$_behavioralUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(Duration(seconds: 3));
      results['behavioral_insights'] = response.statusCode == 200;
    } catch (e) {
      results['behavioral_insights'] = false;
    }
    
    return results;
  }
} 