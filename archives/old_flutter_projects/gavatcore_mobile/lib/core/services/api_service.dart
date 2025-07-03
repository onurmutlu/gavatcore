import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../storage/storage_service.dart';
import '../utils/connectivity_utils.dart';
import '../utils/error_handler.dart';
import '../models/app_exception.dart';

// Exception sınıfları
class ApiException implements Exception {
  final int statusCode;
  final String message;
  
  ApiException(this.statusCode, this.message);
  
  @override
  String toString() => 'ApiException($statusCode): $message';
}

class NetworkException implements Exception {
  final String message;
  
  NetworkException(this.message);
  
  @override
  String toString() => 'NetworkException: $message';
}

class TimeoutException implements Exception {
  final String message;
  
  TimeoutException(this.message);
  
  @override
  String toString() => 'TimeoutException: $message';
}

class RequestCancelledException implements Exception {
  final String message;
  
  RequestCancelledException(this.message);
  
  @override
  String toString() => 'RequestCancelledException: $message';
}

// API Service Provider
final apiServiceProvider = Provider<ApiService>((ref) {
  final storage = ref.read(storageServiceProvider);
  return ApiService(storage: storage);
});

class ApiService {
  final StorageService storage;
  final String baseUrl;
  late final Map<String, String> _headers;

  ApiService({
    required this.storage,
    String? customBaseUrl,
  }) : baseUrl = customBaseUrl ?? 'http://localhost:8001' {
    _headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  Future<void> _updateAuthHeader() async {
    final token = await storage.getString('auth_token');
    if (token != null) {
      _headers['Authorization'] = 'Bearer $token';
    }
  }

  Future<Map<String, dynamic>> get(String endpoint) async {
    try {
      await _updateAuthHeader();
      
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
      ).timeout(const Duration(seconds: 30));

      return _handleResponse(response);
    } catch (e) {
      throw AppException('GET request failed: $e');
    }
  }

