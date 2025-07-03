import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:gavatcore_mobile/core/repositories/token_repository.dart';
import 'package:gavatcore_mobile/core/providers/token_provider.dart';

@GenerateMocks([TokenRepository])
import 'token_provider_test.mocks.dart';

void main() {
  late TokenNotifier tokenNotifier;
  late MockTokenRepository mockRepository;

  setUp(() async {
    mockRepository = MockTokenRepository();
    when(mockRepository.getTokenStats()).thenAnswer((_) async => {});
    when(mockRepository.getTokenTransactions()).thenAnswer((_) async => []);
    tokenNotifier = TokenNotifier(mockRepository);
    await Future.delayed(Duration.zero); // StateNotifier'ın başlangıç durumunu bekle
  });

  group('TokenNotifier', () {
    test('initial state should be loaded with empty data', () {
      expect(tokenNotifier.state.status, equals(TokenStatus.loaded));
      expect(tokenNotifier.state.stats, equals({}));
      expect(tokenNotifier.state.transactions, isEmpty);
    });

    test('loadTokenData success should update state to loaded', () async {
      final mockStats = {
        'total_tokens': 1000000,
        'distributed_tokens': 750000,
        'active_users': 1234,
      };

      final mockTransactions = [
        {
          'id': '1',
          'amount': 100,
          'type': 'transfer',
          'timestamp': '2024-03-14T12:00:00Z',
        }
      ];

      when(mockRepository.getTokenStats()).thenAnswer((_) async => mockStats);
      when(mockRepository.getTokenTransactions())
          .thenAnswer((_) async => mockTransactions);

      await tokenNotifier.loadTokenData();

      expect(tokenNotifier.state.status, equals(TokenStatus.loaded));
      expect(tokenNotifier.state.stats, equals(mockStats));
      expect(tokenNotifier.state.transactions, equals(mockTransactions));
    });

    test('loadTokenData failure should update state to error', () async {
      when(mockRepository.getTokenStats())
          .thenThrow(Exception('Failed to load token stats'));

      await tokenNotifier.loadTokenData();

      expect(tokenNotifier.state.status, equals(TokenStatus.error));
      expect(tokenNotifier.state.error, contains('Failed to load token stats'));
    });

    test('refreshData should update state with new data', () async {
      final mockStats = {
        'total_tokens': 1000000,
        'distributed_tokens': 800000,
        'active_users': 1500,
      };

      final mockTransactions = [
        {
          'id': '2',
          'amount': 200,
          'type': 'reward',
          'timestamp': '2024-03-14T13:00:00Z',
        }
      ];

      when(mockRepository.getTokenStats()).thenAnswer((_) async => mockStats);
      when(mockRepository.getTokenTransactions())
          .thenAnswer((_) async => mockTransactions);

      await tokenNotifier.refreshData();

      expect(tokenNotifier.state.status, equals(TokenStatus.loaded));
      expect(tokenNotifier.state.stats, equals(mockStats));
      expect(tokenNotifier.state.transactions, equals(mockTransactions));
    });

    test('refreshData failure should update state to error', () async {
      when(mockRepository.getTokenStats())
          .thenThrow(Exception('Failed to refresh token data'));

      await tokenNotifier.refreshData();

      expect(tokenNotifier.state.status, equals(TokenStatus.error));
      expect(tokenNotifier.state.error, contains('Failed to refresh token data'));
    });
  });
} 