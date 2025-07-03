import '../models/user.dart';
import '../services/api_service.dart';
import '../storage/storage_service.dart';

class AuthRepository {
  final ApiService _apiService = ApiService();

  Future<User?> getCurrentUser() async {
    try {
      final token = await StorageService.getAuthToken();
      if (token == null) return null;

      final userData = await StorageService.getUser();
      if (userData != null) {
        return User.fromJson(userData);
      }

      return null;
    } catch (e) {
      return null;
    }
  }

  Future<User> login(String email, String password) async {
    try {
      // Demo kullanıcı kontrolü
      if (email == 'demo@gavatcore.com' && password == 'demo123') {
        final demoUser = User(
          id: '1',
          email: email,
          name: 'Demo Kullanıcı',
          role: 'admin',
        );

        // Storage'a kaydet
        await StorageService.saveAuthToken('demo_token_123');
        await StorageService.saveUser(demoUser.toJson());

        return demoUser;
      }

      // API çağrısı (gerçek durumda)
      final response = await _apiService.post('/auth/login', data: {
        'email': email,
        'password': password,
      });

      final user = User.fromJson(response['user']);
      final token = response['token'];

      // Storage'a kaydet
      await StorageService.saveAuthToken(token);
      await StorageService.saveUser(user.toJson());

      return user;
    } catch (e) {
      throw Exception('Giriş başarısız: $e');
    }
  }

  Future<void> logout() async {
    try {
      await StorageService.clearAll();
    } catch (e) {
      throw Exception('Çıkış başarısız: $e');
    }
  }

  Future<User> register(String name, String email, String password) async {
    try {
      final response = await _apiService.post('/auth/register', data: {
        'name': name,
        'email': email,
        'password': password,
      });

      final user = User.fromJson(response['user']);
      final token = response['token'];

      // Storage'a kaydet
      await StorageService.saveAuthToken(token);
      await StorageService.saveUser(user.toJson());

      return user;
    } catch (e) {
      throw Exception('Kayıt başarısız: $e');
    }
  }

  Future<void> refreshToken() async {
    try {
      final currentToken = await StorageService.getAuthToken();
      if (currentToken == null) throw Exception('Token bulunamadı');

      final response = await _apiService.post('/auth/refresh');
      final newToken = response['token'];

      await StorageService.saveAuthToken(newToken);
    } catch (e) {
      throw Exception('Token yenileme başarısız: $e');
    }
  }
} 