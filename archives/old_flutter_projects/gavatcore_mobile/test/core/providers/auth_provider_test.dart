import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:gavatcore_mobile/core/repositories/auth_repository.dart';
import 'package:gavatcore_mobile/core/providers/auth_provider.dart';

@GenerateMocks([AuthRepository])
import 'auth_provider_test.mocks.dart';

void main() {
  late AuthNotifier authNotifier;
  late MockAuthRepository mockRepository;

  setUp(() async {
    mockRepository = MockAuthRepository();
    when(mockRepository.isLoggedIn()).thenAnswer((_) async => false);
    when(mockRepository.getUserData()).thenAnswer((_) async => null);
    authNotifier = AuthNotifier(mockRepository);
    await Future.delayed(Duration.zero); // StateNotifier'ın başlangıç durumunu bekle
  });

  group('AuthNotifier', () {
    test('initial state should be unauthenticated when not logged in', () {
      expect(authNotifier.state.status, equals(AuthStatus.unauthenticated));
    });

    test('login success should update state to authenticated', () async {
      final mockUserData = {'id': 1, 'username': 'test_user'};

      when(mockRepository.login('test_user', 'test_pass'))
          .thenAnswer((_) async => {});
      when(mockRepository.getUserData())
          .thenAnswer((_) async => mockUserData);

      await authNotifier.login('test_user', 'test_pass');

      expect(authNotifier.state.status, equals(AuthStatus.authenticated));
      expect(authNotifier.state.userData, equals(mockUserData));
    });

    test('login failure should update state to error', () async {
      when(mockRepository.login('test_user', 'test_pass'))
          .thenThrow(Exception('Invalid credentials'));

      await authNotifier.login('test_user', 'test_pass');

      expect(authNotifier.state.status, equals(AuthStatus.error));
      expect(authNotifier.state.error, contains('Invalid credentials'));
    });

    test('logout should update state to unauthenticated', () async {
      when(mockRepository.logout()).thenAnswer((_) async => {});

      await authNotifier.logout();

      expect(authNotifier.state.status, equals(AuthStatus.unauthenticated));
    });
  });
} 