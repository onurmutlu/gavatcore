import 'dart:io';
import 'package:flutter/foundation.dart';

class ConnectivityUtils {
  static Future<bool> hasInternetConnection() async {
    try {
      final result = await InternetAddress.lookup('google.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (e) {
      debugPrint('Internet connection check failed: $e');
      return false;
    } catch (e) {
      debugPrint('Unexpected error during internet check: $e');
      return false;
    }
  }

  static Future<bool> isServerReachable() async {
    try {
      final result = await InternetAddress.lookup('api.gavatcore.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (e) {
      debugPrint('Server reachability check failed: $e');
      return false;
    } catch (e) {
      debugPrint('Unexpected error during server check: $e');
      return false;
    }
  }

  static Future<ConnectionStatus> checkConnection() async {
    if (!await hasInternetConnection()) {
      return ConnectionStatus.noInternet;
    }

    if (!await isServerReachable()) {
      return ConnectionStatus.serverUnreachable;
    }

    return ConnectionStatus.connected;
  }
}

enum ConnectionStatus {
  connected,
  noInternet,
  serverUnreachable;

  String get message {
    switch (this) {
      case ConnectionStatus.connected:
        return 'Bağlantı başarılı';
      case ConnectionStatus.noInternet:
        return 'İnternet bağlantısı bulunamadı. Lütfen bağlantınızı kontrol edin.';
      case ConnectionStatus.serverUnreachable:
        return 'Sunucuya ulaşılamıyor. Lütfen daha sonra tekrar deneyin.';
    }
  }
} 