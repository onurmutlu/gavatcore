import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../models/bot.dart';

final botRepositoryProvider = Provider((ref) => BotRepository(ApiService()));

class BotRepository {
  final ApiService _apiService;

  BotRepository(this._apiService);

  Future<List<Bot>> getBots() async {
    try {
      final response = await _apiService.get('/api/bots');
      
      if (response['success'] == true) {
        final List<dynamic> botsData = response['bots'] ?? [];
        return botsData.map((data) => Bot.fromJson(data)).toList();
      } else {
        throw Exception('Failed to get bots: ${response['message']}');
      }
    } catch (e) {
      throw Exception('Error fetching bots: $e');
    }
  }

  Future<bool> updateBotStatus(String botId, bool isActive) async {
    try {
      final response = await _apiService.put('/api/bots/$botId/status', {
        'is_active': isActive,
      });

      return response['success'] == true;
    } catch (e) {
      throw Exception('Error updating bot status: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getBotLogs(String botId) async {
    try {
      final response = await _apiService.get('/api/bots/$botId/logs');
      
      if (response['success'] == true) {
        return List<Map<String, dynamic>>.from(response['logs'] ?? []);
      } else {
        throw Exception('Failed to get bot logs: ${response['message']}');
      }
    } catch (e) {
      throw Exception('Error fetching bot logs: $e');
    }
  }

  Future<Map<String, dynamic>> getBotStats(String botId) async {
    try {
      final response = await _apiService.get('/api/bots/$botId/stats');
      
      if (response['success'] == true) {
        return response['stats'] ?? {};
      } else {
        throw Exception('Failed to get bot stats: ${response['message']}');
      }
    } catch (e) {
      throw Exception('Error fetching bot stats: $e');
    }
  }
} 