import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repositories/bot_repository.dart';
import '../models/bot.dart';

final botStateProvider = StateNotifierProvider<BotNotifier, BotState>((ref) {
  return BotNotifier(ref.watch(botRepositoryProvider));
});

class BotNotifier extends StateNotifier<BotState> {
  final BotRepository _repository;

  BotNotifier(this._repository) : super(const BotState.initial()) {
    loadBots();
  }

  Future<void> loadBots() async {
    state = const BotState.loading();
    try {
      final bots = await _repository.getBots();
      state = BotState.loaded(bots);
    } catch (e) {
      state = BotState.error(e.toString());
    }
  }

  Future<void> updateBotStatus(String botId, bool isActive) async {
    try {
      await _repository.updateBotStatus(botId, isActive);
      await loadBots(); // Reload bots after update
    } catch (e) {
      state = BotState.error(e.toString());
    }
  }
}

class BotState {
  final BotStatus status;
  final List<Bot>? bots;
  final String? error;

  const BotState._({
    required this.status,
    this.bots,
    this.error,
  });

  const BotState.initial() : this._(status: BotStatus.initial);

  const BotState.loading() : this._(status: BotStatus.loading);

  const BotState.loaded(List<Bot> bots)
      : this._(status: BotStatus.loaded, bots: bots);

  const BotState.error(String error)
      : this._(status: BotStatus.error, error: error);

  bool get isLoading => status == BotStatus.loading;
  bool get isLoaded => status == BotStatus.loaded;
  bool get hasError => status == BotStatus.error;
}

enum BotStatus {
  initial,
  loading,
  loaded,
  error,
} 