class User {
  final String id;
  final String email;
  final String name;
  final String role;
  final String? avatar;
  final DateTime? lastLogin;
  final bool isActive;

  const User({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.avatar,
    this.lastLogin,
    this.isActive = true,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id']?.toString() ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      role: json['role'] ?? 'user',
      avatar: json['avatar'],
      lastLogin: json['last_login'] != null 
          ? DateTime.tryParse(json['last_login'])
          : null,
      isActive: json['is_active'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'role': role,
      'avatar': avatar,
      'last_login': lastLogin?.toIso8601String(),
      'is_active': isActive,
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? name,
    String? role,
    String? avatar,
    DateTime? lastLogin,
    bool? isActive,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      role: role ?? this.role,
      avatar: avatar ?? this.avatar,
      lastLogin: lastLogin ?? this.lastLogin,
      isActive: isActive ?? this.isActive,
    );
  }

  bool get isAdmin => role.toLowerCase() == 'admin';
  bool get isSuperAdmin => role.toLowerCase() == 'super_admin';

  String get displayName => name.isNotEmpty ? name : email;
  
  String get roleDisplayName {
    switch (role.toLowerCase()) {
      case 'admin':
        return '🛡️ Yönetici';
      case 'super_admin':
        return '👑 Süper Admin';
      case 'moderator':
        return '🔨 Moderatör';
      case 'user':
        return '👤 Kullanıcı';
      default:
        return '❓ $role';
    }
  }

  @override
  String toString() {
    return 'User(id: $id, email: $email, name: $name, role: $role)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 