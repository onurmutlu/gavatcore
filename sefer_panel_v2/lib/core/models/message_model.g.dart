// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MessageModel _$MessageModelFromJson(Map<String, dynamic> json) => MessageModel(
      id: json['id'] as String,
      userId: json['userId'] as String,
      botId: json['botId'] as String?,
      content: json['content'] as String,
      replyTo: json['replyTo'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
      type: $enumDecode(_$MessageTypeEnumMap, json['type']),
      isAiGenerated: json['isAiGenerated'] as bool? ?? false,
      aiRating: (json['aiRating'] as num?)?.toDouble(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$MessageModelToJson(MessageModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'botId': instance.botId,
      'content': instance.content,
      'replyTo': instance.replyTo,
      'timestamp': instance.timestamp.toIso8601String(),
      'type': _$MessageTypeEnumMap[instance.type]!,
      'isAiGenerated': instance.isAiGenerated,
      'aiRating': instance.aiRating,
      'metadata': instance.metadata,
    };

const _$MessageTypeEnumMap = {
  MessageType.text: 'text',
  MessageType.image: 'image',
  MessageType.video: 'video',
  MessageType.audio: 'audio',
  MessageType.file: 'file',
  MessageType.command: 'command',
  MessageType.system: 'system',
};
