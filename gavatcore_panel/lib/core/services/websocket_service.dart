import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _messageController =
      StreamController<Map<String, dynamic>>.broadcast();
  final String baseUrl;
  bool _isConnected = false;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;

  WebSocketService({this.baseUrl = 'ws://localhost:8000/ws'});

  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;
  bool get isConnected => _isConnected;

  Future<void> connect() async {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(baseUrl));
      _isConnected = true;
      _reconnectAttempts = 0;

      _channel!.stream.listen(
        (data) {
          try {
            final message = json.decode(data);
            _messageController.add(message);
          } catch (e) {
            print('WebSocket: Error parsing message: $e');
          }
        },
        onDone: () {
          _isConnected = false;
          _attemptReconnect();
        },
        onError: (error) {
          print('WebSocket error: $error');
          _isConnected = false;
          _attemptReconnect();
        },
      );

      print('WebSocket connected to $baseUrl');
    } catch (e) {
      print('WebSocket connection failed: $e');
      _isConnected = false;
      _attemptReconnect();
    }
  }

  void _attemptReconnect() {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      print('WebSocket: Max reconnect attempts reached');
      return;
    }

    _reconnectAttempts++;
    final delay = Duration(seconds: _reconnectAttempts * 2);
    
    print('WebSocket: Attempting reconnect in ${delay.inSeconds} seconds (attempt $_reconnectAttempts)');
    
    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  void sendMessage(Map<String, dynamic> message) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(json.encode(message));
    }
  }

  void subscribeToChannel(String channel) {
    sendMessage({
      'type': 'subscribe',
      'channel': channel,
    });
  }

  void unsubscribeFromChannel(String channel) {
    sendMessage({
      'type': 'unsubscribe',
      'channel': channel,
    });
  }

  void dispose() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _messageController.close();
  }
}

final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.dispose());
  return service;
}); 