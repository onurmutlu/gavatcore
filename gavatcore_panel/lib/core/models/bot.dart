class Bot {
  final String id;
  final String name;
  final String username;
  final bool isActive;
  final int messageCount;
  final int userCount;
  final DateTime? lastActivity;
  final String? status;
  final Map<String, dynamic>? metadata;

  const Bot({
    required this.id,
    required this.name,
    required this.username,
    required this.isActive,
    this.messageCount = 0,
    this.userCount = 0,
    this.lastActivity,
    this.status,
    this.metadata,
  });

  factory Bot.fromJson(Map<String, dynamic> json) {
    return Bot(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      username: json['username'] ?? '',
      isActive: json['is_active'] ?? false,
      messageCount: json['message_count'] ?? 0,
      userCount: json['user_count'] ?? 0,
      lastActivity: json['last_activity'] != null 
          ? DateTime.tryParse(json['last_activity'])
          : null,
      status: json['status'],
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'username': username,
      'is_active': isActive,
      'message_count': messageCount,
      'user_count': userCount,
      if (lastActivity != null) 'last_activity': lastActivity!.toIso8601String(),
      if (status != null) 'status': status,
      if (metadata != null) 'metadata': metadata,
    };
  }

  Bot copyWith({
    String? id,
    String? name,
    String? username,
    bool? isActive,
    int? messageCount,
    int? userCount,
    DateTime? lastActivity,
    String? status,
    Map<String, dynamic>? metadata,
  }) {
    return Bot(
      id: id ?? this.id,
      name: name ?? this.name,
      username: username ?? this.username,
      isActive: isActive ?? this.isActive,
      messageCount: messageCount ?? this.messageCount,
      userCount: userCount ?? this.userCount,
      lastActivity: lastActivity ?? this.lastActivity,
      status: status ?? this.status,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'Bot(id: $id, name: $name, username: $username, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Bot && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 