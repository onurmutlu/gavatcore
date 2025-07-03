import 'package:json_annotation/json_annotation.dart';

part 'character.g.dart';

@JsonSerializable()
class Character {
  final String id;
  final String name;
  final String mode;
  final String tone;
  final String systemPrompt;
  final String model;
  final bool humanizer;
  final DateTime? lastActive;
  final Map<String, dynamic>? stats;

  Character({
    required this.id,
    required this.name,
    required this.mode,
    required this.tone,
    required this.systemPrompt,
    required this.model,
    required this.humanizer,
    this.lastActive,
    this.stats,
  });

  factory Character.fromJson(Map<String, dynamic> json) {
    try {
      // Handle different possible field mappings from API
      final String id = json['username'] as String? ?? json['id'] as String? ?? '';
      final String name = json['display_name'] as String? ?? json['name'] as String? ?? json['username'] as String? ?? 'Unknown';
      
      // Handle persona object for system prompt
      String systemPrompt = '';
      if (json['persona'] != null && json['persona'] is Map) {
        final persona = json['persona'] as Map<String, dynamic>;
        systemPrompt = persona['gpt_prompt'] as String? ?? '';
      }
      if (systemPrompt.isEmpty) {
        systemPrompt = json['system_prompt'] as String? ?? json['systemPrompt'] as String? ?? '';
      }
      
      return Character(
        id: id,
        name: name,
        mode: json['reply_mode'] as String? ?? json['mode'] as String? ?? 'gpt',
        tone: json['tone'] as String? ?? 'neutral',
        systemPrompt: systemPrompt,
        model: json['model'] as String? ?? 'gpt-4',
        humanizer: json['humanizer'] as bool? ?? json['gpt_enhanced'] as bool? ?? false,
        lastActive: json['last_active'] != null || json['created_at'] != null
            ? DateTime.tryParse((json['last_active'] ?? json['created_at']) as String? ?? '')
            : null,
        stats: json['stats'] as Map<String, dynamic>? ?? {
          'message_count': 0,
          'is_active': json['type'] == 'bot'
        },
      );
    } catch (e) {
      print('❌ Error parsing character JSON: $e');
      print('📋 JSON data: $json');
      
      // Return a safe fallback character
      return Character(
        id: json['username'] as String? ?? json['id'] as String? ?? 'unknown',
        name: json['display_name'] as String? ?? json['name'] as String? ?? 'Unknown Character',
        mode: 'gpt',
        tone: 'neutral', 
        systemPrompt: 'Default character prompt',
        model: 'gpt-4',
        humanizer: false,
        lastActive: null,
        stats: {'message_count': 0, 'is_active': false},
      );
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'mode': mode,
      'tone': tone,
      'system_prompt': systemPrompt,
      'model': model,
      'humanizer': humanizer,
      'last_active': lastActive?.toIso8601String(),
      'stats': stats,
    };
  }

  Character copyWith({
    String? id,
    String? name,
    String? mode,
    String? tone,
    String? systemPrompt,
    String? model,
    bool? humanizer,
    DateTime? lastActive,
    Map<String, dynamic>? stats,
  }) {
    return Character(
      id: id ?? this.id,
      name: name ?? this.name,
      mode: mode ?? this.mode,
      tone: tone ?? this.tone,
      systemPrompt: systemPrompt ?? this.systemPrompt,
      model: model ?? this.model,
      humanizer: humanizer ?? this.humanizer,
      lastActive: lastActive ?? this.lastActive,
      stats: stats ?? this.stats,
    );
  }

  @override
  String toString() {
    return 'Character(id: $id, name: $name, mode: $mode, tone: $tone, model: $model)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Character && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

// Enum-like constants for dropdown options
class CharacterMode {
  static const String manual = 'manual';
  static const String gpt = 'gpt';
  static const String hybrid = 'hybrid';
  static const String manualplus = 'manualplus';

  static const List<String> values = [manual, gpt, hybrid, manualplus];

  static String getDisplayName(String mode) {
    switch (mode) {
      case manual:
        return 'Manuel';
      case gpt:
        return 'GPT';
      case hybrid:
        return 'Hibrit';
      case manualplus:
        return 'Manuel+';
      default:
        return mode;
    }
  }
}

class CharacterTone {
  static const String neutral = 'neutral';
  static const String seductive = 'seductive';
  static const String aggressive = 'aggressive';
  static const String caring = 'caring';
  static const String passive = 'passive';
  static const String ironic = 'ironic';
  static const String bubbly = 'bubbly';

  static const List<String> values = [
    neutral,
    seductive,
    aggressive,
    caring,
    passive,
    ironic,
    bubbly,
  ];

  static String getDisplayName(String tone) {
    switch (tone) {
      case neutral:
        return 'Nötr';
      case seductive:
        return 'Baştan Çıkarıcı';
      case aggressive:
        return 'Agresif';
      case caring:
        return 'Şefkatli';
      case passive:
        return 'Pasif';
      case ironic:
        return 'İronik';
      case bubbly:
        return 'Neşeli';
      default:
        return tone;
    }
  }
}

class CharacterModel {
  static const String gpt35turbo = 'gpt-3.5-turbo';
  static const String gpt4 = 'gpt-4';
  static const String gpt4o = 'gpt-4o';
  static const String claudeSonnet = 'claude-sonnet';
  static const String claudeOpus = 'claude-opus';

  static const List<String> values = [
    gpt35turbo,
    gpt4,
    gpt4o,
    claudeSonnet,
    claudeOpus,
  ];

  static String getDisplayName(String model) {
    switch (model) {
      case gpt35turbo:
        return 'GPT-3.5 Turbo';
      case gpt4:
        return 'GPT-4';
      case gpt4o:
        return 'GPT-4o';
      case claudeSonnet:
        return 'Claude Sonnet';
      case claudeOpus:
        return 'Claude Opus';
      default:
        return model;
    }
  }
} 