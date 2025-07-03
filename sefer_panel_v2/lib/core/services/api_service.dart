import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/message_model.dart';
import '../models/stats_model.dart';
import '../models/bot_model.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final _storage = const FlutterSecureStorage();
  final String _baseUrl = 'http://localhost:8000/api';

  Future<String?> _getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  Future<Map<String, String>> _getHeaders() async {
    final token = await _getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Bot Yönetimi
  Future<List<BotModel>> getBots() async {
    final response = await http.get(
      Uri.parse('$_baseUrl/bots'),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => BotModel.fromJson(json)).toList();
    } else {
      throw Exception('Botlar alınamadı: ${response.statusCode}');
    }
  }

  Future<BotModel> updateBot(String botId, Map<String, dynamic> updates) async {
    final response = await http.patch(
      Uri.parse('$_baseUrl/bots/$botId'),
      headers: await _getHeaders(),
      body: jsonEncode(updates),
    );

    if (response.statusCode == 200) {
      return BotModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Bot güncellenemedi: ${response.statusCode}');
    }
  }

  // Mesaj Yönetimi
  Future<List<MessageModel>> getMessages({
    String? userId,
    String? botId,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
    int? offset,
  }) async {
    final queryParams = {
      if (userId != null) 'userId': userId,
      if (botId != null) 'botId': botId,
      if (startDate != null) 'startDate': startDate.toIso8601String(),
      if (endDate != null) 'endDate': endDate.toIso8601String(),
      if (limit != null) 'limit': limit.toString(),
      if (offset != null) 'offset': offset.toString(),
    };

    final response = await http.get(
      Uri.parse('$_baseUrl/messages').replace(queryParameters: queryParams),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => MessageModel.fromJson(json)).toList();
    } else {
      throw Exception('Mesajlar alınamadı: ${response.statusCode}');
    }
  }

  // İstatistikler
  Future<StatsModel> getStats({
    DateTime? startDate,
    DateTime? endDate,
    String? botId,
  }) async {
    final queryParams = {
      if (startDate != null) 'startDate': startDate.toIso8601String(),
      if (endDate != null) 'endDate': endDate.toIso8601String(),
      if (botId != null) 'botId': botId,
    };

    final response = await http.get(
      Uri.parse('$_baseUrl/stats').replace(queryParameters: queryParams),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      return StatsModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('İstatistikler alınamadı: ${response.statusCode}');
    }
  }

  // AI Derecelendirme
  Future<Map<String, dynamic>> getAiRatings({
    String? botId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final queryParams = {
      if (botId != null) 'botId': botId,
      if (startDate != null) 'startDate': startDate.toIso8601String(),
      if (endDate != null) 'endDate': endDate.toIso8601String(),
    };

    final response = await http.get(
      Uri.parse('$_baseUrl/ai-ratings').replace(queryParameters: queryParams),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('AI derecelendirmeleri alınamadı: ${response.statusCode}');
    }
  }

  // Gelir Takibi
  Future<Map<String, dynamic>> getRevenue({
    DateTime? startDate,
    DateTime? endDate,
    String? source,
  }) async {
    final queryParams = {
      if (startDate != null) 'startDate': startDate.toIso8601String(),
      if (endDate != null) 'endDate': endDate.toIso8601String(),
      if (source != null) 'source': source,
    };

    final response = await http.get(
      Uri.parse('$_baseUrl/revenue').replace(queryParameters: queryParams),
      headers: await _getHeaders(),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Gelir bilgileri alınamadı: ${response.statusCode}');
    }
  }
} 