// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'character.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Character _$CharacterFromJson(Map<String, dynamic> json) => Character(
      id: json['id'] as String,
      name: json['name'] as String,
      mode: json['mode'] as String,
      tone: json['tone'] as String,
      systemPrompt: json['systemPrompt'] as String,
      model: json['model'] as String,
      humanizer: json['humanizer'] as bool,
      lastActive: json['lastActive'] == null
          ? null
          : DateTime.parse(json['lastActive'] as String),
      stats: json['stats'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$CharacterToJson(Character instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'mode': instance.mode,
      'tone': instance.tone,
      'systemPrompt': instance.systemPrompt,
      'model': instance.model,
      'humanizer': instance.humanizer,
      'lastActive': instance.lastActive?.toIso8601String(),
      'stats': instance.stats,
    };
