import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:gavatcore_mobile/core/providers/auth_provider.dart';
import 'package:gavatcore_mobile/core/services/api_service.dart';
import 'package:gavatcore_mobile/core/storage/storage_service.dart';

class MockApiService extends Mock implements ApiService {}

void main() {
  late AuthProvider authProvider;
  late MockApiService mockApiService;

  setUp(() {
    mockApiService = MockApiService();
    authProvider = AuthProvider(mockApiService);
  });

  group('AuthProvider Tests', () {
    test('login success', () async {
      final loginResponse = {
        'token': 'test_token',
        'user': {'id': 1, 'name': 'Test User'},
      };

      when(mockApiService.post(
        '/auth/login',
        data: anyNamed('data'),
      )).thenAnswer((_) async => loginResponse);

      await authProvider.login('test@example.com', 'password');

      verify(mockApiService.post(
        '/auth/login',
        data: {
          'email': 'test@example.com',
          'password': 'password',
        },
      )).called(1);

      expect(authProvider.isLoggedIn, true);
      expect(authProvider.user, loginResponse['user']);
    });

    test('login failure', () async {
      when(mockApiService.post(
        '/auth/login',
        data: anyNamed('data'),
      )).thenThrow(ApiException(401, 'Invalid credentials'));

      expect(
        () => authProvider.login('test@example.com', 'wrong_password'),
        throwsA(isA<ApiException>()),
      );

      expect(authProvider.isLoggedIn, false);
      expect(authProvider.user, null);
    });

    test('logout success', () async {
      when(mockApiService.post('/auth/logout'))
          .thenAnswer((_) async => {'success': true});

      await authProvider.logout();

      verify(mockApiService.post('/auth/logout')).called(1);
      expect(authProvider.isLoggedIn, false);
      expect(authProvider.user, null);
    });

    test('check auth status', () async {
      when(mockApiService.get('/auth/status'))
          .thenAnswer((_) async => {'isLoggedIn': true});

      final isLoggedIn = await authProvider.checkAuthStatus();

      verify(mockApiService.get('/auth/status')).called(1);
      expect(isLoggedIn, true);
    });
  });
} 