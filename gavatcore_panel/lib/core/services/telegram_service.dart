import 'dart:convert';
import 'dart:js' as js;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import '../models/user_model.dart';

class TelegramService {
  static final TelegramService _instance = TelegramService._internal();
  factory TelegramService() => _instance;
  TelegramService._internal();

  final _storage = const FlutterSecureStorage();
  UserModel? _currentUser;
  
  // TODO: Backend URL'yi konfigürasyon dosyasından al
  final String _baseUrl = 'http://localhost:8000/api';

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
        _currentUser = UserModel.fromJson(userData);
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

  Future<UserModel?> getCurrentUser() async {
    if (_currentUser != null) return _currentUser;
    
    try {
      final userDataStr = await _storage.read(key: 'user_data');
      if (userDataStr != null) {
        final userData = jsonDecode(userDataStr);
        _currentUser = UserModel.fromJson(userData);
      }
    } catch (e) {
      print('Error getting current user: $e');
    }
    
    return _currentUser;
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