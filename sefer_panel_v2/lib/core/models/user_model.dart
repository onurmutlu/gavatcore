import 'package:json_annotation/json_annotation.dart';

part 'user_model.g.dart';

@JsonSerializable()
class UserModel {
  final String id;
  final String username;
  final String? firstName;
  final String? lastName;
  final String? photoUrl;
  final bool isAdmin;
  final List<String> roles;
  final DateTime lastLogin;

  UserModel({
    required this.id,
    required this.username,
    this.firstName,
    this.lastName,
    this.photoUrl,
    this.isAdmin = false,
    this.roles = const [],
    required this.lastLogin,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);
  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  String get fullName => [firstName, lastName].where((e) => e != null).join(' ');
  bool hasRole(String role) => roles.contains(role);
} 