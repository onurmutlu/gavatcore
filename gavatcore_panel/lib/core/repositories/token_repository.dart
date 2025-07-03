import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';

final tokenRepositoryProvider = Provider((ref) => TokenRepository(ApiService()));

class TokenRepository {
  final ApiService _apiService;

  TokenRepository(this._apiService);

  Future<Map<String, dynamic>> getTokenStats() async {
    try {
      return await _apiService.getTokenStats();
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getTokenTransactions() async {
    try {
      return await _apiService.getTokenTransactions();
    } catch (e) {
      rethrow;
    }
  }
} 