import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../services/telegram_service.dart';
import '../models/user.dart';

// 🚀 SaaS API Providers
final apiServiceProvider = Provider((ref) => ApiService());

final saasApiServiceProvider = Provider((ref) {
  final apiService = ref.watch(apiServiceProvider);
  return SaasApiService(apiService);
});

final telegramServiceProvider = Provider((ref) => TelegramService());

final authProvider = AsyncNotifierProvider<AuthNotifier, User?>(() {
  return AuthNotifier();
});

class AuthNotifier extends AsyncNotifier<User?> {
  late SaasApiService _saasService;

  @override
  Future<User?> build() async {
    _saasService = ref.watch(saasApiServiceProvider);
    final telegramService = ref.watch(telegramServiceProvider);
    
    // Check Telegram session first
    try {
      final hasSession = await telegramService.checkExistingSession();
      if (hasSession) {
        final user = await telegramService.getCurrentUser();
        if (user != null) return user;
      }
    } catch (e) {
      // Continue to check API auth
    }
    
    // Check if user is already authenticated via API
    final isLoggedIn = await isAuthenticated();
    if (isLoggedIn) {
      try {
        final apiService = ref.watch(apiServiceProvider);
        final userData = await apiService.getCurrentUser();
        // Convert UserData to User model
        return User(
          id: userData.id.toString(),
          email: userData.email ?? '',
          name: userData.fullName,
          role: 'user',
        );
      } catch (e) {
        // Token might be expired, clear auth state
        await _clearAuthState();
        return null;
      }
    }
    return null;
  }

  Future<bool> login(User user) async {
    state = const AsyncValue.loading();
    
    try {
      state = AsyncValue.data(user);
      return true;
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
      return false;
    }
  }

  Future<bool> apiLogin(String username, String password) async {
    state = const AsyncValue.loading();
    
    try {
      final authResponse = await _saasService.login(username, password);
      // Convert UserData to User model
      final user = User(
        id: authResponse.user.id.toString(),
        email: authResponse.user.email ?? '',
        name: authResponse.user.fullName,
        role: 'user',
      );
      state = AsyncValue.data(user);
      return true;
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
      return false;
    }
  }

  Future<bool> register({
    required String username,
    String? email,
    String? password,
    String? firstName,
    String? lastName,
  }) async {
    state = const AsyncValue.loading();
    
    try {
      final authResponse = await _saasService.register(
        username: username,
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );
      state = AsyncValue.data(authResponse.user);
      return true;
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
      return false;
    }
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    
    try {
      // Clear Telegram session
      final telegramService = ref.watch(telegramServiceProvider);
      await telegramService.logout();
      
      // Clear API auth
      await _saasService.logout();
      
      state = const AsyncValue.data(null);
    } catch (e, stackTrace) {
      state = AsyncValue.error(e, stackTrace);
    }
  }

  Future<void> refreshUser() async {
    try {
      final isLoggedIn = await isAuthenticated();
      if (isLoggedIn) {
        final apiService = ref.watch(apiServiceProvider);
        final user = await apiService.getCurrentUser();
        state = AsyncValue.data(user);
      } else {
        state = const AsyncValue.data(null);
      }
    } catch (e, stackTrace) {
      await _clearAuthState();
      state = const AsyncValue.data(null);
    }
  }

  Future<bool> validateToken() async {
    try {
      final apiService = ref.watch(apiServiceProvider);
      await apiService.verifyToken();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> _clearAuthState() async {
    // This will be handled by the SaasApiService logout method
    await _saasService.logout();
  }
}

// 🎯 Subscription Provider
final subscriptionProvider = FutureProvider<SubscriptionStatus?>((ref) async {
  final saasService = ref.watch(saasApiServiceProvider);
  final authState = ref.watch(authProvider);
  
  // Only fetch subscription if user is authenticated
  return authState.when(
    data: (user) async {
      if (user != null) {
        try {
          return await saasService.getSubscriptionStatus();
        } catch (e) {
          return null;
        }
      }
      return null;
    },
    loading: () => null,
    error: (_, __) => null,
  );
});

// 💳 Pricing Plans Provider
final pricingPlansProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final saasService = ref.watch(saasApiServiceProvider);
  
  try {
    return await saasService.getPricingPlans();
  } catch (e) {
    return null;
  }
});

// Helper providers for UI state
final isAuthenticatedProvider = Provider<bool>((ref) {
  final authState = ref.watch(authProvider);
  return authState.when(
    data: (user) => user != null,
    loading: () => false,
    error: (_, __) => false,
  );
});

final currentUserProvider = Provider<User?>((ref) {
  final authState = ref.watch(authProvider);
  return authState.when(
    data: (user) => user,
    loading: () => null,
    error: (_, __) => null,
  );
});

// Auth state enum for compatibility
enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
} 