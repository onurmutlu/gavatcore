import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:gavatcore_mobile/core/providers/bot_provider.dart';
import 'package:gavatcore_mobile/core/services/api_service.dart';
import 'package:gavatcore_mobile/core/storage/storage_service.dart';

class MockApiService extends Mock implements ApiService {}

void main() {
  late BotProvider botProvider;
  late MockApiService mockApiService;

  setUp(() {
    mockApiService = MockApiService();
    botProvider = BotProvider(mockApiService);
  });

  group('BotProvider Tests', () {
    test('fetch bots success', () async {
      final botsResponse = {
        'bots': [
          {
            'id': 1,
            'name': 'Bot 1',
            'status': 'active',
            'type': 'chat',
          },
          {
            'id': 2,
            'name': 'Bot 2',
            'status': 'inactive',
            'type': 'support',
          },
        ],
      };

      when(mockApiService.get('/bots'))
          .thenAnswer((_) async => botsResponse);

      await botProvider.fetchBots();

      verify(mockApiService.get('/bots')).called(1);
      expect(botProvider.bots.length, 2);
      expect(botProvider.bots[0]['name'], 'Bot 1');
      expect(botProvider.bots[1]['status'], 'inactive');
    });

    test('fetch bots failure', () async {
      when(mockApiService.get('/bots'))
          .thenThrow(ApiException(500, 'Server error'));

      expect(
        () => botProvider.fetchBots(),
        throwsA(isA<ApiException>()),
      );

      expect(botProvider.bots, isEmpty);
    });

    test('create bot success', () async {
      final newBot = {
        'id': 3,
        'name': 'New Bot',
        'status': 'active',
        'type': 'chat',
      };

      when(mockApiService.post(
        '/bots',
        data: anyNamed('data'),
      )).thenAnswer((_) async => newBot);

      await botProvider.createBot('New Bot', 'chat');

      verify(mockApiService.post(
        '/bots',
        data: {
          'name': 'New Bot',
          'type': 'chat',
        },
      )).called(1);

      expect(botProvider.bots.length, 1);
      expect(botProvider.bots.last, newBot);
    });

    test('update bot success', () async {
      final updatedBot = {
        'id': 1,
        'name': 'Updated Bot',
        'status': 'inactive',
        'type': 'support',
      };

      when(mockApiService.put(
        '/bots/1',
        data: anyNamed('data'),
      )).thenAnswer((_) async => updatedBot);

      await botProvider.updateBot(1, 'Updated Bot', 'support', 'inactive');

      verify(mockApiService.put(
        '/bots/1',
        data: {
          'name': 'Updated Bot',
          'type': 'support',
          'status': 'inactive',
        },
      )).called(1);
    });

    test('delete bot success', () async {
      when(mockApiService.delete('/bots/1'))
          .thenAnswer((_) async => {'success': true});

      await botProvider.deleteBot(1);

      verify(mockApiService.delete('/bots/1')).called(1);
    });

    test('start bot success', () async {
      when(mockApiService.post('/bots/1/start'))
          .thenAnswer((_) async => {'success': true});

      await botProvider.startBot(1);

      verify(mockApiService.post('/bots/1/start')).called(1);
    });

    test('stop bot success', () async {
      when(mockApiService.post('/bots/1/stop'))
          .thenAnswer((_) async => {'success': true});

      await botProvider.stopBot(1);

      verify(mockApiService.post('/bots/1/stop')).called(1);
    });

    test('get bot stats success', () async {
      final statsResponse = {
        'messages_sent': 100,
        'messages_received': 80,
        'active_users': 50,
        'uptime': '24h',
      };

      when(mockApiService.get('/bots/1/stats'))
          .thenAnswer((_) async => statsResponse);

      final stats = await botProvider.getBotStats(1);

      verify(mockApiService.get('/bots/1/stats')).called(1);
      expect(stats['messages_sent'], 100);
      expect(stats['active_users'], 50);
    });
  });
} 