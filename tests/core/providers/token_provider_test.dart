import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:gavatcore_mobile/core/providers/token_provider.dart';
import 'package:gavatcore_mobile/core/services/api_service.dart';
import 'package:gavatcore_mobile/core/storage/storage_service.dart';

class MockApiService extends Mock implements ApiService {}

void main() {
  late TokenProvider tokenProvider;
  late MockApiService mockApiService;

  setUp(() {
    mockApiService = MockApiService();
    tokenProvider = TokenProvider(mockApiService);
  });

  group('TokenProvider Tests', () {
    test('fetch tokens success', () async {
      final tokensResponse = {
        'tokens': [
          {'id': 1, 'name': 'Token 1', 'value': 100},
          {'id': 2, 'name': 'Token 2', 'value': 200},
        ],
      };

      when(mockApiService.get('/tokens'))
          .thenAnswer((_) async => tokensResponse);

      await tokenProvider.fetchTokens();

      verify(mockApiService.get('/tokens')).called(1);
      expect(tokenProvider.tokens.length, 2);
      expect(tokenProvider.tokens[0]['name'], 'Token 1');
      expect(tokenProvider.tokens[1]['value'], 200);
    });

    test('fetch tokens failure', () async {
      when(mockApiService.get('/tokens'))
          .thenThrow(ApiException(500, 'Server error'));

      expect(
        () => tokenProvider.fetchTokens(),
        throwsA(isA<ApiException>()),
      );

      expect(tokenProvider.tokens, isEmpty);
    });

    test('create token success', () async {
      final newToken = {
        'id': 3,
        'name': 'New Token',
        'value': 300,
      };

      when(mockApiService.post(
        '/tokens',
        data: anyNamed('data'),
      )).thenAnswer((_) async => newToken);

      await tokenProvider.createToken('New Token', 300);

      verify(mockApiService.post(
        '/tokens',
        data: {
          'name': 'New Token',
          'value': 300,
        },
      )).called(1);

      expect(tokenProvider.tokens.length, 1);
      expect(tokenProvider.tokens.last, newToken);
    });

    test('update token success', () async {
      final updatedToken = {
        'id': 1,
        'name': 'Updated Token',
        'value': 150,
      };

      when(mockApiService.put(
        '/tokens/1',
        data: anyNamed('data'),
      )).thenAnswer((_) async => updatedToken);

      await tokenProvider.updateToken(1, 'Updated Token', 150);

      verify(mockApiService.put(
        '/tokens/1',
        data: {
          'name': 'Updated Token',
          'value': 150,
        },
      )).called(1);
    });

    test('delete token success', () async {
      when(mockApiService.delete('/tokens/1'))
          .thenAnswer((_) async => {'success': true});

      await tokenProvider.deleteToken(1);

      verify(mockApiService.delete('/tokens/1')).called(1);
    });
  });
} 