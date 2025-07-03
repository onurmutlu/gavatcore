class LogEntry {
  final String timestamp;
  final String level;
  final String message;
  final String source;
  final Map<String, dynamic>? metadata;

  const LogEntry({
    required this.timestamp,
    required this.level,
    required this.message,
    required this.source,
    this.metadata,
  });

  factory LogEntry.fromJson(Map<String, dynamic> json) {
    return LogEntry(
      timestamp: json['timestamp'] ?? '',
      level: json['level'] ?? 'INFO',
      message: json['message'] ?? '',
      source: json['source'] ?? 'system',
      metadata: json['metadata'],
    );
  }

  String get levelIcon {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return '❌';
      case 'WARNING':
        return '⚠️';
      case 'INFO':
        return 'ℹ️';
      case 'DEBUG':
        return '🐛';
      case 'SUCCESS':
        return '✅';
      default:
        return '📋';
    }
  }

  String get formattedTime {
    try {
      final dateTime = DateTime.parse(timestamp);
      return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp,
      'level': level,
      'message': message,
      'source': source,
      if (metadata != null) 'metadata': metadata,
    };
  }

  @override
  String toString() {
    return 'LogEntry(timestamp: $timestamp, level: $level, message: $message, source: $source)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is LogEntry &&
        other.timestamp == timestamp &&
        other.level == level &&
        other.message == message &&
        other.source == source;
  }

  @override
  int get hashCode {
    return timestamp.hashCode ^
        level.hashCode ^
        message.hashCode ^
        source.hashCode;
  }
} 