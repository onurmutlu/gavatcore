class BotStatus {
  final String id;
  final String name;
  final String description;
  final String status; // "running", "stopped", "error"
  final int? pid;
  final double uptime; // in minutes
  final int messagesSent;
  final double memoryUsage; // MB
  final double cpuUsage; // percentage
  final DateTime? lastRestart;
  final int restartCount;
  final String performer;
  final String telegramHandle;
  final bool autoRestart;

  BotStatus({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    this.pid,
    required this.uptime,
    required this.messagesSent,
    required this.memoryUsage,
    required this.cpuUsage,
    this.lastRestart,
    required this.restartCount,
    required this.performer,
    required this.telegramHandle,
    required this.autoRestart,
  });

  factory BotStatus.fromJson(Map<String, dynamic> json) {
    return BotStatus(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      status: json['status'] ?? 'unknown',
      pid: json['pid'],
      uptime: (json['uptime'] ?? 0).toDouble(),
      messagesSent: json['messages_sent'] ?? 0,
      memoryUsage: (json['memory_usage'] ?? 0).toDouble(),
      cpuUsage: (json['cpu_usage'] ?? 0).toDouble(),
      lastRestart: json['last_restart'] != null 
          ? DateTime.parse(json['last_restart']) 
          : null,
      restartCount: json['restart_count'] ?? 0,
      performer: json['performer'] ?? '',
      telegramHandle: json['telegram_handle'] ?? '',
      autoRestart: json['auto_restart'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'status': status,
      'pid': pid,
      'uptime': uptime,
      'messages_sent': messagesSent,
      'memory_usage': memoryUsage,
      'cpu_usage': cpuUsage,
      'last_restart': lastRestart?.toIso8601String(),
      'restart_count': restartCount,
      'performer': performer,
      'telegram_handle': telegramHandle,
      'auto_restart': autoRestart,
    };
  }

  bool get isRunning => status == 'running';
  bool get isStopped => status == 'stopped';
  bool get hasError => status == 'error';

  String get statusIcon {
    switch (status) {
      case 'running':
        return '🟢';
      case 'stopped':
        return '🟡';
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  }

  String get formattedUptime {
    if (uptime < 60) {
      return '${uptime.toInt()}dk';
    } else if (uptime < 1440) {
      return '${(uptime / 60).toStringAsFixed(1)}sa';
    } else {
      return '${(uptime / 1440).toStringAsFixed(1)}g';
    }
  }
} 