  Future<Map<String, dynamic>> post(String endpoint, dynamic data) async {
    try {
      await _updateAuthHeader();
      
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
        body: json.encode(data),
      ).timeout(const Duration(seconds: 30));

      return _handleResponse(response);
    } catch (e) {
      throw AppException('POST request failed: $e');
    }
  }

  Future<Map<String, dynamic>> put(String endpoint, dynamic data) async {
    try {
      await _updateAuthHeader();
      
      final response = await http.put(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
        body: json.encode(data),
      ).timeout(const Duration(seconds: 30));

      return _handleResponse(response);
    } catch (e) {
      throw AppException('PUT request failed: $e');
    }
  }

  Future<Map<String, dynamic>> delete(String endpoint) async {
    try {
      await _updateAuthHeader();
      
      final response = await http.delete(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers,
      ).timeout(const Duration(seconds: 30));

      return _handleResponse(response);
    } catch (e) {
      throw AppException('DELETE request failed: $e');
    }
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      try {
        return json.decode(response.body);
      } catch (e) {
        // If response is not JSON, wrap it
        return {
          'success': true,
          'data': response.body,
        };
      }
    } else {
      throw AppException(
        'Request failed with status ${response.statusCode}: ${response.body}',
      );
    }
  }

  // Character Management Endpoints (Real API calls)
  Future<Map<String, dynamic>> getCharacters() async {
    try {
      print('🔄 API: Getting characters from $baseUrl/characters');
      final response = await get('/characters');
      print('✅ API: Characters response: $response');
      return response;
    } catch (e) {
      print('❌ API Error: $e');
      // Fallback to mock data if API fails
      print('🔄 Falling back to mock data...');
      await Future.delayed(const Duration(milliseconds: 500));
      
      return {
        'success': true,
        'characters': [
          {
            'id': 'lara',
            'name': 'Lara',
            'mode': 'gpt',
            'tone': 'seductive',
            'system_prompt': 'Sen çok çekici ve akıllı bir kadınsın. Her zaman flörtöz ve eğlenceli davranırsın.',
            'model': 'gpt-4',
            'humanizer': true,
            'last_active': DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(),
            'stats': {'message_count': 1542, 'is_active': true}
          },
          {
            'id': 'babagavat',
            'name': 'Baba Gavat',
            'mode': 'hybrid',
            'tone': 'aggressive',
            'system_prompt': 'Sen sert, direkt konuşan ve hiçbir şeyden çekinmeyen bir adamsın.',
            'model': 'gpt-4o',
            'humanizer': false,
            'last_active': DateTime.now().subtract(const Duration(minutes: 15)).toIso8601String(),
            'stats': {'message_count': 892, 'is_active': true}
          },
          {
            'id': 'geisha',
            'name': 'Geisha',
            'mode': 'gpt',
            'tone': 'caring',
            'system_prompt': 'Sen nazik, şefkatli ve anlayışlı bir kadınsın. Herkese saygı gösterirsin.',
            'model': 'claude-sonnet',
            'humanizer': true,
            'last_active': DateTime.now().subtract(const Duration(hours: 2)).toIso8601String(),
            'stats': {'message_count': 634, 'is_active': false}
          },
          {
            'id': 'balkiz',
            'name': 'Bal Kız',
            'mode': 'manual',
            'tone': 'bubbly',
            'system_prompt': 'Sen çok neşeli, enerjik ve pozitif bir kişisin. Her zaman gülümser ve mutlu görünürsün.',
            'model': 'gpt-3.5-turbo',
            'humanizer': true,
            'last_active': DateTime.now().subtract(const Duration(hours: 1)).toIso8601String(),
            'stats': {'message_count': 423, 'is_active': true}
          },
          {
            'id': 'mystic',
            'name': 'Mystic Oracle',
            'mode': 'manualplus',
            'tone': 'ironic',
            'system_prompt': 'Sen gizemli, ironik ve derin düşüncelere sahip birisisin.',
            'model': 'claude-opus',
            'humanizer': false,
            'last_active': DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
            'stats': {'message_count': 156, 'is_active': false}
          }
        ]
      };
    }
  }

  Future<Map<String, dynamic>> getCharacterStats(String characterId) async {
    final response = await get('/characters/$characterId/stats');
    return response;
  }

  Future<Map<String, dynamic>> getAllCharacterStats() async {
    final response = await get('/characters/stats');
    return response;
  }

  Future<Map<String, dynamic>> updateCharacter(String characterId, Map<String, dynamic> data) async {
    try {
      print('🔄 API: Updating character $characterId with data: $data');
      final response = await put('/characters/$characterId', data);
      print('✅ API: Update response: $response');
      return response;
    } catch (e) {
      print('❌ API Error: $e');
      // Fallback to mock response if API fails
      print('🔄 Falling back to mock response...');
      await Future.delayed(const Duration(milliseconds: 800));
      
      return {
        'success': true,
        'message': 'Karakter başarıyla güncellendi (Mock)',
        'character': {
          'id': characterId,
          ...data,
        }
      };
    }
  }

  Future<Map<String, dynamic>> updateCharacterMode(String characterId, String mode) async {
    final response = await post('/characters/$characterId/mode', {
      'mode': mode,
    });
    return response;
  }

  Future<Map<String, dynamic>> testCharacterReply(String characterId, String message) async {
    try {
      print('🔄 API: Testing reply for $characterId with message: $message');
      final response = await post('/characters/$characterId/test', {
        'message': message,
      });
      print('✅ API: Test reply response: $response');
      return response;
    } catch (e) {
      print('❌ API Error: $e');
      // Fallback to mock reply
      final mockReplies = {
        'lara': 'Merhaba tatlım 💋 Çok ilginç bir mesaj! 😊',
        'babagavat': 'Ne demek istiyorsun? Düzgün konuş!',
        'geisha': 'Anlıyorum, sana yardım edebilirim 🌸',
        'balkiz': 'Vay be! Çok harika! 🎉✨',
        'mystic': 'İlginç bir perspektif... Derin anlamı düşünmeliyiz...'
      };
      
      return {
        'success': true,
        'reply': mockReplies[characterId] ?? 'Mock yanıt: $message',
        'character_id': characterId
      };
    }
  }

  // System & Health Endpoints
  Future<Map<String, dynamic>> getSystemStatus() async {
    final response = await get('/api/system/status');
    return response;
  }

  Future<Map<String, dynamic>> getSystemHealth() async {
    final response = await get('/api/system/health');
    return response;
  }

  Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await get('/api/admin/dashboard/stats');
    return response;
  }

  // Bot Management Endpoints
  Future<Map<String, dynamic>> startSystem() async {
    final response = await post('/api/system/start', {});
    return response;
  }

  Future<Map<String, dynamic>> stopSystem() async {
    final response = await post('/api/system/stop', {});
    return response;
  }

  Future<Map<String, dynamic>> restartBot(String username) async {
    final response = await post('/api/bot/$username/restart', {});
    return response;
  }

  // Behavioral & Analytics Endpoints
  Future<Map<String, dynamic>> getUserBehavior(String userId) async {
    final response = await get('/api/behavioral/profile/$userId');
    return response;
  }

  Future<Map<String, dynamic>> getHighRiskUsers() async {
    final response = await get('/api/behavioral/users/high-risk');
    return response;
  }

  Future<Map<String, dynamic>> getBehavioralInsights() async {
    final response = await get('/api/behavioral/insights/summary');
    return response;
  }

  // Campaign & Stats Endpoints
  Future<Map<String, dynamic>> getCampaignStats() async {
    final response = await get('/api/campaign/stats');
    return response;
  }

  Future<Map<String, dynamic>> getRecentLogs() async {
    final response = await get('/api/logs/recent');
    return response;
  }

  // Showcu Management Endpoints
  Future<Map<String, dynamic>> createShowcu(Map<String, dynamic> data) async {
    // This endpoint needs to be implemented in backend
    final response = await post('/api/showcu/create', data);
    return response;
  }

  // Character Config Management (Backend'e eklenecek)
  Future<Map<String, dynamic>> getCharacterConfig(String characterId) async {
    // Simulated response for now
    return {
      'success': true,
      'config': {
        'name': characterId,
        'system_prompt': 'Default prompt for $characterId',
        'tone': 'flirty',
        'gpt_model': 'gpt-4',
        'humanizer_enabled': true,
        'typing_speed': 20,
        'emoji_usage_rate': 0.3,
        'mistake_chance': 0.05,
      }
    };
  }

  Future<Map<String, dynamic>> updateCharacterPrompt(String characterId, String prompt) async {
    // This endpoint needs to be implemented in backend
    final response = await post('/api/characters/$characterId/update_prompt', {
      'system_prompt': prompt,
    });
    return response;
  }

  Future<Map<String, dynamic>> updateCharacterTone(String characterId, String tone) async {
    // This endpoint needs to be implemented in backend  
    final response = await post('/api/characters/$characterId/set_tone', {
      'tone': tone,
    });
    return response;
  }

  Future<Map<String, dynamic>> getTokenStats() async {
    // This endpoint needs to be implemented in backend
    return {
      'success': true,
      'total_tokens': 125000,
      'total_cost': 2.5,
      'today_tokens': 5000,
      'today_cost': 0.1,
      'by_model': {
        'gpt-4': {'tokens': 80000, 'cost': 2.0},
        'gpt-3.5-turbo': {'tokens': 45000, 'cost': 0.5},
      },
      'by_character': {
        'lara': {'tokens': 50000, 'cost': 1.0},
        'babagavat': {'tokens': 40000, 'cost': 0.8},
        'geisha': {'tokens': 35000, 'cost': 0.7},
      }
    };
  }
}

