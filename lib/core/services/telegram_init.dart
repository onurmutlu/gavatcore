import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class TelegramInitService {
  static const String BOT_TOKEN = String.fromEnvironment('BOT_TOKEN');
  
  /// Telegram WebApp initData'yı decode eder ve doğrular
  static Future<Map<String, dynamic>> decodeAndVerifyInitData(String initData) async {
    try {
      // URI decode
      final decoded = Uri.decodeComponent(initData);
      
      // Key-value pairs'leri ayır
      final pairs = decoded.split('&');
      final params = <String, String>{};
      
      String dataCheckString = '';
      for (final pair in pairs) {
        final parts = pair.split('=');
        if (parts.length == 2) {
          final key = parts[0];
          final value = parts[1];
          
          if (key != 'hash') {
            // Hash hesaplaması için data string'i oluştur
            if (dataCheckString.isNotEmpty) {
              dataCheckString += '\n';
            }
            dataCheckString += '$key=$value';
          }
          
          params[key] = value;
        }
      }
      
      // Hash doğrulaması
      final secretKey = utf8.encode(BOT_TOKEN);
      final hmac = Hmac(sha256, secretKey);
      final calculatedHash = hmac.convert(utf8.encode(dataCheckString)).toString();
      
      if (calculatedHash != params['hash']) {
        throw Exception('Invalid hash');
      }
      
      // User data'yı parse et
      final userData = jsonDecode(params['user'] ?? '{}');
      
      return {
        'user': userData,
        'auth_date': int.parse(params['auth_date'] ?? '0'),
        'is_valid': true,
      };
    } catch (e) {
      if (kDebugMode) {
        print('Telegram initData decode hatası: $e');
      }
      return {
        'is_valid': false,
        'error': e.toString(),
      };
    }
  }
  
  /// Telegram WebApp'in hazır olup olmadığını kontrol eder
  static bool get isWebAppReady {
    if (kIsWeb) {
      // js interop ile Telegram.WebApp kontrolü
      return true; // TODO: JS interop implement edilecek
    }
    return false;
  }
  
  /// Telegram tema renklerini Flutter temasına uyarlar
  static Map<String, Color> getTelegramThemeColors() {
    if (!isWebAppReady) return {
      'background': Colors.black,
      'text': Colors.white,
      'hint': Colors.grey,
      'link': Colors.blue,
      'button': Colors.blue,
      'buttonText': Colors.white,
    };
    
    return {
      'background': const Color(0xFF000000), // TODO: JS interop ile gerçek renkleri al
      'text': const Color(0xFFFFFFFF),
      'hint': const Color(0xFF8E8E93),
      'link': const Color(0xFF0A84FF),
      'button': const Color(0xFF007AFF),
      'buttonText': const Color(0xFFFFFFFF),
    };
  }
} 