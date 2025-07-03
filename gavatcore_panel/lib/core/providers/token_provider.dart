import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repositories/token_repository.dart';

final tokenStateProvider = StateNotifierProvider<TokenNotifier, TokenState>((ref) {
  return TokenNotifier(ref.watch(tokenRepositoryProvider));
});

class TokenNotifier extends StateNotifier<TokenState> {
  final TokenRepository _repository;

  TokenNotifier(this._repository) : super(const TokenState.initial()) {
    loadTokenData();
  }

  Future<void> loadTokenData() async {
    state = const TokenState.loading();
    try {
      final stats = await _repository.getTokenStats();
      final transactions = await _repository.getTokenTransactions();
      state = TokenState.loaded(stats, transactions);
    } catch (e) {
      state = TokenState.error(e.toString());
    }
  }

  Future<void> refreshData() async {
    try {
      final stats = await _repository.getTokenStats();
      final transactions = await _repository.getTokenTransactions();
      state = TokenState.loaded(stats, transactions);
    } catch (e) {
      state = TokenState.error(e.toString());
    }
  }
}

class TokenState {
  final TokenStatus status;
  final Map<String, dynamic>? stats;
  final List<Map<String, dynamic>>? transactions;
  final String? error;

  const TokenState._({
    required this.status,
    this.stats,
    this.transactions,
    this.error,
  });

  const TokenState.initial() : this._(status: TokenStatus.initial);

  const TokenState.loading() : this._(status: TokenStatus.loading);

  const TokenState.loaded(
    Map<String, dynamic> stats,
    List<Map<String, dynamic>> transactions,
  ) : this._(
          status: TokenStatus.loaded,
          stats: stats,
          transactions: transactions,
        );

  const TokenState.error(String error)
      : this._(status: TokenStatus.error, error: error);

  bool get isLoading => status == TokenStatus.loading;
  bool get isLoaded => status == TokenStatus.loaded;
  bool get hasError => status == TokenStatus.error;
}

enum TokenStatus {
  initial,
  loading,
  loaded,
  error,
} 