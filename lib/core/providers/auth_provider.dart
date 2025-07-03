import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../storage/storage_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../repositories/auth_repository.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService;
  bool _isLoggedIn = false;
  Map<String, dynamic>? _user;

  AuthProvider(this._apiService);

  bool get isLoggedIn => _isLoggedIn;
  Map<String, dynamic>? get user => _user;

  Future<void> login(String email, String password) async {
    try {
      final response = await _apiService.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      final token = response['token'] as String;
      final userData = response['user'] as Map<String, dynamic>;

      await StorageService.setAuthToken(token);
      await StorageService.setUserData(userData);

      _isLoggedIn = true;
      _user = userData;
      notifyListeners();
    } catch (e) {
      _isLoggedIn = false;
      _user = null;
      rethrow;
    }
  }

  Future<void> logout() async {
    try {
      await _apiService.post('/auth/logout');
    } finally {
      await StorageService.clearAll();
      _isLoggedIn = false;
      _user = null;
      notifyListeners();
    }
  }

  Future<bool> checkAuthStatus() async {
    try {
      final response = await _apiService.get('/auth/status');
      _isLoggedIn = response['isLoggedIn'] as bool;
      if (_isLoggedIn) {
        _user = await StorageService.getUserData();
      }
      notifyListeners();
      return _isLoggedIn;
    } catch (e) {
      _isLoggedIn = false;
      _user = null;
      notifyListeners();
      return false;
    }
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository();
});

final authProvider = AsyncNotifierProvider<AuthNotifier, User?>(() {
  return AuthNotifier();
});

class AuthNotifier extends AsyncNotifier<User?> {
  late AuthRepository _authRepository;

  @override
  Future<User?> build() async {
    _authRepository = ref.read(authRepositoryProvider);
    return await _authRepository.getCurrentUser();
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    
    try {
      final user = await _authRepository.login(email, password);
      state = AsyncValue.data(user);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    }
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    
    try {
      await _authRepository.logout();
      state = const AsyncValue.data(null);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> refreshUser() async {
    try {
      final user = await _authRepository.getCurrentUser();
      state = AsyncValue.data(user);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
} 