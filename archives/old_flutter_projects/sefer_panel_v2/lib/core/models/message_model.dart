import 'package:json_annotation/json_annotation.dart';

part 'message_model.g.dart';

@JsonSerializable()
class MessageModel {
  final String id;
  final String userId;
  final String? botId;
  final String content;
  final String? replyTo;
  final DateTime timestamp;
  final MessageType type;
  final bool isAiGenerated;
  final double? aiRating;
  final Map<String, dynamic>? metadata;

  MessageModel({
    required this.id,
    required this.userId,
    this.botId,
    required this.content,
    this.replyTo,
    required this.timestamp,
    required this.type,
    this.isAiGenerated = false,
    this.aiRating,
    this.metadata,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) => _$MessageModelFromJson(json);
  Map<String, dynamic> toJson() => _$MessageModelToJson(this);
}

enum MessageType {
  text,
  image,
  video,
  audio,
  file,
  command,
  system,
} 