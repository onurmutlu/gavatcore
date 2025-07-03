import 'dart:io';

class ConnectivityUtils {
  static Future<bool> hasInternetConnection() async {
    try {
      final result = await InternetAddress.lookup('google.com');
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } on SocketException catch (_) {
      return false;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> canReachApi(String host, {int port = 80, Duration timeout = const Duration(seconds: 5)}) async {
    try {
      final socket = await Socket.connect(host, port, timeout: timeout);
      socket.destroy();
      return true;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> pingHost(String host) async {
    try {
      final result = await Process.run('ping', ['-c', '1', host]);
      return result.exitCode == 0;
    } catch (e) {
      return false;
    }
  }
} 