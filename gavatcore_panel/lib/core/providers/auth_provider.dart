import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repositories/auth_repository.dart';
import '../services/api_service.dart';
import '../models/user.dart';

final apiServiceProvider = Provider((ref) => ApiService());

final authRepositoryProvider = Provider((ref) => AuthRepository(ApiService()));

final authProvider = AsyncNotifierProvider<AuthNotifier, User?>(() {
  return AuthNotifier();
});

class AuthNotifier extends AsyncNotifier<User?> {
  late AuthRepository _repository;

  @override
  Future<User?> build() async {
    _repository = ref.watch(authRepositoryProvider);
    
    // Check if user is already logged in
    final isLoggedIn = await AuthRepository.isLoggedIn();
    if (isLoggedIn) {
      return await _repository.getCurrentUser();
    }
    return null;
  }

  Future<bool> login(String email, String password) async {
    state = const AsyncValue.loading();
    
    try {
      final success = await _repository.login(email, password);
      if (success) {
        final user = await _repository.getCurrentUser();
        state = AsyncValue.data(user);
        return true;
      } else {
        state = const AsyncValue.data(null);
        return false;
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
      return false;
    }
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    
    try {
      await _repository.logout();
      state = const AsyncValue.data(null);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> refreshUser() async {
    try {
      final isLoggedIn = await AuthRepository.isLoggedIn();
      if (isLoggedIn) {
        final user = await _repository.getCurrentUser();
        state = AsyncValue.data(user);
      } else {
        state = const AsyncValue.data(null);
      }
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<bool> validateToken() async {
    try {
      return await _repository.validateToken();
    } catch (e) {
      return false;
    }
  }
}

class AuthState {
  final AuthStatus status;
  final Map<String, dynamic>? userData;
  final String? error;

  const AuthState._({
    required this.status,
    this.userData,
    this.error,
  });

  const AuthState.initial() : this._(status: AuthStatus.initial);

  const AuthState.loading() : this._(status: AuthStatus.loading);

  const AuthState.authenticated(Map<String, dynamic> userData)
      : this._(status: AuthStatus.authenticated, userData: userData);

  const AuthState.unauthenticated() : this._(status: AuthStatus.unauthenticated);

  const AuthState.error(String error)
      : this._(status: AuthStatus.error, error: error);

  bool get isLoading => status == AuthStatus.loading;
  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isUnauthenticated => status == AuthStatus.unauthenticated;
  bool get hasError => status == AuthStatus.error;
}

enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
} 