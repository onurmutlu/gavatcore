import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../storage/storage_service.dart';
import '../models/user.dart';

final authRepositoryProvider = Provider((ref) {
  final apiService = ref.read(apiServiceProvider);
  return AuthRepository(apiService);
});

class AuthRepository {
  final ApiService _apiService;
  static String? _authToken;

  AuthRepository(this._apiService);

  // Static method for auth token
  static void setAuthToken(String token) {
    _authToken = token;
    StorageService.instance.setString('auth_token', token);
  }

  static String? getAuthToken() {
    _authToken ??= StorageService.instance.getString('auth_token');
    return _authToken;
  }

  static void clearAuthToken() {
    _authToken = null;
    StorageService.instance.deleteKey('auth_token');
  }

  // Instance methods for user operations
  Future<bool> login(String email, String password) async {
    try {
      // Mock login logic - replace with real API call
      if (email == 'admin@gavatcore.com' && password == 'admin123' ||
          email == 'onur_mutlu' && password == 'gavatcore2024' ||
          email == 'admin' && password == 'admin123') {
        
        // Generate a mock token
        final token = 'mock_token_${DateTime.now().millisecondsSinceEpoch}';
        
        // Save auth data
        setAuthToken(token);
        await StorageService.instance.setString('user_email', email);
        await StorageService.instance.setBool('is_logged_in', true);
        await StorageService.instance.setString('user_name', 
          email == 'onur_mutlu' ? 'Onur Mutlu' : 'Admin User');
        await StorageService.instance.setString('user_role', 'admin');
        
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    clearAuthToken();
    await StorageService.instance.deleteKey('user_email');
    await StorageService.instance.deleteKey('user_name');
    await StorageService.instance.deleteKey('user_role');
    await StorageService.instance.setBool('is_logged_in', false);
  }

  // Static method for quick login check
  static Future<bool> isLoggedIn() async {
    final token = getAuthToken();
    final isLoggedIn = StorageService.instance.getBool('is_logged_in') ?? false;
    return token != null && isLoggedIn;
  }

  Future<User?> getCurrentUser() async {
    final email = StorageService.instance.getString('user_email');
    final name = StorageService.instance.getString('user_name');
    final role = StorageService.instance.getString('user_role');
    
    if (email != null) {
      return User(
        id: '1',
        email: email,
        name: name ?? 'Admin User',
        role: role ?? 'admin',
      );
    }
    return null;
  }

  // Add the missing getUserData method
  Future<Map<String, dynamic>?> getUserData() async {
    final user = await getCurrentUser();
    if (user != null) {
      return {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'auth_token': getAuthToken(),
        'is_logged_in': await isLoggedIn(),
      };
    }
    return null;
  }

  // Utility methods
  Future<bool> validateToken() async {
    final token = getAuthToken();
    if (token == null) return false;
    
    // Mock token validation - replace with real API call
    return token.startsWith('mock_token_') && await isLoggedIn();
  }

  Future<void> refreshToken() async {
    // Mock token refresh - replace with real API call
    if (await isLoggedIn()) {
      final newToken = 'mock_token_${DateTime.now().millisecondsSinceEpoch}';
      setAuthToken(newToken);
    }
  }

  Future<void> saveUserData(Map<String, dynamic> userData) async {
    await StorageService.setUserData(userData);
  }
} 