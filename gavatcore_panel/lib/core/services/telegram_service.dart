import 'dart:convert';
import 'dart:js' as js;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import '../models/user.dart';

class TelegramService {
  static final TelegramService _instance = TelegramService._internal();
  factory TelegramService() => _instance;
  TelegramService._internal();

  final _storage = const FlutterSecureStorage();
  User? _currentUser;
  
  final String _baseUrl = 'http://localhost:5050/api';

  // Telegram Web App API'sine erişim
  js.JsObject? get _webApp {
    final window = js.context['window'];
    if (window == null) return null;
    return window['Telegram']?['WebApp'] as js.JsObject?;
  }

  Future<void> initialize() async {
    try {
      // Telegram Web App'ten init data al
      final webApp = _webApp;
      if (webApp == null) {
        throw Exception('Telegram Web App API bulunamadı');
      }

      final initData = webApp['initData'];
      if (initData == null || initData.isEmpty) {
        throw Exception('Telegram init data bulunamadı');
      }

      await _storage.write(key: 'telegram_init_data', value: initData);
      
      // Backend'e doğrulama isteği gönder
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/verify-telegram'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'init_data': initData}),
      );

      if (response.statusCode == 200) {
        final userData = jsonDecode(response.body);
        _currentUser = User.fromJson(userData);
        await _storage.write(key: 'user_data', value: jsonEncode(userData));

        // Tema rengini ayarla
        webApp.callMethod('setBackgroundColor', ['#1A1A1A']);
        webApp.callMethod('setHeaderColor', ['#000000']);
      } else {
        throw Exception('Doğrulama başarısız: ${response.statusCode}');
      }
    } catch (e) {
      print('Telegram initialization error: $e');
      rethrow;
    }
  }

  Future<User?> getCurrentUser() async {
    if (_currentUser != null) return _currentUser;
    
    try {
      final userDataStr = await _storage.read(key: 'user_data');
      if (userDataStr != null) {
        final userData = jsonDecode(userDataStr);
        _currentUser = User.fromJson(userData);
      }
    } catch (e) {
      print('Error getting current user: $e');
    }
    
    return _currentUser;
  }

  Future<List<Map<String, dynamic>>> getAvailableBots() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/telegram/bots'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(result['bots'] ?? []);
      } else {
        throw Exception('Failed to get bots: ${response.statusCode}');
      }
    } catch (e) {
      print('Get bots error: $e');
      rethrow;
    }
  }

  Future<bool> checkExistingSession({String? botName}) async {
    try {
      final sessionKey = botName != null ? 'telegram_session_$botName' : 'telegram_session';
      final sessionData = await _storage.read(key: sessionKey);
      if (sessionData != null && botName != null) {
        final response = await http.post(
          Uri.parse('$_baseUrl/telegram/validate-session'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'session_data': sessionData,
            'bot_name': botName,
          }),
        );
        return response.statusCode == 200;
      }
      return false;
    } catch (e) {
      print('Session check error: $e');
      return false;
    }
  }

  Future<Map<String, dynamic>> sendCode(String botName) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/telegram/send-code'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'bot_name': botName}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to send code: ${response.statusCode}');
      }
    } catch (e) {
      print('Send code error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> verifyCode(
    String code,
    String phoneCodeHash,
    String sessionId,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/telegram/verify-code'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'code': code,
          'phone_code_hash': phoneCodeHash,
          'session_id': sessionId,
        }),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        
        if (result['session_data'] != null && result['bot_name'] != null) {
          await _storage.write(
            key: 'telegram_session_${result['bot_name']}', 
            value: result['session_data']
          );
        }
        
        return result;
      } else {
        throw Exception('Code verification failed: ${response.statusCode}');
      }
    } catch (e) {
      print('Verify code error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> verifyTwoFactor(String password, String sessionId) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/telegram/verify-2fa'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'password': password,
          'session_id': sessionId,
        }),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        
        if (result['session_data'] != null && result['bot_name'] != null) {
          await _storage.write(
            key: 'telegram_session_${result['bot_name']}', 
            value: result['session_data']
          );
        }
        
        if (result['user'] != null) {
          _currentUser = User.fromJson(result['user']);
          await _storage.write(key: 'user_data', value: jsonEncode(result['user']));
        }
        
        return result;
      } else {
        throw Exception('2FA verification failed: ${response.statusCode}');
      }
    } catch (e) {
      print('Verify 2FA error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> sendMessage({
    required String chatId,
    required String message,
    required String botName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/telegram/send-message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'chat_id': chatId,
          'message': message,
          'bot_name': botName,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to send message: ${response.statusCode}');
      }
    } catch (e) {
      print('Send message error: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getMessages({
    String? chatId,
    String? botName,
    int limit = 50,
  }) async {
    try {
      final queryParams = <String, String>{
        'limit': limit.toString(),
        'bot_name': botName,
      };
      if (chatId != null) queryParams['chat_id'] = chatId;

      final uri = Uri.parse('$_baseUrl/telegram/messages').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(result['messages'] ?? []);
      } else {
        throw Exception('Failed to get messages: ${response.statusCode}');
      }
    } catch (e) {
      print('Get messages error: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getChats([String? botName]) async {
    try {
      final uri = Uri.parse('$_baseUrl/telegram/chats');

      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(result['chats'] ?? []);
      } else {
        throw Exception('Failed to get chats: ${response.statusCode}');
      }
    } catch (e) {
      print('Get chats error: $e');
      rethrow;
    }
  }

  Future<void> showAlert(String message) async {
    final webApp = _webApp;
    if (webApp != null) {
      webApp.callMethod('showAlert', [message]);
    } else {
      // Fallback to browser alert
      js.context.callMethod('alert', [message]);
    }
  }

  Future<bool> showConfirm(String message) async {
    final webApp = _webApp;
    if (webApp != null) {
      final result = await webApp.callMethod('showConfirm', [message]);
      return result == true;
    } else {
      // Fallback to browser confirm
      final result = js.context.callMethod('confirm', [message]);
      return result == true;
    }
  }

  Future<void> openTelegramLink(String username) async {
    final webApp = _webApp;
    if (webApp != null) {
      webApp.callMethod('openTelegramLink', ['https://t.me/$username']);
    } else {
      js.context.callMethod('open', ['https://t.me/$username', '_blank']);
    }
  }

  Future<void> openInvoice(String url) async {
    final webApp = _webApp;
    if (webApp != null) {
      webApp.callMethod('openInvoice', [url]);
    } else {
      js.context.callMethod('open', [url, '_blank']);
    }
  }

  Future<void> logout() async {
    await _storage.deleteAll();
    _currentUser = null;
  }
} 