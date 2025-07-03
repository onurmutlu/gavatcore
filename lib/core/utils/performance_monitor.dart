import 'dart:developer' as developer;
import 'package:flutter/foundation.dart';

class PerformanceMonitor {
  static final Map<String, Stopwatch> _timers = {};
  static final Map<String, int> _counters = {};
  
  static void startTimer(String key) {
    _timers[key] = Stopwatch()..start();
  }
  
  static Duration stopTimer(String key) {
    final timer = _timers[key];
    if (timer == null) {
      throw Exception('Timer $key not found');
    }
    
    timer.stop();
    final duration = timer.elapsed;
    _timers.remove(key);
    
    if (kDebugMode) {
      developer.log(
        'Timer $key completed in ${duration.inMilliseconds}ms',
        name: 'Performance',
      );
    }
    
    return duration;
  }
  
  static void incrementCounter(String key) {
    _counters[key] = (_counters[key] ?? 0) + 1;
    
    if (kDebugMode) {
      developer.log(
        'Counter $key: ${_counters[key]}',
        name: 'Performance',
      );
    }
  }
  
  static void resetCounter(String key) {
    _counters.remove(key);
  }
  
  static int getCounter(String key) {
    return _counters[key] ?? 0;
  }
  
  static void logMemoryUsage() {
    if (kDebugMode) {
      developer.log(
        'Memory usage stats',
        name: 'Performance',
        error: {
          'heapSize': '${(ProcessInfo.currentRss / 1024 / 1024).toStringAsFixed(2)}MB',
          'heapUsed': '${(ProcessInfo.currentRss / 1024 / 1024).toStringAsFixed(2)}MB',
        },
      );
    }
  }
  
  static void clearAll() {
    _timers.clear();
    _counters.clear();
  }
} 