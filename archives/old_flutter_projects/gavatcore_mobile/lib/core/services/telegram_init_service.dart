import 'dart:convert';
import 'package:crypto/crypto.dart';

class TelegramInitService {
  static Map<String, dynamic> decodeAndVerifyInitData(String initDataString) {
    if (initDataString.isEmpty) {
      throw Exception('Init data is empty');
    }

    final params = Uri.splitQueryString(initDataString);
    final hash = params['hash'];
    if (hash == null) {
      throw Exception('Hash not found in init data');
    }

    // Remove hash from params
    params.remove('hash');

    // Sort params alphabetically
    final sortedKeys = params.keys.toList()..sort();
    final dataCheckString = sortedKeys
        .map((key) => '$key=${params[key]}')
        .join('\n');

    // TODO: Add bot token validation
    const botToken = 'YOUR_BOT_TOKEN';
    final secretKey = Hmac(sha256, utf8.encode('WebAppData'));
    final dataCheckHash = secretKey.convert(utf8.encode(dataCheckString)).toString();

    if (hash != dataCheckHash) {
      throw Exception('Hash mismatch');
    }

    return params;
  }
} 