import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:gavatcore_mobile/core/repositories/bot_repository.dart';
import 'package:gavatcore_mobile/core/providers/bot_provider.dart';

@GenerateMocks([BotRepository])
import 'bot_provider_test.mocks.dart';

void main() {
  late BotNotifier botNotifier;
  late MockBotRepository mockRepository;

  setUp(() async {
    mockRepository = MockBotRepository();
    when(mockRepository.getBots()).thenAnswer((_) async => []);
    botNotifier = BotNotifier(mockRepository);
    await Future.delayed(Duration.zero); // StateNotifier'ın başlangıç durumunu bekle
  });

  group('BotNotifier', () {
    test('initial state should be loaded with empty list', () {
      expect(botNotifier.state.status, equals(BotStatus.loaded));
      expect(botNotifier.state.bots, isEmpty);
    });

    test('loadBots success should update state to loaded', () async {
      final mockBots = [
        {
          'id': '1',
          'name': 'Test Bot',
          'status': 'active',
          'messages': 100,
        }
      ];

      when(mockRepository.getBots()).thenAnswer((_) async => mockBots);

      await botNotifier.loadBots();

      expect(botNotifier.state.status, equals(BotStatus.loaded));
      expect(botNotifier.state.bots, equals(mockBots));
    });

    test('loadBots failure should update state to error', () async {
      when(mockRepository.getBots()).thenThrow(Exception('Failed to load bots'));

      await botNotifier.loadBots();

      expect(botNotifier.state.status, equals(BotStatus.error));
      expect(botNotifier.state.error, contains('Failed to load bots'));
    });

    test('updateBotStatus should reload bots on success', () async {
      final mockBots = [
        {
          'id': '1',
          'name': 'Test Bot',
          'status': 'active',
          'messages': 100,
        }
      ];

      when(mockRepository.updateBotStatus('1', true))
          .thenAnswer((_) async => {'status': 'success'});
      when(mockRepository.getBots()).thenAnswer((_) async => mockBots);

      await botNotifier.updateBotStatus('1', true);

      expect(botNotifier.state.status, equals(BotStatus.loaded));
      expect(botNotifier.state.bots, equals(mockBots));
    });

    test('updateBotStatus failure should update state to error', () async {
      when(mockRepository.updateBotStatus('1', true))
          .thenThrow(Exception('Failed to update bot status'));

      await botNotifier.updateBotStatus('1', true);

      expect(botNotifier.state.status, equals(BotStatus.error));
      expect(botNotifier.state.error, contains('Failed to update bot status'));
    });
  });
} 